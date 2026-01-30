import smbus2
import time
from setting import *

# =====================
# LSM6DSOX  Driver for Raspberry Pi
# =====================
# This script reads acceleration (X, Y, Z) and gyroscope (X, Y, Z) values from the LSM6DSOX sensor
# connected to the standard I2C pins of the Raspberry Pi (SDA: GPIO 2, SCL: GPIO 3).
#
# The sensor communicates via the I2C bus. We use the smbus2 library here.
#
# The values read are raw (signed 16-bit integers). To get acceleration in g or angular velocity in dps,
# you must apply a scale factor (see notes at the end).

# Important LSM6DSOX registers
CTRL1_XL = 0x10   # Accelerometer configuration (ODR, range, etc.)
CTRL2_G = 0x11        # Gyroscope configuration (ODR, range, etc.)
CTRL3_C = 0x12        # General configuration (BDU, auto-increment...)
OUTX_L_G = 0x22       # Start of gyroscope data registers (6 bytes)
OUTX_L_XL = 0x28      # Start of accelerometer data registers (6 bytes)

class drv_lsm6dsow:
    def __init__(self, bus=i2cbus , adresse=LSM6DSOX_ADDR):
        # Open the I2C bus (bus=1 for Raspberry Pi)
        self.bus = smbus2.SMBus(bus)
        self.adresse = adresse
        self.init_lsm6dsox()

    def init_lsm6dsox(self):
        # Initialize the sensor with desired settings (104 Hz, ±2g for accel, 104 Hz, ±245 dps for gyro):
        self.bus.write_byte_data(self.adresse, CTRL1_XL, FQ104HZ | FS_2G)
        self.bus.write_byte_data(self.adresse, CTRL2_G, FQ_G_104HZ | FS_G_245DPS)
        # - Enable BDU (Block Data Update) and auto-increment
        self.bus.write_byte_data(self.adresse, CTRL3_C, CTRL3_C_BDU | CTRL3_C_IF_INC)
        time.sleep(0.1)  # Small delay for settings to take effect

    def read_accel(self):
        # Read 6 bytes from OUTX_L_XL: X_L, X_H, Y_L, Y_H, Z_L, Z_H
        data = self.bus.read_i2c_block_data(self.adresse, OUTX_L_XL, bytes)
        # Combine bytes and convert to signed integer (two's complement)
        x = self._twos_complement(data[1] << 8 | data[0], 16)
        y = self._twos_complement(data[3] << 8 | data[2], 16)
        z = self._twos_complement(data[5] << 8 | data[4], 16)
        return x, y, z

    def read_gyro(self):
        # Read 6 bytes from OUTX_L_G: X_L, X_H, Y_L, Y_H, Z_L, Z_H
        data = self.bus.read_i2c_block_data(self.adresse, OUTX_L_G, bytes)
        # Combine bytes and convert to signed integer (two's complement)
        x = self._twos_complement(data[1] << 8 | data[0], 16)
        y = self._twos_complement(data[3] << 8 | data[2], 16)
        z = self._twos_complement(data[5] << 8 | data[4], 16)
        return x, y, z

    def _twos_complement(self, val, bits):
        # Convert an unsigned integer to signed (two's complement)
        # Example: 0xFFFE (65534) on 16 bits => -2
        if val & (1 << (bits - 1)):
            val -= 1 << bits
        return val

