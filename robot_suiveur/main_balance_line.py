"""Robot Bipède Suiveur de Ligne Auto-Stable.

Ce script est le point d'entrée principal. Il combine :
- La boucle de balance (IMU + PID + Gravité)
- La boucle de suivi de ligne (Capteurs IR + PID)
- La télémétrie en temps réel

Usage:
    python3 main_balance_line.py           # Mode complet
    python3 main_balance_line.py --balance # Balance seule
    python3 main_balance_line.py --calibrate # Calibrer l'angle vertical
"""

from __future__ import annotations

import argparse
import signal
import time
import math

from sensors.MCP3208 import MCP3208
from sensors.line_detector import get_line_error
from motor.controller import DualMotorController
from motor.config import (
    MOTOR1_STEP_PIN, MOTOR1_DIR_PIN, MOTOR1_DIRECTION,
    MOTOR2_STEP_PIN, MOTOR2_DIR_PIN, MOTOR2_DIRECTION,
    MAX_SPEED_RPM,
    BALANCE_KP, BALANCE_KI, BALANCE_KD, BALANCE_KG,
    LINE_KP, LINE_KI, LINE_KD,
    ALPHA, OUTPUT_BETA, IMU_AXIS, ANGLE_OFFSET, DEADBAND_DEG,
    LINE_THRESHOLD, SEARCH_SPEED_RPM,
)
from control.pid import PID
from control.balance_controller import BalanceController

# ── Configuration ──────────────────────────────────────────────────────────────
LOOP_HZ = 100          # fréquence cible de la boucle principale
FALL_ANGLE = 45.0      # angle (°) au-delà duquel on considère que le robot a chuté
DISPLAY_HZ = 10        # fréquence de rafraîchissement de l'affichage télémétrie

# Variable globale pour l'arrêt propre
running = True

