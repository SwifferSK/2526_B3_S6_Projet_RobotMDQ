import RPi.GPIO as GPIO
import time
from .config import (DEFAULT_SPEED_RPM, DEFAULT_STEPS_PER_REV, DEFAULT_MICROSTEP,
                     DEGREES_PER_CIRCLE, DIRECTION_FORWARD, DIRECTION_BACKWARD)

class TMC2225:
    

    def __init__(self, step_pin, dir_pin, 
                 speed_rpm=DEFAULT_SPEED_RPM, 
                 direction=DIRECTION_FORWARD, 
                 steps_per_rev=DEFAULT_STEPS_PER_REV, 
                 microstep=DEFAULT_MICROSTEP):
        
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.steps_per_rev = steps_per_rev
        self.microstep = microstep

        GPIO.setmode(GPIO.BCM) #
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

        self.set_speed(speed_rpm)
        self.set_direction(direction)

    def set_speed(self, speed_rpm):
        """Définit la vitesse du moteur en RPM et calcule la fréquence (Hz)"""
        if speed_rpm <= 0:
            raise ValueError("La vitesse (RPM) doit être positive")
        
        self.speed_rpm = speed_rpm
        total_steps_per_rev = self.steps_per_rev * self.microstep
        # Calcule la fréquence (Hz) requise pour la fonction step()
        self.freq = (self.speed_rpm * total_steps_per_rev) / 60
        
        if self.freq == 0:
            self.delay = 0
        else:
            self.delay = 1 / (2 * self.freq)

    def set_direction(self, direction):
        """Définir la direction du moteur"""
        if direction not in (DIRECTION_FORWARD, DIRECTION_BACKWARD):
            raise ValueError(f"La direction doit être {DIRECTION_FORWARD} ou {DIRECTION_BACKWARD}")
        self.direction = direction
        GPIO.output(self.dir_pin, self.direction)

    def step(self, steps=1):
        """Effectuer un nombre de pas donné"""
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.delay)


    def rotate(self, angle):
        """Faire tourner le moteur d'un angle en degrés"""
        steps = int((angle / DEGREES_PER_CIRCLE) * (self.steps_per_rev * self.microstep))
        self.step(steps)



    def info(self):
        """Afficher les infos du moteur"""
        print(f"[TMC2225] Step pin: {self.step_pin} | Dir pin: {self.dir_pin} | "
              f"Speed: {self.speed_rpm:.2f} RPM | Dir: {self.direction}")

    def cleanup(self):
        """Nettoyer uniquement les GPIO de ce moteur"""
        GPIO.cleanup((self.step_pin, self.dir_pin))