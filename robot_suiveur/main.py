
from __future__ import annotations

import time

from sensors.MCP3208 import MCP3208
from sensors.line_detector import detect_line
from motor.controller import DualMotorController
from motor.config import (
    MOTOR1_STEP_PIN,
    MOTOR1_DIR_PIN,
    MOTOR1_DIRECTION,
    MOTOR2_STEP_PIN,
    MOTOR2_DIR_PIN,
    MOTOR2_DIRECTION,
)


THRESHOLD = 1.5    
LOOP_DELAY = 0.0    


FORWARD_ANGLE = 5.0
TURN_ANGLE = 3.0
SEARCH_ANGLE = 2.0

BASE_SPEED = 10.0
TURN_SPEED_REDUCTION = 0.5


def main() -> None:
    adc = MCP3208(vref=3.3)

    motors = DualMotorController(
        motor1_params={
            "step": MOTOR1_STEP_PIN,
            "dir": MOTOR1_DIR_PIN,
            "direction": MOTOR1_DIRECTION,
        },
        motor2_params={
            "step": MOTOR2_STEP_PIN,
            "dir": MOTOR2_DIR_PIN,
            "direction": MOTOR2_DIRECTION,
        },
    )

    try:
        print("Starting line follower (Ctrl+C to stop)...")
        motors.info()
        
        
        motors.set_speeds(0, 0)
        motors.start_continuous()

        while True:
            
            pos = detect_line(adc, threshold=THRESHOLD, verbose=True)

          
            if pos == "center":
               
                motors.set_speeds(BASE_SPEED, BASE_SPEED)
            elif pos == "left":
               
                motors.set_speeds(BASE_SPEED * TURN_SPEED_REDUCTION, BASE_SPEED)
            elif pos == "right":
                
                motors.set_speeds(BASE_SPEED, BASE_SPEED * TURN_SPEED_REDUCTION)
            else:
        
                motors.set_speeds(BASE_SPEED * 0.5, -BASE_SPEED * 0.5)

            if LOOP_DELAY > 0:
                time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        try:
            adc.close()
        except Exception:
            pass
        try:
            motors.stop_all()
        except Exception:
            pass


if __name__ == "__main__":
    main()
