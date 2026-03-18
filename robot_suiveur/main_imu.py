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
    MOTOR1_DIRECTION,
    MOTOR2_STEP_PIN,
    MOTOR2_DIR_PIN,
    MOTOR2_DIRECTION,
)

# --- Réglages Ultra Simples d'Équilibre ---
# Si le robot penche, les moteurs vont tourner pour le rattraper.
KP = 1.5               # Positif ! Car l'erreur est désormais (Target - Current)
KD = 0.05              # Positif pour que le gyroscope s'oppose aux variations
TARGET_ANGLE = -90.0   # L'angle où le robot est parfaitement droit au repos
DEADBAND = 2.0         # Zone morte (en degrés) autour de -90 où le robot ne fait rien (évite les tremblements)
ALPHA = 0.98           # Coefficient du filtre complémentaire (0.98 = 98% gyro, 2% inclinaison accélérateur)
LOOP_DELAY = 0.01      # Boucle plus rapide (100Hz) pour un bon échantillonnage
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
            "direction": MOTOR1_DIRECTION,
        },
        motor2_params={
            "step": MOTOR2_STEP_PIN,
            "dir": MOTOR2_DIR_PIN,
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

        # Variable pour le filtre passe-bas
        filtered_angle_x = -90.0
        last_time = time.time()
        print_counter = 0

        while True:
            current_time = time.time()
            dt = current_time - last_time
            # Sécurité anti-zéro pour la première boucle
            if dt <= 0:
                dt = 0.001
            last_time = current_time

            # Lecture IMU (même chose que dans app.py)
            x_a, y_a, z_a = driver.read_accel()
            x_g, y_g, z_g = driver.read_gyro()
            
            # Calcul des angles d'inclinaison avec l'accéléromètre (Pitch / Roll)
            angle_x = math.degrees(math.atan2(y_a * SF_2G, z_a * SF_2G))
            angle_y = math.degrees(math.atan2(x_a * SF_2G, z_a * SF_2G))
            
            # Le gyroscope donne la vitesse de rotation (dérivée). Sur l'axe X:
            # IMPORTANT: Si le gyroscope ne va pas dans le même sens que l'accéléromètre,
            # le filtre complémentaire "détruit" l'angle et le PID compense à l'envers.
            # Mettre INVERT_GYRO = -1.0 si le robot devient fou en tombant d'un côté !
            INVERT_GYRO = 1.0
            gyro_x_dps = x_g * SF_200DPS * INVERT_GYRO

            # --- Filtre Complémentaire (Complementary Filter) ---
            # Combine le gyroscope (rapide, sans beaucoup de bruit de vibration) 
            # et l'accéléromètre (pas de dérive lente mais très bruité par les moteurs).
            filtered_angle_x = ALPHA * (filtered_angle_x + gyro_x_dps * dt) + (1.0 - ALPHA) * angle_x

            # --- Logique d'équilibrage ---
            # On utilise l'angle filtré pour la stabilité
            current_angle = filtered_angle_x
            
            # Formule d'erreur Inverse : Target - Current
            error = TARGET_ANGLE - current_angle
            
            # --- Zone morte (Deadband) ---
            # Si l'erreur est toute petite, on ignore pour éviter qu'il tremble
            if abs(error) < DEADBAND:
                correction_speed = 0.0
            else:
                # Calcul de la vitesse à envoyer aux roues (Correction Proportionnelle + Dérivée)
                # Remarque: gyro_x_dps n'a pas besoin d'être soustrait vu qu'il est la dérivée de current,
                # mais si on utilise (Target - Current), pour s'opposer, la dérivée de l'erreur est : (0 - vitesse) = -vitesse.
                # On utilise + ou - selon la définition du repère. A ajuster si le robot oscille trop.
                correction_speed = (error * KP) - (gyro_x_dps * KD)
            
            # Bridage de la vitesse max
            if correction_speed > MAX_SPEED:
                correction_speed = MAX_SPEED
            elif correction_speed < -MAX_SPEED:
                correction_speed = -MAX_SPEED
                
            # Les moteurs pas-à-pas sont souvent montés en miroir sur un robot 2 roues.
            # Pour avancer droit, un moteur doit tourner en sens horaire (positif) et l'autre en anti-horaire (négatif).
            # Si le robot tourne sur lui-même au lieu d'avancer/reculer, on inverse le signe d'un des deux.
            motors.set_speeds(correction_speed, -correction_speed)
            
            # Affichage ralenti pour ne pas inonder la console (1 fois toutes les 10 boucles -> ~10 fois par seconde)
            print_counter += 1
            if print_counter >= 10:
                print(f"Inclinaison X (Utilisé): {current_angle:.2f}° | Gyro X: {gyro_x_dps:.2f} dps")
                print(f"-> Vitesse Moteurs: {correction_speed:.2f} RPM | Erreur: {error:.2f}°")
                print("-" * 50)
                print_counter = 0

            # On attend le temps restant pour avoir exactement 100Hz
            time_spent = time.time() - current_time
            sleep_time = LOOP_DELAY - time_spent
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    finally:
        try:
            motors.stop_all()
        except:
            pass


if __name__ == "__main__":
    main()
