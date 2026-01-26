from drv_lsm6dsow import *
from setting import *
import math
if __name__ == "__main__":
    # Instantiate the driver (I2C bus 1)
    driver = drv_lsm6dsow(bus=1)
    print("Reading acceleration and gyroscope values :")
    print("Press Ctrl+C to stop.")
    while True:
        x_a, y_a, z_a = driver.read_accel()
        x_g, y_g, z_g = driver.read_gyro()
        #print(f"Accel X: {x_a}, Y: {y_a}, Z: {z_a} | Gyro X: {x_g}, Y: {y_g}, Z: {z_g}")
        angle_x = math.degrees(math.atan2(y_a * SF_2G,z_a * SF_2G))
        angle_y = math.degrees(math.atan2(x_a * SF_2G, z_a * SF_2G))
        print(f"Accel X: {(x_a * SF_2G):.2f} g, Y: {(y_a * SF_2G):.2f} g, Z: {(z_a * SF_2G):.2f} g | Gyro X: {(x_g * SF_200DPS):.2f} dps, Y: {(y_g * SF_200DPS):.2f} dps, Z: {(z_g * SF_200DPS):.2f} dps")
        print(f"Angle X: {angle_x:.2f}°, Angle Y: {angle_y:.2f}°")
        time.sleep(time_delay)
