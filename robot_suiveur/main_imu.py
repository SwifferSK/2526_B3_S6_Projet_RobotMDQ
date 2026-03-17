"""Robot suiveur - Maintien du cap avec IMU (Gyroscope).

Ce script :
- Initialise les moteurs
- Initialise l'IMU (LSM6DSOX)
- Utilise le gyroscope (axe Z) pour calculer l'angle de lacet (yaw)
- Ajuste la vitesse des moteurs gauche/droit pour maintenir un cap de 0°

Lance :
  python3 main_imu.py
"""

from __future__ import annotations

import time
import sys

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

# Import de l'IMU
try:
    from imu.drv_lsm6dsow import drv_lsm6dsow
    from imu.setting import SF_200DPS
except ImportError:
    print("Erreur : Impossible d'importer les modules IMU.")
    print("Assurez-vous que les dépendances (smbus2, etc.) sont installées.")
    sys.exit(1)

# --- Réglages de la navigation au gyroscope ---
BASE_SPEED = 10.0      # Vitesse de base en RPM
KP = 0.5               # Coefficient proportionnel pour corriger la trajectoire
                       # (Augmenter si le robot ne corrige pas assez, diminuer s'il oscille)

LOOP_DELAY = 0.02      # Pause à chaque itération (Hz = 1/0.02 = 50Hz)


def main() -> None:
    # Initialisation de l'IMU
    print("Initialisation de l'IMU...")
    try:
        imu = drv_lsm6dsow(bus=1)
    except Exception as e:
        print(f"Erreur lors de la connexion à l'IMU : {e}")
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
        print("Starting IMU straight line navigation (Ctrl+C to stop)...")
        motors.info()
        
        # Démarrer le mouvement continu (moteurs initialement à 0)
        motors.set_speeds(0, 0)
        motors.start_continuous()

        current_angle_z = 0.0
        last_time = time.time()

        # Petite pause pour laisser l'IMU se stabiliser
        time.sleep(0.5)

        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Lecture du gyroscope
            x_g, y_g, z_g = imu.read_gyro()
            
            # Conversion de la valeur brute de l'axe Z en dps (degrés par seconde)
            # Attention : Selon l'orientation physique de l'IMU sur le robot,
            # il se peut que tu doives utiliser un autre axe (x ou y) ou inverser le signe.
            gyro_z_dps = z_g * SF_200DPS

            # Si le robot est à l'arrêt, le capteur bruit un peu.
            # On peut mettre un petit seuil (deadband) pour éviter la dérive
            if abs(gyro_z_dps) < 1.0:
                gyro_z_dps = 0.0

            # Intégration pour obtenir l'angle (Yaw)
            current_angle_z += gyro_z_dps * dt

            # Calcul de l'erreur (on veut que l'angle reste à 0)
            error = 0.0 - current_angle_z

            # Terme proportionnel
            correction = error * KP

            # Calcul des vitesses pour chaque moteur
            # Si le robot a tourné à droite (angle négatif -> erreur positive),
            # correction est positive -> on accélère le moteur droit et ralentit le gauche (ou inversement selon le montage)
            # Note : Assure-toi que MOTOR1 (ex: gauche) et MOTOR2 (ex: droit) correspondent bien!
            # Si le robot tourne du mauvais côté lors de la correction, il suffira d'inverser les signes de 'correction' ici :
            speed_motor1 = BASE_SPEED - correction
            speed_motor2 = BASE_SPEED + correction

            # On s'assure que la vitesse ne devienne pas négative de façon inattendue (ou qu'elle reste dans des limites)
            # Si on veut autoriser le robot à freiner complètement ou tourner en marche arrière, on garde tel quel (driver adapté)
            # Sinon on bride : max(0, min(speed_motor, MAX_SPEED))
            
            motors.set_speeds(speed_motor1, speed_motor2)

            # Debugging optionnel (dé-commenter pour voir les valeurs)
            # print(f"Angle Z: {current_angle_z:.2f}° | Z_dps: {gyro_z_dps:.2f} | M1: {speed_motor1:.2f} | M2: {speed_motor2:.2f}")

            time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        try:
            motors.stop_all()
        except Exception:
            pass


if __name__ == "__main__":
    main()
