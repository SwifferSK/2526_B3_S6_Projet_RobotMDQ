"""Robot suiveur - Maintien du cap ultra simple.

Ce script :
- Initialise les moteurs
- Initialise l'IMU via drv_lsm6dsow
- Affiche les informations de l'accéléromètre et du gyroscope
- Avance tout droit en utilisant les données de l'accéléromètre (ou gyro) pour se corriger.
"""

from __future__ import annotations

import time
import sys
import os
import math

# Ajout du dossier 'imu' au chemin pour pouvoir importer drv_lsm6dsow et setting tels quels
sys.path.append(os.path.join(os.path.dirname(__file__), "imu"))

# Import de l'IMU (exactement comme dans app.py)
try:
    from drv_lsm6dsow import *
    from setting import *
except ImportError as e:
    print(f"Erreur d'import : {e}")
    print("Normal sur Windows. À tester sur Raspberry Pi.")
    sys.exit(1)

# Import des modules moteurs
from motor.controller import DualMotorController
from motor.config import (
    MOTOR1_STEP_PIN,
    MOTOR1_DIR_PIN,
    MOTOR1_SPEED_RPM,
    MOTOR1_DIRECTION,
    MOTOR2_STEP_PIN,
    MOTOR2_DIR_PIN,
    MOTOR2_SPEED_RPM,
    MOTOR2_DIRECTION,
)

# --- Réglages Ultra Simples ---
BASE_SPEED = 10.0      # Vitesse des moteurs en RPM
KP = 0.5               # Facteur de correction (0 si tu veux qu'il aille juste tout droit sans rien corriger)
LOOP_DELAY = 0.5       # On ralentit la boucle pour bien lire les prints (comme app.py)


def main() -> None:
    print("Initialisation de l'IMU...")
    try:
        driver = drv_lsm6dsow(bus=1)
    except Exception as e:
        print(f"Erreur IMU : {e}")
        return

    # Initialisation des moteurs
    motors = DualMotorController(
        motor1_params={
            "step": MOTOR1_STEP_PIN,
            "dir": MOTOR1_DIR_PIN,
            "speed_rpm": MOTOR1_SPEED_RPM,
            "direction": MOTOR1_DIRECTION,
        },
        motor2_params={
            "step": MOTOR2_STEP_PIN,
            "dir": MOTOR2_DIR_PIN,
            "speed_rpm": MOTOR2_SPEED_RPM,
            "direction": MOTOR2_DIRECTION,
        },
    )

    try:
        print("Démarrage du robot. Ctrl+C pour arrêter.")
        motors.info()
        
        # Moteurs en avant toute
        motors.set_speeds(BASE_SPEED, BASE_SPEED)
        motors.start_continuous()
        time.sleep(0.5)

        # Variables pour le calcul du cap (lacet/yaw) basé sur le gyroscope
        current_angle_z = 0.0
        last_time = time.time()

        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Lecture IMU (même chose que dans app.py)
            x_a, y_a, z_a = driver.read_accel()
            x_g, y_g, z_g = driver.read_gyro()
            
            # Calcul des angles d'inclinaison avec l'accéléromètre (Pitch / Roll)
            angle_x = math.degrees(math.atan2(y_a * SF_2G, z_a * SF_2G))
            angle_y = math.degrees(math.atan2(x_a * SF_2G, z_a * SF_2G))
            
            # Affichage demandé (comme dans app.py)
            print(f"Accel X: {(x_a * SF_2G):.2f}g, Y: {(y_a * SF_2G):.2f}g, Z: {(z_a * SF_2G):.2f}g | "
                  f"Gyro X: {(x_g * SF_200DPS):.2f}dps, Y: {(y_g * SF_200DPS):.2f}dps, Z: {(z_g * SF_200DPS):.2f}dps")
            print(f"Angle X: {angle_x:.2f}°, Angle Y: {angle_y:.2f}°")

            # --- Correction ultra simple pour aller droit avec l'axe Z (Gyroscope lacet) ---
            # L'accéléromètre ne peut pas calculer la boussole/lacet, on utilise le gyro Z.
            gyro_z_dps = z_g * SF_200DPS
            if abs(gyro_z_dps) < 1.0: 
                gyro_z_dps = 0.0 # Ignorer le bruit
                
            current_angle_z += gyro_z_dps * dt

            # Correction des moteurs (si l'angle est très différent de 0, on compense)
            correction = current_angle_z * KP
            
            # On demande aux moteurs d'ajuster leur vitesse pour compenser la rotation
            motors.set_speeds(BASE_SPEED - correction, BASE_SPEED + correction)
            
            print(f"Cap actuel (Z): {current_angle_z:.2f}° | Correction appliquée: {correction:.2f}")
            print("-" * 50)

            time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    finally:
        try:
            motors.stop_all()
        except:
            pass


if __name__ == "__main__":
    main()
