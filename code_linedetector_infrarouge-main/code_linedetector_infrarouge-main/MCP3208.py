import spidev  # Library for SPI communication

BIT_START = 4
BIT_CONV_SINGLE = 2

class MCP3208:
    def __init__(self, spi_bus=0, spi_device=0, clock_speed=1000000, vref=3.3):
        # Initialize SPI communication with the MCP3208 ADC
        self.spi = spidev.SpiDev()               # Create an SPI device object
        self.spi.open(spi_bus, spi_device)       # Open SPI communication (bus, device)
        self.spi.max_speed_hz = clock_speed      # Set SPI clock speed (Hz)
        self.vref = vref                         # Store the reference voltage (V)

    def read_channel(self, channel):
        # Read the raw 12-bit value from one of the 8 ADC channels (0–7)
        if not 0 <= channel <= 7:                # Validate channel number
            raise ValueError("Invalid channel (must be between 0 and 7).")

        # Build the command to send to the MCP3208
        # 1st byte: start bit (0b00000110) + top channel bits
        # 2nd byte: remaining channel bits shifted + zero padding
        # 3rd byte: dummy byte (0)
        command = [BIT_START | BIT_CONV_SINGLE | (channel >> 2), (channel & 3) << 6, 0]

        # Send command and receive response (3 bytes)
        result = self.spi.xfer2(command)

        # Convert the 12-bit ADC result from the response bytes
        value = ((result[1] & 15) << 8) | result[2]
        return value

    def read_voltage(self, channel):
        # Read the ADC value and convert it to a voltage
        value = self.read_channel(channel)
        return (value / 4095.0) * self.vref      # Convert 12-bit ADC value to voltage (0–Vref)

    def read_all_channels(self):
        # Read voltage values from all 8 channels (0–7)
        return [self.read_voltage(ch) for ch in range(8)]

    def close(self):
        # Close the SPI connection properly
        self.spi.close()
