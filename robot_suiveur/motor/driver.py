from __future__ import annotations

import time

try:
    import RPi.GPIO as GPIO  # type: ignore
except ImportError:  # pragma: no cover
    GPIO = None

from .config import (
    DEFAULT_SPEED_RPM,
    DEFAULT_STEPS_PER_REV,
    DEFAULT_MICROSTEP,
    DEGREES_PER_CIRCLE,
    DIRECTION_FORWARD,
    DIRECTION_BACKWARD,
)


class TMC2225:
    """Very simple STEP/DIR stepper driver helper.

    This toggles STEP with a computed delay based on RPM + steps_per_rev + microstep.
    """

    def __init__(
        self,
        step_pin: int,
        dir_pin: int,
        speed_rpm: float = DEFAULT_SPEED_RPM,
        direction: int = DIRECTION_FORWARD,
        steps_per_rev: int = DEFAULT_STEPS_PER_REV,
        microstep: int = DEFAULT_MICROSTEP,
    ):
        if GPIO is None:  # pragma: no cover
            raise ImportError("RPi.GPIO is required on Raspberry Pi.")

        self.step_pin = int(step_pin)
        self.dir_pin = int(dir_pin)
        self.steps_per_rev = int(steps_per_rev)
        self.microstep = int(microstep)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

        self.set_speed(speed_rpm)
        self.set_direction(direction)

    def set_speed(self, speed_rpm: float) -> None:
        if speed_rpm <= 0:
            raise ValueError("La vitesse (RPM) doit être positive")

        self.speed_rpm = float(speed_rpm)
        total_steps_per_rev = self.steps_per_rev * self.microstep
        self.freq = (self.speed_rpm * total_steps_per_rev) / 60.0
        self.delay = 0.0 if self.freq == 0 else 1.0 / (2.0 * self.freq)

    def set_direction(self, direction: int) -> None:
        if direction not in (DIRECTION_FORWARD, DIRECTION_BACKWARD):
            raise ValueError(f"La direction doit être {DIRECTION_FORWARD} ou {DIRECTION_BACKWARD}")
        self.direction = direction
        GPIO.output(self.dir_pin, self.direction)

    def step(self, steps: int = 1) -> None:
        for _ in range(int(steps)):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.delay)

    def rotate(self, angle_deg: float) -> None:
        """Rotate by an angle in degrees.

        If angle_deg is negative, direction is temporarily inverted.
        """
        angle = float(angle_deg)
        if angle == 0:
            return

        restore_direction = None
        if angle < 0:
            angle = abs(angle)
            restore_direction = self.direction
            opposite_direction = (DIRECTION_FORWARD + DIRECTION_BACKWARD) - self.direction
            self.set_direction(opposite_direction)

        steps = int((angle / DEGREES_PER_CIRCLE) * (self.steps_per_rev * self.microstep))
        self.step(steps)

        if restore_direction is not None:
            self.set_direction(restore_direction)

    def info(self) -> None:
        print(
            f"[TMC2225] Step pin: {self.step_pin} | Dir pin: {self.dir_pin} | "
            f"Speed: {self.speed_rpm:.2f} RPM | Dir: {self.direction}"
        )

    def cleanup(self) -> None:
        GPIO.cleanup((self.step_pin, self.dir_pin))
