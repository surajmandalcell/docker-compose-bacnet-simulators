import asyncio
import random
import signal
import sys
from bacpypes.core import run, deferred, enable_sleeping
from bacpypes.local.device import LocalDeviceObject
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogInputObject, BinaryInputObject, MultiStateValueObject
from bacpypes.primitivedata import Enumerated
from bacpypes.constructeddata import ArrayOf
from bacpypes.basetypes import EngineeringUnits

class CASBACnetStackServer(BIPSimpleApplication):
    def __init__(self, device, address):
        BIPSimpleApplication.__init__(self, device, address)
        self.create_objects()
        self.running = True

    def create_objects(self):
        ai0 = AnalogInputObject(
            objectIdentifier=('analogInput', 0),
            objectName='ANALOG INPUT 0',
            presentValue=0.0,
            units=EngineeringUnits.enumerations['percent'],
        )
        self.add_object(ai0)

        bi33 = BinaryInputObject(
            objectIdentifier=('binaryInput', 33),
            objectName='green',
            presentValue='inactive',
            description="This is the green binary_input description"
        )
        self.add_object(bi33)

        mv333 = MultiStateValueObject(
            objectIdentifier=('multiStateValue', 333),
            objectName='blue',
            presentValue=1,
            numberOfStates=3,
            stateText=ArrayOf(Enumerated)(['one', 'two', 'three']),
            description="This is the blue multi_state_value description"
        )
        self.add_object(mv333)

    def update_values(self):
        ai0 = self.get_object_id(('analogInput', 0))
        ai0.presentValue = round(random.uniform(0, 100), 2)

        bi33 = self.get_object_id(('binaryInput', 33))
        bi33.presentValue = 'active' if random.random() > 0.5 else 'inactive'

        mv333 = self.get_object_id(('multiStateValue', 333))
        mv333.presentValue = random.randint(1, 3)

async def run_bacnet_server(server):
    while server.running:
        server.update_values()
        await asyncio.sleep(5)

def bacnet_task(server):
    deferred(server.startup)
    run()
    
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

async def main():
    enable_sleeping()
    
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    device = LocalDeviceObject(
        objectName="CAS BACnet Stack Server",
        objectIdentifier=389002,
        maxApduLengthAccepted=1476,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=389,
        vendorName="Chipkin Automation Systems",
        modelName="CAS BACnet stack",
        firmwareRevision="v1",
        applicationSoftwareVersion="v1",
        description="CAS BACnet Stack server example",
    )

    server = CASBACnetStackServer(device, "0.0.0.0")

    bacnet_server_task = asyncio.create_task(run_bacnet_server(server))
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, bacnet_task, server)

    try:
        await bacnet_server_task
    except asyncio.CancelledError:
        server.running = False

if __name__ == "__main__":
    asyncio.run(main())