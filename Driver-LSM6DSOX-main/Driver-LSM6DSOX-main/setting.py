# I2C address of the LSM6DSOX (0x6A if SA0 pin is low, otherwise 0x6B)
LSM6DSOX_ADDR = 0x6A

# I2C bus (1 for Raspberry Pi)
i2cbus = 1

# Number of bytes to read for gyro and accel
bytes = 6
#frequency settings for accelerometer
FQ_POWER_DOWN = 0x00   # gyroscope disabled
FQ12_5HZ      = 0x10
FQ26HZ        = 0x20
FQ52HZ        = 0x30
FQ104HZ       = 0x40
FQ208HZ       = 0x50
FQ416HZ       = 0x60
FQ833HZ       = 0x70
FQ1660HZ      = 0x80  # 1.66 kHz
FQ3330HZ      = 0x90  # 3.33 kHz
FQ6660HZ      = 0xA0  # 6.66 kHz

#Accelerometer full-scale selection
FS_2G  = 0x00
FS_16G = 0x04
FS_4G  = 0x08
FS_8G  = 0x0C

#Gyroscope Frequencies
FQ_G_POWER_DOWN = 0x00  # gyroscope disabled
FQ_G_12_5HZ     = 0x10
FQ_G_26HZ       = 0x20
FQ_G_52HZ       = 0x30
FQ_G_104HZ      = 0x40
FQ_G_208HZ      = 0x50
FQ_G_416HZ      = 0x60
FQ_G_833HZ      = 0x70
FQ_G_1660HZ     = 0x80
FQ_G_3330HZ     = 0x90
FQ_G_6660HZ     = 0xA0

# Gyroscope Full Scale
FS_G_125DPS   = 0x02
FS_G_245DPS   = 0x00
FS_G_500DPS   = 0x04
FS_G_1000DPS  = 0x08
FS_G_2000DPS  = 0x0C

# CTRL3_C Register Bits
CTRL3_C_BOOT      = 0x80  # Bit 7: Reboot memory content
CTRL3_C_BDU       = 0x40  # Bit 6: Block Data Update
CTRL3_C_H_LACTIVE = 0x20  # Bit 5: Interrupt active level (0: high, 1: low)
CTRL3_C_PP_OD     = 0x10  # Bit 4: Push-pull / Open-drain selection for INT1/INT2
CTRL3_C_SIM       = 0x08  # Bit 3: SPI Serial Interface Mode selection (0: 4-wire, 1: 3-wire)
CTRL3_C_IF_INC    = 0x04  # Bit 2: Register address auto-increment enable (1: enabled)
# Bit 1 is reserved and should be kept at 0
CTRL3_C_SW_RESET  = 0x01  # Bit 0: Software Reset

# Time delay for each data read (in seconds)
time_delay = 1

# SCALE FACTOR
# - For other ranges (±4g, ±8g, ±16g or ±500/1000/2000 dps), the scale factor changes (see LSM6DSOX datasheet)
#   Accelerometer scale factors (LSB/g):
SF_2G = 0.000061
SF_4G = 0.000122
SF_8G = 0.000244
SF_16G = 0.000488

#   Gyroscope scale factors (LSB/dps):
SF_200DPS = 0.00875
SF_500DPS = 0.0175
SF_1000DPS = 0.035
SF_2000DPS = 0.07

# =====================
# Additional notes:
#
# - To get acceleration in g, multiply the raw value by 0.000061 (for ±2g)
#   Example: x_g = x_a * 0.000061
#
# - To get angular velocity in dps (degrees/second), multiply the raw value by 0.00875 (for ±250 dps)
#   Example: x_dps = x_g * 0.00875
#
# - Raw values range from -32768 to +32767 (int16)
#   This corresponds to the full sensor range.
#
# - Raw values are in LSB (Least Significant Bit). To get a physical unit (g or dps), you must apply the scale factor.
#
# - Two's complement allows correct interpretation of negative values sent by the sensor.
#
# - To read the gyroscope, you must read from register OUTX_L_G (0x22)
#   (already done in the read_gyro() function)
#
# - For more details, see the official LSM6DSOX datasheet:
#   https://www.st.com/resource/en/datasheet/lsm6dsox.pdf