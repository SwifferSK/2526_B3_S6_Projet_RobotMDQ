"""Robot suiveur - Maintien de l'équilibre Multithreading.

Ce script :
- Initialise les moteurs via pigpio
- Initialise l'IMU
- Utilise deux Threads séparés pour de hautes performances :
  1. Thread IMU : Lit l'IMU à 200Hz, applique les filtres (Passe-bas + Complémentaire).
  2. Thread PID : Calcule l'erreur à 100Hz et met à jour la vitesse des moteurs, garanti sans lag.
"""

from __future__ import annotations

import time
import sys
import os
import math
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), "imu"))

try:
    from drv_lsm6dsow import *
    from setting import *
except ImportError as e:
    print(f"Erreur d'import : {e}")
    print("Testé sur Windows ? Attendu sur Raspberry Pi.")
    sys.exit(1)

from motor.controller import DualMotorController
from motor.config import (
    MOTOR1_STEP_PIN,
    MOTOR1_DIR_PIN,
    MOTOR1_DIRECTION,
    MOTOR2_STEP_PIN,
    MOTOR2_DIR_PIN,
    MOTOR2_DIRECTION,
)

# --- Réglages Ultra Simples d'Équilibre ---
KP_DEFAULT = 45.0         
KD_DEFAULT = 0.8       # Amortisseur lissé
ALPHA_DEFAULT = 0.98   # Filtre complémentaire (plus élevé = plus de confiance au gyro)
TARGET_ANGLE_DEFAULT = -86.5   

# Global state partagé entre les threads
class RobotState:
    def __init__(self):
        self.lock = threading.Lock()
        self.angle_x = TARGET_ANGLE_DEFAULT
        self.gyro_x = 0.0
        self.running = True

state = RobotState()


def imu_worker(driver, alpha):
    """Thread 1: Lecture très rapide et filtrage de l'IMU (200Hz)"""
    print("[Thread IMU] Démarré.")
    last_time = time.time()
    
    # Valeurs internes
    filtered_angle = TARGET_ANGLE_DEFAULT
    
    while state.running:
        current_time = time.time()
        dt = current_time - last_time
        if dt <= 0:
            dt = 0.001
        last_time = current_time

        try:
            x_a, y_a, z_a = driver.read_accel()
            x_g, y_g, z_g = driver.read_gyro()
            
            # Accéléromètre : donne l'angle absolu mais très bruité
            angle_x_acc = math.degrees(math.atan2(y_a * SF_2G, z_a * SF_2G))
            # Gyroscope : donne la vitesse mais dérive
            gyro_x_dps = x_g * SF_200DPS

            # Filtre Complémentaire
            new_filtered_angle = alpha * (filtered_angle + gyro_x_dps * dt) + (1.0 - alpha) * angle_x_acc
            filtered_angle = new_filtered_angle

            # Partage sécurisé des variables propres
            with state.lock:
                state.angle_x = filtered_angle
                state.gyro_x = gyro_x_dps

        except Exception as e:
            # En cas d'erreur I2C transitoire on ignore sans crasher le thread
            pass

        # Petite pause pour tourner à ~200Hz (0.005s)
        time.sleep(0.005)
    
    print("[Thread IMU] Arrêté.")


def get_float_input(prompt: str, default: float) -> float:
    try:
        user_input = input(f"{prompt} [défaut={default}] : ").strip()
        if not user_input:
            return default
        return float(user_input)
    except:
        return default


def main() -> None:
    print("="*40)
    kp = get_float_input("Entrez KP (Force)", KP_DEFAULT)
    kd = get_float_input("Entrez KD (Amortisseur/Vibrations)", KD_DEFAULT)
    alpha = get_float_input("Entrez ALPHA (Filtre Complémentaire)", ALPHA_DEFAULT)
    target_angle = get_float_input("Entrez TARGET_ANGLE (Angle)", TARGET_ANGLE_DEFAULT)
    print("="*40)

    # 1. Init IMU
    print("Initialisation de l'IMU...")
    try:
        driver = drv_lsm6dsow(bus=1)
    except Exception as e:
        print(f"Erreur IMU : {e}")
        return

    # 2. Init Moteurs (utilise maintenant pigpio + Hardware PWM)
    print("Initialisation des Moteurs (Pigpio Hardware PWM)...")
    try:
        motors = DualMotorController(
            motor1_params={"step": MOTOR1_STEP_PIN, "dir": MOTOR1_DIR_PIN, "direction": MOTOR1_DIRECTION},
            motor2_params={"step": MOTOR2_STEP_PIN, "dir": MOTOR2_DIR_PIN, "direction": MOTOR2_DIRECTION},
        )
    except Exception as e:
        print(f"Erreur Moteur : {e}")
        return

    # 3. Lancer Threads
    imu_thread = threading.Thread(target=imu_worker, args=(driver, alpha), daemon=True)
    imu_thread.start()

    motors.set_speeds(0, 0)
    motors.start_continuous()
    
    time.sleep(1.0)
    print("\n" + "!"*40)
    print(" ! ÉQUILIBRAGE ACTIF DANS 1 SECONDE")
    print(" ! Lâchez le robot doucement...")
    print("!"*40 + "\n")
    time.sleep(1)

    print_counter = 0
    max_speed = 800.0
    deadband = 0.1
    filtered_gyro_x = 0.0 # On commence à 0

    try:
        # Boucle PID (Main Thread) : On tourne à ~100Hz pour des commandes fluides
        while state.running:
            # 1. Lecture des variables avec le lock très rapide
            with state.lock:
                current_angle = state.angle_x
                raw_gyro_x = state.gyro_x

            # 2. Filtre Passe-bas sur la dérivée (gyro) pour adoucir le KD
            # Cela évite que les moteurs donnent des petits "coups" secs à cause du bruit gyro
            filtered_gyro_x = (filtered_gyro_x * 0.7) + (raw_gyro_x * 0.3)

            # 3. Calcul de l'erreur
            error = target_angle - current_angle

            if abs(error) < deadband:
                correction_speed = 0.0
            else:
                # PD Controller
                correction_speed = (error * kp) - (filtered_gyro_x * kd)

            # 4. Limites
            if correction_speed > max_speed:
                correction_speed = max_speed
            elif correction_speed < -max_speed:
                correction_speed = -max_speed

            # 5. Envoi des vitesses de manière instanée grâce à pigpio !
            # Note: modifiez le signe ici si jamais le robot va à l'envers ou tourne sur lui-même
            motors.set_speeds(-correction_speed, correction_speed)

            # 6. Affichage au ralenti
            print_counter += 1
            if print_counter >= 50: # Toute les demi-secondes
                print(f"Angle X: {current_angle:.2f}° | Gyro X: {filtered_gyro_x:.2f} dps")
                print(f"Vitesse PWM: {correction_speed:.1f} RPM")
                print("-" * 30)
                print_counter = 0

            time.sleep(0.01) # Boucle 100Hz propre

    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    finally:
        state.running = False
        imu_thread.join(timeout=1.0)
        try:
            motors.stop_all()
        except:
            pass
        print("Fin du programme.")


if __name__ == "__main__":
    main()
