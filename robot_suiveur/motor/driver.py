from __future__ import annotations

import time
import math

try:
    import pigpio
except ImportError:
    pigpio = None

from .config import (
    DEFAULT_SPEED_RPM,
    DEFAULT_STEPS_PER_REV,
    DEFAULT_MICROSTEP,
    DEGREES_PER_CIRCLE,
    DIRECTION_FORWARD,
    DIRECTION_BACKWARD,
)

class TMC2225:
    """TMC2225 driver using hardware PWM with pigpio for perfect zero-jitter stepping."""
    
    pi = None # Class-level pigpio connection

    def __init__(
        self,
        step_pin: int,
        dir_pin: int,
        speed_rpm: float = DEFAULT_SPEED_RPM,
        direction: int = DIRECTION_FORWARD,
        steps_per_rev: int = DEFAULT_STEPS_PER_REV,
        microstep: int = DEFAULT_MICROSTEP,
    ):
        if pigpio is None:
            raise ImportError("La librairie pigpio n'est pas installée. Installez-la avec 'pip install pigpio'.")
            
        if TMC2225.pi is None:
            TMC2225.pi = pigpio.pi()
            if not TMC2225.pi.connected:
                raise RuntimeError("pigpiod n'est pas lancé! Lancez 'sudo pigpiod' dans le terminal.")

        self.step_pin = int(step_pin)
        self.dir_pin = int(dir_pin)
        self.steps_per_rev = int(steps_per_rev)
        self.microstep = int(microstep)
        self.default_direction = direction
        
        self.speed_rpm = 0.0
        self.direction = direction
        self._continuous_running = False

        TMC2225.pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        TMC2225.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        
        self.set_speed(speed_rpm)

    def set_speed(self, speed_rpm: float) -> None:
        """Modifie la vitesse en temps réel via PWM matériel (très fluide)."""
        if speed_rpm < 0:
            dir_val = DIRECTION_BACKWARD if self.default_direction == DIRECTION_FORWARD else DIRECTION_FORWARD
            self.set_direction(dir_val)
        elif speed_rpm > 0:
            self.set_direction(self.default_direction)

        self.speed_rpm = abs(speed_rpm)
        total_steps_per_rev = self.steps_per_rev * self.microstep
        self.freq = int((self.speed_rpm * total_steps_per_rev) / 60.0)

        if self._continuous_running:
            if self.freq > 0:
                try:
                    # 500000/1M = 50% duty cycle, fréquence precise en Hz.
                    TMC2225.pi.hardware_PWM(self.step_pin, self.freq, 500000)
                except pigpio.error:
                    # Fallback sur le DMA PWM classique si la pin ne supporte pas Hardware PWM
                    TMC2225.pi.set_PWM_frequency(self.step_pin, self.freq)
                    TMC2225.pi.set_PWM_dutycycle(self.step_pin, 128)
            else:
                try:
                    TMC2225.pi.hardware_PWM(self.step_pin, 0, 0)
                except pigpio.error:
                    TMC2225.pi.set_PWM_dutycycle(self.step_pin, 0)

    def set_direction(self, direction: int) -> None:
        if direction not in (DIRECTION_FORWARD, DIRECTION_BACKWARD):
            raise ValueError(f"Direction {direction} invalide.")
        if self.direction != direction:
            self.direction = direction
            TMC2225.pi.write(self.dir_pin, self.direction)

    def step(self, steps: int = 1) -> None:
        """Fait des pas de manière bloquante (sans utiliser le PWM continu)."""
        if self.freq == 0:
            return
        delay = 1.0 / self.freq
        for _ in range(int(steps)):
            TMC2225.pi.write(self.step_pin, 1)
            time.sleep(delay / 2.0)
            TMC2225.pi.write(self.step_pin, 0)
            time.sleep(delay / 2.0)

    def rotate(self, angle_deg: float) -> None:
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
        """Démarre le PWM continu (0 lag CPU)."""
        self._continuous_running = True
        self.set_speed(self.speed_rpm) # applique le PWM

    def stop_continuous(self) -> None:
        """Stoppe le PWM."""
        self._continuous_running = False
        self.set_speed(0.0)

    def info(self) -> None:
        print(
            f"[TMC2225 pigpio] Step: {self.step_pin} | Dir: {self.dir_pin} | "
            f"Speed: {self.speed_rpm:.2f} RPM | Freq: {self.freq} Hz"
        )

    def cleanup(self) -> None:
        self.stop_continuous()
        if TMC2225.pi is not None and TMC2225.pi.connected:
            TMC2225.pi.write(self.dir_pin, 0)
            TMC2225.pi.write(self.step_pin, 0)
