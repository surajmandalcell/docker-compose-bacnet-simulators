docker build -t bacnet-emulator .

docker rm -f bacnet-emulator

docker run --name bacnet-emulator --network bacnet-net --ip 192.168.3.100 bacnet-emulator