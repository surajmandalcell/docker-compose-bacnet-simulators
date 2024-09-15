import os

from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import AnalogValueObject, BinaryValueObject, MultiStateValueObject
from bacpypes.basetypes import EngineeringUnits
from bacpypes.core import run

# BACnet device configuration
device_id = int(os.environ.get("DEVICE_ID", 1))
object_name = os.environ.get("OBJECT_NAME", "SE8350_Room_Controller")
vendor_id = int(os.environ.get("VENDOR_ID", 65530))  # Schneider Electric's vendor ID

# Create BACnet objects for SE8350 controller
room_temp = AnalogValueObject(
    objectIdentifier=("analogValue", 1),
    objectName="RoomTemperature",
    presentValue=22.0,
    units=EngineeringUnits("degreesCelsius"),
)

setpoint = AnalogValueObject(
    objectIdentifier=("analogValue", 2),
    objectName="Setpoint",
    presentValue=21.0,
    units=EngineeringUnits("degreesCelsius"),
)

humidity = AnalogValueObject(
    objectIdentifier=("analogValue", 3),
    objectName="Humidity",
    presentValue=50.0,
    units=EngineeringUnits("percentRelativeHumidity"),
)

occupancy = BinaryValueObject(
    objectIdentifier=("binaryValue", 1),
    objectName="OccupancyStatus",
    presentValue="inactive",
)

fan_status = MultiStateValueObject(
    objectIdentifier=("multiStateValue", 1),
    objectName="FanStatus",
    numberOfStates=3,
    stateText=["Off", "Low", "High"],
    presentValue=1,
)

hvac_mode = MultiStateValueObject(
    objectIdentifier=("multiStateValue", 2),
    objectName="HVACMode",
    numberOfStates=5,
    stateText=["Off", "Auto", "Heat", "Cool", "EmergencyHeat"],
    presentValue=2,
)

# Create a BACnet device object
device_object = LocalDeviceObject(
    objectName=object_name,
    objectIdentifier=device_id,
    vendorIdentifier=vendor_id,
    maxApduLengthAccepted=1024,
    segmentationSupported="segmentedBoth",
    maxSegmentsAccepted=1024,
)

# Create and initialize the BACnet/IP application
app = BIPSimpleApplication(device_object, "0.0.0.0")

# Add objects to the application
app.add_object(room_temp)
app.add_object(setpoint)
app.add_object(humidity)
app.add_object(occupancy)
app.add_object(fan_status)
app.add_object(hvac_mode)

if __name__ == "__main__":
    print("SE8350 Room Controller simulation running. Press Ctrl+C to exit.")
    run()