def signal_handler(sig, frame):
    global running
    print("\nArrêt demandé...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# ── Initialisation ─────────────────────────────────────────────────────────────
def build_motors() -> DualMotorController:
    return DualMotorController(
        motor1_params={"step": MOTOR1_STEP_PIN, "dir": MOTOR1_DIR_PIN, "direction": MOTOR1_DIRECTION},
        motor2_params={"step": MOTOR2_STEP_PIN, "dir": MOTOR2_DIR_PIN, "direction": MOTOR2_DIRECTION},
    )

# ── Boucle principale ──────────────────────────────────────────────────────────
def run(balance_only: bool = False) -> None:
    print(f"Initialisation de l'IMU (Axe={IMU_AXIS})…")
    
    # Contrôleur de balance (encapsule IMU + PID + Gravité)
    bc = BalanceController(
        kp=BALANCE_KP, ki=BALANCE_KI, kd=BALANCE_KD, kg=BALANCE_KG,
        max_speed=MAX_SPEED_RPM,
        angle_offset=ANGLE_OFFSET,
        alpha=ALPHA,
        output_beta=OUTPUT_BETA,
        axis=IMU_AXIS,
        deadband=DEADBAND_DEG,
    )

    # ADC pour la ligne
    adc = MCP3208(vref=3.3) if not balance_only else None
    
    # PID ligne — boucle externe
    line_pid = PID(
        kp=LINE_KP, ki=LINE_KI, kd=LINE_KD,
        out_min=-MAX_SPEED_RPM/2, out_max=MAX_SPEED_RPM/2,
    )

    motors = build_motors()

    print("Démarrage du robot. Tenez-le droit !")
    if balance_only:
        print("Mode : BALANCE SEULE")

    dt_target = 1.0 / LOOP_HZ
    display_interval = 1.0 / DISPLAY_HZ
    last_time = time.monotonic()
    last_display = time.monotonic()
    
    steer_cmd = 0.0
    line_err: float | None = None
    loop_count = 0
    actual_hz = 0.0

    try:
        # Démarrage des moteurs
        motors.start_continuous()
        
        while running:
            now = time.monotonic()
            dt = now - last_time
            
            if dt < dt_target:
                time.sleep(max(0, dt_target - dt))
                continue
            
            last_time = now

            # ── 1. Boucle de Balance ─────────────────────────────────────────
            # Récupère l'angle et calcule la vitesse de base (speed_cmd)
            speed_cmd = bc.update(dt)
            angle = bc.angle

            # Arrêt d'urgence si chute
            if abs(angle) > FALL_ANGLE:
                print(f"\nChute ! (Angle={angle:.1f}°) - Arrêt")
                motors.set_speeds(0, 0)
                bc.reset()
                line_pid.reset()
                steer_cmd = 0.0
                time.sleep(1.0)
                last_time = time.monotonic()
                continue

            # ── 2. Boucle de Ligne ───────────────────────────────────────────
            if not balance_only and adc is not None:
                line_err, _readings = get_line_error(adc, threshold=LINE_THRESHOLD)

                if line_err is not None:
                    steer_cmd = line_pid.compute(error=line_err, dt=dt)
                else:
                    # Ligne perdue : on tourne sur place doucement
                    steer_cmd = SEARCH_SPEED_RPM
                    line_pid.reset()

            # ── 3. Mélange et Envoi aux Moteurs ──────────────────────────────
            speed_left  = speed_cmd + steer_cmd
            speed_right = speed_cmd - steer_cmd

            # NOTE: set_speeds() gère déjà l'inversion du moteur 2 via config.py
            motors.set_speeds(speed_left, speed_right)

            # ── 4. Télémétrie ────────────────────────────────────────────────
            loop_count += 1
            if now - last_display >= display_interval:
                elapsed = now - last_display
                actual_hz = loop_count / elapsed if elapsed > 0 else 0.0
                loop_count = 0
                last_display = now
                _print_telemetry(
                    angle=angle,
                    speed_cmd=speed_cmd,
                    steer_cmd=steer_cmd,
                    speed_left=speed_left,
                    speed_right=speed_right,
                    line_err=line_err,
                    dt=dt,
                    actual_hz=actual_hz,
                    mode="BAL+LINE" if not balance_only else "BAL",
                    deadband=DEADBAND_DEG
                )

    finally:
        motors.stop_all()
        bc.close()
        if adc is not None:
            adc.close()
        print("\nArrêté proprement.")

def _print_telemetry(angle, speed_cmd, steer_cmd, speed_left, speed_right, line_err, dt, actual_hz, mode, deadband):
    line_str = f"LINE={line_err:+.2f}" if line_err is not None else "LINE=None"
    # * si dans la zone morte
    db_marker = "*" if abs(angle) < deadband else " "
    
    msg = (
        f"[{mode}] "
        f"Ang={angle:+6.2f}°{db_marker} | "
        f"V_base={speed_cmd:+5.1f} | "
        f"St={steer_cmd:+5.1f} | "
        f"L={speed_left:+5.1f} R={speed_right:+5.1f} | "
        f"{line_str} | "
        f"Hz={actual_hz:.0f}"
    )
    print(f"\r{msg}", end="", flush=True)

# ── Calibration ────────────────────────────────────────────────────────────────
def calibrate() -> None:
    print("Calibration de l'offset vertical.")
    print("Tenez le robot parfaitement vertical et appuyez sur Entrée…")
    input()
    imu = BalanceController(
        angle_offset=0.0,
        axis=IMU_AXIS,
        alpha=ALPHA,
        output_beta=OUTPUT_BETA
    )
    # On fait une moyenne sur 2 secondes
    print("Mesure en cours…")
    offset = 0.0
    samples = 100
    for _ in range(samples):
        offset += imu._imu.get_tilt_angle()
        time.sleep(0.02)
    imu.close()
    
    avg_offset = offset / samples
    print(f"\nOffset vertical mesuré : {avg_offset:.2f} °")
    print(f"Mettez à jour ANGLE_OFFSET = {avg_offset:.2f} dans motor/config.py")

def main() -> None:
    parser = argparse.ArgumentParser(description="Robot bipède suiveur de ligne")
    parser.add_argument("--calibrate", action="store_true", help="Calibrer l'offset vertical")
    parser.add_argument("--balance",   action="store_true", help="Mode balance seule")
    args = parser.parse_args()

    if args.calibrate:
        calibrate()
    else:
        run(balance_only=args.balance)

if __name__ == "__main__":
    main()
