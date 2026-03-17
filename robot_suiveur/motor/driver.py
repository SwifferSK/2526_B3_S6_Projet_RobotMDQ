from __future__ import annotations

import time
import threading

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
        if GPIO is None:  
            raise ImportError("Pas de GPIO")

        self.step_pin = int(step_pin)
        self.dir_pin = int(dir_pin)
        self.steps_per_rev = int(steps_per_rev)
        self.microstep = int(microstep)
        self.default_direction = direction
        
        self._thread = None
        self._running = False
        self.speed_rpm = 0.0
        self.delay = 0.0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

        self.set_speed(speed_rpm)

    def set_speed(self, speed_rpm: float) -> None:
        if speed_rpm < 0:
            dir_val = DIRECTION_BACKWARD if self.default_direction == DIRECTION_FORWARD else DIRECTION_FORWARD
            self.set_direction(dir_val)
        elif speed_rpm > 0:
            self.set_direction(self.default_direction)

        self.speed_rpm = abs(speed_rpm)
        if self.speed_rpm == 0:
            self.freq = 0.0
            self.delay = 0.0
            return

        total_steps_per_rev = self.steps_per_rev * self.microstep
        self.freq = (self.speed_rpm * total_steps_per_rev) / 60.0
        self.delay = 1.0 / (2.0 * self.freq) if self.freq > 0 else 0.0

    def set_direction(self, direction: int) -> None:
        if direction not in (DIRECTION_FORWARD, DIRECTION_BACKWARD):
            raise ValueError(f"La direction doit être {DIRECTION_FORWARD} ou {DIRECTION_BACKWARD}")
        self.direction = direction
        GPIO.output(self.dir_pin, self.direction)

    def step(self, steps: int = 1) -> None:
        """Fait un nombre précis de pas (bloquant)."""
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

    def start_continuous(self) -> None:
        """Start the background thread for continuous stepping."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._step_loop, daemon=True)
        self._thread.start()

    def stop_continuous(self) -> None:
        """Stop the background thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def _step_loop(self) -> None:
        """Background loop generating step pulses continuously."""
        while self._running:
            delay = self.delay
            if delay > 0 and self.speed_rpm > 0:
                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(delay)
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(delay)
            else:
                time.sleep(0.01)

    def info(self) -> None:
        print(
            f"[TMC2225] Step pin: {self.step_pin} | Dir pin: {self.dir_pin} | "
            f"Speed: {self.speed_rpm:.2f} RPM | Dir: {self.direction}"
        )

    def cleanup(self) -> None:
        self.stop_continuous()
        if GPIO is not None:
            GPIO.cleanup((self.step_pin, self.dir_pin))
