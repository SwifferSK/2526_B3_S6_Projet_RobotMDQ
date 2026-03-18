"""Robot Bipède — Suiveur de Ligne Auto-Stable.

Point d'entrée principal combinant :
  - Boucle de balance (IMU + PID interne, ~100 Hz)
  - Boucle de suivi de ligne (IR + PID externe)

Commandes :
  python3 main_balance_line.py               # mode complet
  python3 main_balance_line.py --calibrate   # calibrer l'offset mécanique
  python3 main_balance_line.py --balance     # balance seule, sans suivi de ligne
"""
from __future__ import annotations

import argparse
import signal
import time

from sensors.MCP3208 import MCP3208
from sensors.line_detector import get_line_error
from motor.controller import DualMotorController
from motor.config import (
    MOTOR1_STEP_PIN, MOTOR1_DIR_PIN, MOTOR1_DIRECTION,
    MOTOR2_STEP_PIN, MOTOR2_DIR_PIN, MOTOR2_DIRECTION,
    MAX_SPEED_RPM,
    BALANCE_KP, BALANCE_KI, BALANCE_KD,
    LINE_KP, LINE_KI, LINE_KD,
    ALPHA, ANGLE_OFFSET,
    LINE_THRESHOLD, SEARCH_SPEED_RPM,
)
from control.pid import PID
from imu.imu_fusion import IMUFusion


# ── Configuration ──────────────────────────────────────────────────────────────
LOOP_HZ = 100          # fréquence cible de la boucle principale
FALL_ANGLE = 45.0      # angle (°) au-delà duquel on considère que le robot a chuté
DISPLAY_HZ = 10        # fréquence de rafraîchissement de l'affichage télémétrie


# ── Initialisation ─────────────────────────────────────────────────────────────
def build_motors() -> DualMotorController:
    return DualMotorController(
        motor1_params={"step": MOTOR1_STEP_PIN, "dir": MOTOR1_DIR_PIN, "direction": MOTOR1_DIRECTION},
        motor2_params={"step": MOTOR2_STEP_PIN, "dir": MOTOR2_DIR_PIN, "direction": MOTOR2_DIRECTION},
    )


