from motor.driver import TMC2225
import time
from .config import (DEFAULT_SPEED_RPM, DEFAULT_STEPS_PER_REV, DEFAULT_MICROSTEP,
                     DIRECTION_FORWARD, DIRECTION_BACKWARD)

class DualMotorController:
    
    
    def __init__(self, motor1_params, motor2_params):
      

        self.motor1 = TMC2225(
            step_pin=motor1_params["step"],
            dir_pin=motor1_params["dir"],
            speed_rpm=motor1_params.get("speed_rpm", DEFAULT_SPEED_RPM),
            direction=motor1_params.get("direction", DIRECTION_FORWARD),
            steps_per_rev=motor1_params.get("steps_per_rev", DEFAULT_STEPS_PER_REV),
            microstep=motor1_params.get("microstep", DEFAULT_MICROSTEP)
        )

        self.motor2 = TMC2225(
            step_pin=motor2_params["step"],
            dir_pin=motor2_params["dir"],
            speed_rpm=motor2_params.get("speed_rpm", DEFAULT_SPEED_RPM),
            direction=motor2_params.get("direction", DIRECTION_BACKWARD), # 0 par défaut
            steps_per_rev=motor2_params.get("steps_per_rev", DEFAULT_STEPS_PER_REV),
            microstep=motor2_params.get("microstep", DEFAULT_MICROSTEP)
        )

    def rotate_both(self, angle1, angle2):
   

 
    def rotate_sync(self, angle, inverse=False):
        """
        Fait tourner les deux moteurs ensemble du même angle.
        Si inverse=True, le deuxième tourne en sens inverse.
        """
        print(f"Rotation synchrone {angle}° (inverse={inverse})")
        if inverse:
            # Calcule la direction opposée (ex: 1+0 - 1 = 0; 1+0 - 0 = 1)
            opposite_direction = (DIRECTION_FORWARD + DIRECTION_BACKWARD) - self.motor2.direction
            self.motor2.set_direction(opposite_direction)

        self.motor1.rotate(angle)
        self.motor2.rotate(angle)
        
        if inverse:
            # Remet la direction d'origine
            original_direction = (DIRECTION_FORWARD + DIRECTION_BACKWARD) - self.motor2.direction
            self.motor2.set_direction(original_direction)

    def stop_all(self):
        """Nettoie les deux moteurs."""
        self.motor1.cleanup()
        self.motor2.cleanup()

    def info(self):
        """Affiche les infos des deux moteurs."""
        print("\n=== INFOS MOTEURS ===")
        self.motor1.info()
        self.motor2.info()
        print("=====================\n")
