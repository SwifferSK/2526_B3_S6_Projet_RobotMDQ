from MCP3208 import MCP3208
import time

THRESHOLD = 1.5  

def detect_line(IFR, threshold=THRESHOLD):
    """
    Reads the 8 sensors from the MCP3208 through the 'adc' object
    and displays the detected line position.
    Returns a string indicating the detected position.
    """

    # Sensor readings
    left_sensor = IFR.read_voltage(0)
    left_sensor1 = IFR.read_voltage(1)
    left_sensor2 = IFR.read_voltage(2)
    center_sensor1 = IFR.read_voltage(3)
    center_sensor = IFR.read_voltage(4)
    right_sensor = IFR.read_voltage(5)
    right1_sensor = IFR.read_voltage(6)
    right2_sensor = IFR.read_voltage(7)

    # Display sensor voltages for monitoring
    print(
        f"L:{left_sensor:.2f}V | L1:{left_sensor1:.2f}V | L2:{left_sensor2:.2f}V | "
        f"C:{center_sensor:.2f}V | C1:{center_sensor1:.2f}V | "
        f"R:{right_sensor:.2f}V | R1:{right1_sensor:.2f}V | R2:{right2_sensor:.2f}V",
        end=" --> "
    )

    # Simple line detection logic
    if left_sensor < threshold or left_sensor1 < threshold or left_sensor2 < threshold:
        position = "Line on the left"
    elif center_sensor < threshold or center_sensor1 < threshold:
        position = "Line in the center"
    elif right_sensor < threshold or right1_sensor < threshold or right2_sensor < threshold:
        position = "Line on the right"
    else:
        position = "No line detected"

    print(position)
    time.sleep(0.2)
    return position
