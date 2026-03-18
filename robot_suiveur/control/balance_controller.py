"""Contrôleur de balance — boucle interne pour maintenir le robot debout.

Lit l'IMU, calcule la commande de vitesse (RPM) via PID,
et retourne (speed_base, steering) à la boucle principale.

Usage:
    from control.balance_controller import BalanceController
    bc = BalanceController()
    speed_base = bc.update(dt)
"""
from __future__ import annotations

import math
from imu.imu_fusion import IMUFusion
from control.pid import PID


class BalanceController:
    """Boucle de balance.

    Args:
        kp, ki, kd: Gains du PID balance.
        max_speed: Limite de vitesse en RPM (envoyée aux moteurs).
        angle_offset: Décalage mécanique (° — mesurer avant de démarrer).
        alpha: Coefficient du filtre complémentaire IMU (0.95–0.99).
    """

    def __init__(
        self,
        kp: float = 5.0,
        ki: float = 0.0,
        kd: float = 0.8,
        kg: float = 0.0,
        max_speed: float = 40.0,
        angle_offset: float = 0.0,
        alpha: float = 0.98,
        output_beta: float = 0.5,
        axis: str = 'X',
        deadband: float = 0.5,
    ) -> None:
        self._imu = IMUFusion(
            alpha=alpha,
            output_beta=output_beta,
            angle_offset=angle_offset,
            axis=axis
        )
        self._pid = PID(
            kp=kp,
            ki=ki,
            kd=kd,
            out_min=-max_speed,
            out_max=max_speed,
        )
        self.kg = kg
        self.max_speed = max_speed
        self.deadband = deadband
        self._last_angle: float = 0.0

    # ── Interface publique ────────────────────────────────────────────────────
    def update(self, dt: float) -> float:
        """Met à jour la boucle de balance.

        Returns:
            Commande de vitesse de base en RPM.
        """
        angle = self._imu.get_tilt_angle()
        self._last_angle = angle

        # 1. Zone morte (Deadband)
        # Si l'angle est très proche de la verticale, on ignore pour éviter les bruits de stepper
        angle_for_pid = 0.0 if abs(angle) < self.deadband else angle

        # 2. Terme PID
        pid_output = self._pid.compute(error=angle_for_pid, dt=dt)

        # 3. Terme Gravité (Feed-Forward)
        # Torque généré par le poids = m * g * L * sin(angle)
        # On compense par un RPM proportionnel : KG * sin(angle)
        gravity_comp = self.kg * math.sin(math.radians(angle))

        # Sortie totale = régulateur + compensation physique
        speed_cmd = pid_output + gravity_comp

        # Bridage final
        if speed_cmd > self.max_speed: speed_cmd = self.max_speed
        elif speed_cmd < -self.max_speed: speed_cmd = -self.max_speed

        return speed_cmd

    @property
    def angle(self) -> float:
        """Dernier angle de tangage lu (°)."""
        return self._last_angle

    def reset(self) -> None:
        """Remet le PID à zéro (ex: après un arrêt)."""
        self._pid.reset()

    def close(self) -> None:
        self._imu.close()
