"""Robot suiveur de ligne - point d'entrée.

Ce script :
- lit les 8 capteurs IR via MCP3208
- détecte la position de la ligne (left/center/right/none)
- commande les 2 moteurs pas-à-pas (STEP/DIR) via le module motor/

Lance :
  python3 main.py
"""

from __future__ import annotations

import time

from sensors.MCP3208 import MCP3208
from sensors.line_detector import detect_line
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

# --- Réglages suiveur de ligne ---
THRESHOLD = 1.5     # ajuste selon tes capteurs
LOOP_DELAY = 0.0    # tu peux mettre 0.02 si tu veux ralentir la boucle

# Angles de commande (plus petit = plus "doux")
FORWARD_ANGLE = 5.0
TURN_ANGLE = 3.0
SEARCH_ANGLE = 2.0


def main() -> None:
    adc = MCP3208(vref=3.3)

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
        print("Starting line follower (Ctrl+C to stop)...")
        motors.info()
        
        # Démarrer le mouvement continu en arrière-plan (moteurs initialement à 0)
        motors.set_speeds(0, 0)
        motors.start_continuous()

        while True:
            # detect_line s'occupe de lire les capteurs et introduit un mini délai de 0.05s
            pos = detect_line(adc, threshold=THRESHOLD, verbose=True)

            # Stratégie simple :
            # - center : avance
            # - left   : corrige à gauche (ralentit/recule un peu côté gauche ou avance côté droit)
            # - right  : corrige à droite
            # - none   : petite recherche
            if pos == "center":
                # Avance tout droit
                motors.set_speeds(BASE_SPEED, BASE_SPEED)
            elif pos == "left":
                # Tourne à gauche : moteur gauche très lent, moteur droit normal
                motors.set_speeds(BASE_SPEED * TURN_SPEED_REDUCTION, BASE_SPEED)
            elif pos == "right":
                # Tourne à droite : moteur droit très lent, moteur gauche normal
                motors.set_speeds(BASE_SPEED, BASE_SPEED * TURN_SPEED_REDUCTION)
            else:
                # Aucun capteur ne voit la ligne : mini balayage
                motors.rotate_both(SEARCH_ANGLE, -SEARCH_ANGLE)

            if LOOP_DELAY > 0:
                time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        try:
            adc.close()
        except Exception:
            pass
        try:
            motors.stop_all()
        except Exception:
            pass


if __name__ == "__main__":
    main()
