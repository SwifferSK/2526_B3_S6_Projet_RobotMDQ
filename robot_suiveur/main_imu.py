"""Robot suiveur - Maintien de l'équilibre ultra simple.

Ce script :
- Initialise les moteurs
- Initialise l'IMU via drv_lsm6dsow
- Affiche les informations de l'accéléromètre et du gyroscope
- Essaie de maintenir le robot en équilibre (debout) en utilisant l'inclinaison.
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

# --- Réglages Ultra Simples d'Équilibre ---
# Si le robot penche, les moteurs vont tourner pour le rattraper.
KP = 1.5               # Facteur de correction (augmente si le robot tombe trop vite sans réagir)
KD = 0.05              # Facteur dérivé (utilise le gyroscope pour adoucir les réactions)
TARGET_ANGLE = -90.0   # L'angle où le robot est parfaitement droit au repos
LOOP_DELAY = 0.02      # Boucle très rapide (50Hz) indispensable pour l'équilibre
MAX_SPEED = 60.0       # Vitesse max des moteurs en RPM pour éviter des commandes extrêmes


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
        
        # Moteurs initialisés à l'arrêt
        motors.set_speeds(0, 0)
        motors.start_continuous()
        time.sleep(0.5)

        print("Début de l'équilibrage dans 1 seconde. Tenez le robot droit !")
        time.sleep(1)

        last_time = time.time()
        print_counter = 0

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
            
            # --- Logique d'équilibrage ---
            # On utilise l'axe X (angle_x) comme point d'équilibre.
            current_angle = angle_x
            
            # Le gyroscope donne la vitesse de rotation (dérivée). Sur l'axe X:
            gyro_x_dps = x_g * SF_200DPS
            
            # Erreur par rapport à l'équilibre parfait
            error = current_angle - TARGET_ANGLE
            
            # Calcul de la vitesse à envoyer aux roues (Correction Proportionnelle + Dérivée)
            # Si le robot tombe en avant, il doit avancer pour remettre les roues sous son centre de gravité.
            correction_speed = (error * KP) + (gyro_x_dps * KD)
            
            # Bridage de la vitesse max
            if correction_speed > MAX_SPEED:
                correction_speed = MAX_SPEED
            elif correction_speed < -MAX_SPEED:
                correction_speed = -MAX_SPEED
                
            # Envoi de la même vitesse aux deux moteurs
            motors.set_speeds(correction_speed, correction_speed)
            
            # Affichage ralenti pour ne pas inonder la console (1 fois toutes les 25 boucles -> ~2 fois par seconde)
            print_counter += 1
            if print_counter >= 25:
                print(f"Inclinaison X (Utilisé): {current_angle:.2f}° | Y: {angle_y:.2f}° | Gyro X: {gyro_x_dps:.2f} dps")
                print(f"-> Vitesse Moteurs: {correction_speed:.2f} RPM | Erreur: {error:.2f}°")
                print("-" * 50)
                print_counter = 0

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
