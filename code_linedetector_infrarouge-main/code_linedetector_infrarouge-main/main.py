from MCP3208 import MCP3208        # Import the MCP3208 ADC class
from detectionline import detect_line  # Import the line detection function
import time                         # Used for timing delays

# === Configuration constants ===
THRESHOLD = 1.5  # Voltage threshold for line detection (adjust according to your sensor setup)
DELAY = 0.05     # Delay (in seconds) between two sensor readings

def main():
    """
    Main program:
    - Initializes the MCP3208 ADC
    - Continuously reads sensor values
    - Detects the line position using the detectionline module
    - Stops cleanly when the user presses Ctrl+C
    """
    IFR = MCP3208(vref=3.3)  # Create an ADC object with a 3.3V reference voltage

    try:
        print("Starting line following (Press Ctrl+C to stop)...")

        # Main loop: read sensors continuously
        while True:
            position = detect_line(IFR, threshold=THRESHOLD)  # Detect the line position
            time.sleep(DELAY)  # Wait a short time before the next reading

    except KeyboardInterrupt:
        # Handles manual interruption (Ctrl+C)
        IFR.close()  # Close the SPI connection safely
        print("\nProgram stopped.")

    except Exception as e:
        # Handles any other unexpected errors
        IFR.close()
        print(f"Error detected: {e}")

# Entry point: only runs when this file is executed directly
if __name__ == "__main__":
    main()
