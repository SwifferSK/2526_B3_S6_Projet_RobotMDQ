from __future__ import annotations

from .driver import TMC2225
from .config import (
    DEFAULT_SPEED_RPM,
    DEFAULT_STEPS_PER_REV,
    DEFAULT_MICROSTEP,
    DIRECTION_FORWARD,
    DIRECTION_BACKWARD,
)


class DualMotorController:
    def __init__(self, motor1_params: dict, motor2_params: dict):
        self.motor1 = TMC2225(
            step_pin=motor1_params["step"],
            dir_pin=motor1_params["dir"],
            speed_rpm=motor1_params.get("speed_rpm", DEFAULT_SPEED_RPM),
            direction=motor1_params.get("direction", DIRECTION_FORWARD),
            steps_per_rev=motor1_params.get("steps_per_rev", DEFAULT_STEPS_PER_REV),
            microstep=motor1_params.get("microstep", DEFAULT_MICROSTEP),
        )

        self.motor2 = TMC2225(
            step_pin=motor2_params["step"],
            dir_pin=motor2_params["dir"],
            speed_rpm=motor2_params.get("speed_rpm", DEFAULT_SPEED_RPM),
            direction=motor2_params.get("direction", DIRECTION_BACKWARD),
            steps_per_rev=motor2_params.get("steps_per_rev", DEFAULT_STEPS_PER_REV),
            microstep=motor2_params.get("microstep", DEFAULT_MICROSTEP),
        )

    def rotate_both(self, angle1: float, angle2: float) -> None:
        """Rotate motors with independent angles."""
        self.motor1.rotate(angle1)
        self.motor2.rotate(angle2)

    def rotate_sync(self, angle: float, inverse: bool = False) -> None:
        """Rotate both motors by the same angle.

        If inverse=True, motor2 temporarily uses opposite direction.
        """
        if inverse:
            opposite_direction = (DIRECTION_FORWARD + DIRECTION_BACKWARD) - self.motor2.direction
            self.motor2.set_direction(opposite_direction)

        self.motor1.rotate(angle)
        self.motor2.rotate(angle)

        if inverse:
            # restore original direction
            opposite_direction = (DIRECTION_FORWARD + DIRECTION_BACKWARD) - self.motor2.direction
            self.motor2.set_direction(opposite_direction)

    def stop_all(self) -> None:
        self.motor1.cleanup()
        self.motor2.cleanup()

    def info(self) -> None:
        print("\n=== INFOS MOTEURS ===")
        self.motor1.info()
        self.motor2.info()
        print("=====================\n")
