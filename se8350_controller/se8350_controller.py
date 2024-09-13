import os
import random
import time
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import AnalogValueObject, BinaryValueObject, MultiStateValueObject
from bacpypes.primitivedata import Real
from bacpypes.basetypes import EngineeringUnits
from bacpypes.core import run, deferred

# BACnet device configuration
device_id = int(os.environ.get("DEVICE_ID", 1))
object_name = os.environ.get("OBJECT_NAME", "SE8350_Room_Controller")
vendor_id = int(os.environ.get("VENDOR_ID", 10))  # Schneider Electric's vendor ID

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


def get_float_value(obj):
    """Helper function to get float value from BACnet object."""
    present_value = obj.presentValue
    
    if isinstance(present_value, Real):
        return present_value
    else:
        return float(present_value)


def update_values():
    """Simulate changes in the controller's values."""
    while True:
        # Update room temperature
        new_temp = get_float_value(room_temp) + random.uniform(-0.5, 0.5)
        room_temp.presentValue = Real(max(10, min(35, new_temp)))

        # Update humidity
        new_humidity = get_float_value(humidity) + random.uniform(-2, 2)
        humidity.presentValue = Real(max(20, min(80, new_humidity)))

        # Occasionally change occupancy
        if random.random() < 0.1:
            occupancy.presentValue = (
                "active" if occupancy.presentValue == "inactive" else "inactive"
            )

        # Adjust fan status based on temperature
        if get_float_value(room_temp) > get_float_value(setpoint) + 1:
            fan_status.presentValue = 3  # High
        elif get_float_value(room_temp) < get_float_value(setpoint) - 1:
            fan_status.presentValue = 2  # Low
        else:
            fan_status.presentValue = 1  # Off

        print(
            f"Room Temp: {get_float_value(room_temp):.1f}°C, "
            f"Setpoint: {get_float_value(setpoint):.1f}°C, "
            f"Humidity: {get_float_value(humidity):.1f}%, "
            f"Occupancy: {occupancy.presentValue}, "
            f"Fan: {fan_status.stateText[fan_status.presentValue - 1]}, "
            f"Mode: {hvac_mode.stateText[hvac_mode.presentValue - 1]}"
        )

        time.sleep(5)


if __name__ == "__main__":
    # Start the value update process
    deferred(update_values)

    print("SE8350 Room Controller simulation running. Press Ctrl+C to exit.")
    run()