# ── Boucle principale ──────────────────────────────────────────────────────────
def run(balance_only: bool = False) -> None:
    print("Initialisation de l'IMU…")
    imu = IMUFusion(alpha=ALPHA, angle_offset=ANGLE_OFFSET)

    adc = MCP3208(vref=3.3) if not balance_only else None
    motors = build_motors()

    # PID balance — boucle interne
    balance_pid = PID(
        kp=BALANCE_KP, ki=BALANCE_KI, kd=BALANCE_KD,
        out_min=-MAX_SPEED_RPM, out_max=MAX_SPEED_RPM,
    )

    # PID ligne — boucle externe
    line_pid = PID(
        kp=LINE_KP, ki=LINE_KI, kd=LINE_KD,
        out_min=-MAX_SPEED_RPM / 2, out_max=MAX_SPEED_RPM / 2,
    )

    # Gestion Ctrl+C propre
    running = True
    def _stop(signum, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    motors.set_speeds(0, 0)
    motors.start_continuous()

    print("Démarrage — Ctrl+C pour arrêter")
    if balance_only:
        print("Mode : BALANCE SEULE (pas de suivi de ligne)")

    dt_target = 1.0 / LOOP_HZ
    display_interval = 1.0 / DISPLAY_HZ
    last_time = time.monotonic()
    last_display = time.monotonic()
    steer_cmd = 0.0
    line_err: float | None = None
    loop_count = 0
    actual_hz = 0.0

    try:
        while running:
            now = time.monotonic()
            dt = now - last_time
            if dt < dt_target:
                time.sleep(dt_target - dt)
                continue
            last_time = now

            # ── Lecture IMU + PID balance ────────────────────────────────────
            angle = imu.get_tilt_angle()

            if abs(angle) > FALL_ANGLE:
                print(f"\nChute détectée (angle={angle:.1f}°) — arrêt moteurs")
                motors.set_speeds(0, 0)
                balance_pid.reset()
                line_pid.reset()
                steer_cmd = 0.0
                # Attendre que le robot soit relevé
                time.sleep(1.0)
                last_time = time.monotonic()  # évite un grand dt au redémarrage
                continue

            speed_cmd = balance_pid.compute(error=angle, dt=dt)

            # ── Lecture capteurs IR + PID ligne ─────────────────────────────
            if not balance_only and adc is not None:
                line_err, _readings = get_line_error(adc, threshold=LINE_THRESHOLD)

                if line_err is not None:
                    steer_cmd = line_pid.compute(error=line_err, dt=dt)
                else:
                    steer_cmd = SEARCH_SPEED_RPM
                    line_pid.reset()

            # ── Commande différentielle gauche/droite ────────────────────────
            speed_left  = speed_cmd + steer_cmd
            speed_right = speed_cmd - steer_cmd

            motors.set_speeds(speed_left, speed_right)

            # ── Télémétrie ───────────────────────────────────────────────────
            loop_count += 1
            now2 = time.monotonic()
            if now2 - last_display >= display_interval:
                elapsed = now2 - last_display
                actual_hz = loop_count / elapsed if elapsed > 0 else 0.0
                loop_count = 0
                last_display = now2
                _print_telemetry(
                    angle=angle,
                    speed_cmd=speed_cmd,
                    steer_cmd=steer_cmd,
                    speed_left=speed_left,
                    speed_right=speed_right,
                    line_err=line_err,
                    dt=dt,
                    actual_hz=actual_hz,
                    balance_only=balance_only,
                )

    finally:
        motors.stop_all()
        imu.close()
        if adc is not None:
            adc.close()
        print("\nArrêté proprement.")


# ── Télémétrie ─────────────────────────────────────────────────────────────────
def _print_telemetry(
    angle: float,
    speed_cmd: float,
    steer_cmd: float,
    speed_left: float,
    speed_right: float,
    line_err: "float | None",
    dt: float,
    actual_hz: float,
    balance_only: bool,
) -> None:
    """Affiche une ligne de télémétrie sur stdout (rafraîchissement en place)."""
    line_str = f"LINE_ERR={line_err:+.2f}" if line_err is not None else "LINE_ERR=None "
    mode_str = "BAL" if balance_only else "BAL+LINE"

    msg = (
        f"[{mode_str}] "
        f"Angle={angle:+6.2f}°  "
        f"PID_out={speed_cmd:+6.1f}RPM  "
        f"Steer={steer_cmd:+5.1f}  "
        f"L={speed_left:+6.1f}RPM  R={speed_right:+6.1f}RPM  "
        f"{line_str}  "
        f"dt={dt*1000:.1f}ms  Hz={actual_hz:.0f}"
    )
    # \r pour réécrire sur la même ligne (terminal compatible ANSI)
    print(f"\r{msg}", end="", flush=True)



# ── Calibration ────────────────────────────────────────────────────────────────
def calibrate() -> None:
    print("Calibration de l'offset mécanique.")
    print("Placez le robot en position verticale et appuyez sur Entrée…")
    input()
    imu = IMUFusion(alpha=ALPHA, angle_offset=0.0)
    offset = imu.calibrate_offset(samples=200)
    imu.close()
    print(f"\nOffset mesuré : {offset:.4f} °")
    print(f"Mettez à jour  ANGLE_OFFSET = {offset:.4f}  dans motor/config.py")


# ── Entrée ─────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Robot bipède suiveur de ligne auto-stable")
    parser.add_argument("--calibrate", action="store_true", help="Calibrer l'offset mécanique de l'IMU")
    parser.add_argument("--balance",   action="store_true", help="Mode balance seule (sans suivi de ligne)")
    args = parser.parse_args()

    if args.calibrate:
        calibrate()
    else:
        run(balance_only=args.balance)


if __name__ == "__main__":
    main()
