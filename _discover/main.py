from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from urllib.parse import unquote
import uvicorn
import netifaces
import ipaddress
import BAC0
import socket
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = FastAPI()
app.mount("/public", StaticFiles(directory="public"), name="public")

class NetworkScanner:
    def __init__(self):
        self.bacnet = None
        # Disable BAC0 for now since we can't initialize it properly
        # We'll still scan for devices on port 47808
        BAC0.log_level('silence')

    def get_network_interfaces(self):
        interfaces = []
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):
                        netmask = addr['netmask']
                        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                        interfaces.append({
                            'interface': iface,
                            'ip': ip,
                            'network': str(network),
                            'netmask': netmask
                        })
        return interfaces

    def scan_ip(self, ip: str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((str(ip), 47808))
            sock.close()
            
            if result == 0:
                return {'ip': str(ip), 'bacnet_available': True, 'devices': [{'device_id': 'unknown', 'properties': 'Port 47808 open'}]}
            return {'ip': str(ip), 'bacnet_available': False, 'devices': []}
        except Exception as e:
            return {'ip': str(ip), 'bacnet_available': False, 'error': str(e)}

    def scan_network(self, network: str):
        try:
            from urllib.parse import unquote
            network = unquote(network)
            net = ipaddress.IPv4Network(network)
            results = []
            
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(self.scan_ip, str(ip)) for ip in net.hosts()]
                for future in futures:
                    result = future.result()
                    if result['bacnet_available']:
                        results.append(result)
            
            return results
        except Exception as e:
            print(f"Error scanning network: {e}")
            return {'error': str(e)}

scanner = NetworkScanner()

@app.get("/")
async def root():
    return RedirectResponse(url="/public/index.html")

@app.get("/api/networks")
async def get_networks():
    try:
        return JSONResponse(scanner.get_network_interfaces())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scan/{network:path}")
async def scan_network(network: str):
    try:
        print(f"Scanning network {network}")
        # Properly decode the URL-encoded network string
        decoded_network = unquote(network)
        results = scanner.scan_network(decoded_network)
        return JSONResponse(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)