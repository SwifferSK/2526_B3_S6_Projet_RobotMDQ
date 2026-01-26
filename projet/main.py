from motor.driver import TMC2225
import time

from motor.config import (MOTOR1_STEP_PIN, MOTOR1_DIR_PIN, MOTOR1_SPEED_RPM, MOTOR1_DIRECTION,
                          MOTOR2_STEP_PIN, MOTOR2_DIR_PIN, MOTOR2_SPEED_RPM, MOTOR2_DIRECTION)

if __name__ == "__main__":
    
    # Paramètres du test
    TEST_ANGLE_MOTOR1 = 5000 
    TEST_ANGLE_MOTOR2 = 180 
    WAIT_DURATION = 1       

    # Initialisation des moteurs à partir de la configuration
    motor1 = TMC2225(step_pin=MOTOR1_STEP_PIN,
                      dir_pin=MOTOR1_DIR_PIN,
                      speed_rpm=MOTOR1_SPEED_RPM,
                      direction=MOTOR1_DIRECTION)
    
    motor2 = TMC2225(step_pin=MOTOR2_STEP_PIN,
                      dir_pin=MOTOR2_DIR_PIN,
                      speed_rpm=MOTOR2_SPEED_RPM,
                      direction=MOTOR2_DIRECTION)

    motor1.info()
    motor2.info()

    # Exécution du test avec les variables
    motor1.rotate(TEST_ANGLE_MOTOR1)
    motor2.rotate(TEST_ANGLE_MOTOR2)

    time.sleep(WAIT_DURATION)

    motor1.cleanup()
    motor2.cleanup()
#from motor.controller import DualMotorController ---si on veut utiliser les moteurs de façon synchronisés
#from motor.controller import DualMotorController

#if __name__ == "__main__":
 #   config_m1 = {"step": 23, "dir": 24, "freq": 500, "direction": 1}
  #  config_m2 = {"step": 17, "dir": 27, "freq": 300, "direction": 0}
#
 #   controller = DualMotorController(config_m1, config_m2)
  #  controller.info()

   # controller.stop_all()
