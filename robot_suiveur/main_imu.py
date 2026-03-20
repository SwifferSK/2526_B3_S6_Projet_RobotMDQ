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
# Valeurs par défaut
KP_DEFAULT = 25           
KD_DEFAULT = 0              
KI_DEFAULT = 0.0               
ALPHA_DEFAULT = 0.90   # Réduit de 0.98 à 0.90 pour être plus réactif
TARGET_ANGLE_DEFAULT = -85   # Point d'équilibre par défaut
DEADBAND = 0        
MAX_INTEGRAL = 100.0   
LOOP_DELAY = 0.01      
MAX_SPEED = 1000    # Augmenté de 60 à 300 RPM pour plus de puissance
PRINT_EVERY = 100   # Une fois par seconde (100Hz / 100)


def get_float_input(prompt: str, default: float) -> float:
    """Demande une valeur à l'utilisateur via le terminal avec une valeur par défaut."""
    try:
        user_input = input(f"{prompt} [défaut={default}] : ").strip()
        if not user_input:
            return default
        return float(user_input)
    except (ValueError, EOFError, KeyboardInterrupt):
        print(f" -> Utilisation de la valeur par défaut : {default}")
        return default


def main() -> None:
    print("\n" + "="*40)
    print("      RÉGLAGE DES PARAMÈTRES PID")
    print("="*40)
    kp = get_float_input("Entrez KP (Proportionnel)", KP_DEFAULT)
    kd = get_float_input("Entrez KD (Dérivé)", KD_DEFAULT)
    ki = get_float_input("Entrez KI (Intégral)", KI_DEFAULT)
    alpha = get_float_input("Entrez ALPHA (Filtre [0.5-0.99])", ALPHA_DEFAULT)
    target_angle = get_float_input("Entrez TARGET_ANGLE (Angle d'équilibre)", TARGET_ANGLE_DEFAULT)
    print("="*40)
    print(f"Paramètres validés : KP={kp}, KD={kd}, KI={ki}, ALPHA={alpha}, TARGET={target_angle}\n")

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

        print("\n" + "!"*40)
        print(" ! ATTENTION : Tenez le robot BIEN DROIT")
        print(" ! Il va s'initialiser dans 1 seconde...")
        print("!"*40 + "\n")
        time.sleep(1)

        # Variable pour le filtre passe-bas et régulateur PID
        filtered_angle_x = -90.0
        integral_error = 0.0
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
            gyro_x_dps = x_g * SF_200DPS

            # --- Filtre Complémentaire (Complementary Filter) ---
            # Combine le gyroscope (rapide, sans beaucoup de bruit de vibration) 
            # et l'accéléromètre (pas de dérive lente mais très bruité par les moteurs).
            filtered_angle_x = alpha * (filtered_angle_x + gyro_x_dps * dt) + (1.0 - alpha) * angle_x

            # --- Logique d'équilibrage ---
            # On utilise l'angle filtré pour la stabilité
            current_angle = filtered_angle_x
            
            # Formule d'erreur Inverse : Target - Current
            error = target_angle - current_angle
            
            # --- Zone morte (Deadband) ---
            # Si l'erreur est toute petite, on ignore pour éviter qu'il tremble
            if abs(error) < DEADBAND:
                correction_speed = 0.0
                integral_error = 0.0 # On vide l'intégrale quand on est dans la zone morte
            else:
                # Accumulation de l'erreur pour la constante Intégrale (I)
                integral_error += error * dt
                
                # Anti-windup pour éviter que le terme intégral grimpe à l'infini
                if integral_error > MAX_INTEGRAL:
                    integral_error = MAX_INTEGRAL
                elif integral_error < -MAX_INTEGRAL:
                    integral_error = -MAX_INTEGRAL

                # Calcul de la vitesse à envoyer aux roues (Correction PID Complète)
                correction_speed = (error * kp) - (gyro_x_dps * kd) + (integral_error * ki)
            
            # Bridage de la vitesse max
            if correction_speed > MAX_SPEED:
                correction_speed = MAX_SPEED
            elif correction_speed < -MAX_SPEED:
                correction_speed = -MAX_SPEED
                
            # Les moteurs pas-à-pas sont souvent montés en miroir sur un robot 2 roues.
            # Étant donné que le robot réagissait à l'envers (il reculait quand il tombait en avant),
            # nous inversons les signes de la correction pour le forcer à "rattraper" sa chute !
            motors.set_speeds(-correction_speed, correction_speed)
            
            # Affichage ralenti pour ne pas inonder la console (1 fois toutes les 100 boucles -> ~1 fois par seconde)
            print_counter += 1
            if print_counter >= PRINT_EVERY:
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
