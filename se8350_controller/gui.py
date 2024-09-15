import tkinter as tk
from tkinter import ttk
import asyncio
import os

from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.primitivedata import Real, Enumerated
from bacpypes.object import get_datatype
from bacpypes.apdu import ReadPropertyRequest, WritePropertyRequest
from bacpypes.pdu import Address
from bacpypes.iocb import IOCB

class BACnetClientApp(BIPSimpleApplication):
    def __init__(self, device, address):
        BIPSimpleApplication.__init__(self, device, address)

    async def read_property(self, address, obj_type, obj_inst, prop_id):
        request = ReadPropertyRequest(
            objectIdentifier=(obj_type, obj_inst),
            propertyIdentifier=prop_id,
        )
        request.pduDestination = Address(address)
        iocb = IOCB(request)
        await self.request_io(iocb)
        
        if iocb.ioResponse:
            return iocb.ioResponse.propertyValue.cast_out(get_datatype(obj_type, prop_id))
        else:
            raise Exception("Error reading property")

    async def write_property(self, address, obj_type, obj_inst, prop_id, value, priority=None):
        request = WritePropertyRequest(
            objectIdentifier=(obj_type, obj_inst),
            propertyIdentifier=prop_id,
            propertyValue=value,
        )
        request.pduDestination = Address(address)
        iocb = IOCB(request)
        await self.request_io(iocb)
        
        if iocb.ioError:
            raise Exception("Error writing property")

class GUI:
    def __init__(self, master, bacnet_app, loop):
        self.master = master
        self.bacnet_app = bacnet_app
        self.loop = loop
        self.master.title("SE8350 Room Controller")

        self.create_widgets()

    def create_widgets(self):
        # Room Temperature
        ttk.Label(self.master, text="Room Temperature:").grid(row=0, column=0, sticky="w")
        self.room_temp_var = tk.StringVar()
        ttk.Entry(self.master, textvariable=self.room_temp_var).grid(row=0, column=1)
        ttk.Button(self.master, text="Update", command=lambda: self.update_value("analogValue", 1, "presentValue", self.room_temp_var.get())).grid(row=0, column=2)

        # Setpoint
        ttk.Label(self.master, text="Setpoint:").grid(row=1, column=0, sticky="w")
        self.setpoint_var = tk.StringVar()
        ttk.Entry(self.master, textvariable=self.setpoint_var).grid(row=1, column=1)
        ttk.Button(self.master, text="Update", command=lambda: self.update_value("analogValue", 2, "presentValue", self.setpoint_var.get())).grid(row=1, column=2)

        # Humidity
        ttk.Label(self.master, text="Humidity:").grid(row=2, column=0, sticky="w")
        self.humidity_var = tk.StringVar()
        ttk.Entry(self.master, textvariable=self.humidity_var).grid(row=2, column=1)
        ttk.Button(self.master, text="Update", command=lambda: self.update_value("analogValue", 3, "presentValue", self.humidity_var.get())).grid(row=2, column=2)

        # Occupancy Status
        ttk.Label(self.master, text="Occupancy Status:").grid(row=3, column=0, sticky="w")
        self.occupancy_var = tk.StringVar()
        ttk.Combobox(self.master, textvariable=self.occupancy_var, values=["inactive", "active"]).grid(row=3, column=1)
        ttk.Button(self.master, text="Update", command=lambda: self.update_value("binaryValue", 1, "presentValue", self.occupancy_var.get())).grid(row=3, column=2)

        # Fan Status
        ttk.Label(self.master, text="Fan Status:").grid(row=4, column=0, sticky="w")
        self.fan_status_var = tk.StringVar()
        ttk.Combobox(self.master, textvariable=self.fan_status_var, values=["Off", "Low", "High"]).grid(row=4, column=1)
        ttk.Button(self.master, text="Update", command=lambda: self.update_value("multiStateValue", 1, "presentValue", self.fan_status_var.get())).grid(row=4, column=2)

        # HVAC Mode
        ttk.Label(self.master, text="HVAC Mode:").grid(row=5, column=0, sticky="w")
        self.hvac_mode_var = tk.StringVar()
        ttk.Combobox(self.master, textvariable=self.hvac_mode_var, values=["Off", "Auto", "Heat", "Cool", "EmergencyHeat"]).grid(row=5, column=1)
        ttk.Button(self.master, text="Update", command=lambda: self.update_value("multiStateValue", 2, "presentValue", self.hvac_mode_var.get())).grid(row=5, column=2)

        # Refresh button
        ttk.Button(self.master, text="Refresh All", command=self.refresh_all).grid(row=6, column=1)

    def refresh_all(self):
        asyncio.run_coroutine_threadsafe(self._refresh_all(), self.loop)

    async def _refresh_all(self):
        self.room_temp_var.set(await self.bacnet_app.read_property("127.0.0.1:47808", "analogValue", 1, "presentValue"))
        self.setpoint_var.set(await self.bacnet_app.read_property("127.0.0.1:47808", "analogValue", 2, "presentValue"))
        self.humidity_var.set(await self.bacnet_app.read_property("127.0.0.1:47808", "analogValue", 3, "presentValue"))
        self.occupancy_var.set(await self.bacnet_app.read_property("127.0.0.1:47808", "binaryValue", 1, "presentValue"))
        self.fan_status_var.set(await self.bacnet_app.read_property("127.0.0.1:47808", "multiStateValue", 1, "presentValue"))
        self.hvac_mode_var.set(await self.bacnet_app.read_property("127.0.0.1:47808", "multiStateValue", 2, "presentValue"))

    def update_value(self, obj_type, obj_inst, prop_id, value):
        if obj_type in ["analogValue", "analogInput", "analogOutput"]:
            value = Real(float(value))
        elif obj_type in ["multiStateValue", "multiStateInput", "multiStateOutput"]:
            value = Enumerated(int(value))
        else:
            value = value

        asyncio.run_coroutine_threadsafe(
            self.bacnet_app.write_property("127.0.0.1:47808", obj_type, obj_inst, prop_id, value),
            self.loop
        )

async def run_gui(bacnet_app):
    root = tk.Tk()
    gui = GUI(root, bacnet_app, asyncio.get_running_loop())

    while True:
        root.update()
        await asyncio.sleep(0.1)

async def main():
    # Create a minimal BACnet device object for the client
    device_object = LocalDeviceObject(
        objectName="BACnet Client",
        objectIdentifier=3056,  # You can choose any number that doesn't conflict with the server
        vendorIdentifier=555,
    )

    # Use a different port for the client
    client_address = os.environ.get('BACPYPES_IP', '0.0.0.0')
    client_port = int(os.environ.get('BACPYPES_PORT', 47809))  # Use a different port, e.g., 47809

    # Create the BACnet client application
    bacnet_app = BACnetClientApp(device_object, f"{client_address}:{client_port}")

    print(f"BACnet client running on {client_address}:{client_port}")

    # Run the GUI
    await run_gui(bacnet_app)

if __name__ == "__main__":
    asyncio.run(main())