"""Contrôleur de balance — boucle interne pour maintenir le robot debout.

Lit l'IMU, calcule la commande de vitesse (RPM) via PID,
et retourne (speed_base, steering) à la boucle principale.

Usage:
    from control.balance_controller import BalanceController
    bc = BalanceController()
    speed_base = bc.update(dt)
"""
from __future__ import annotations

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
        kp: float = 30.0,
        ki: float = 0.5,
        kd: float = 1.5,
        max_speed: float = 60.0,
        angle_offset: float = 0.0,
        alpha: float = 0.98,
    ) -> None:
        self._imu = IMUFusion(alpha=alpha, angle_offset=angle_offset)
        self._pid = PID(
            kp=kp,
            ki=ki,
            kd=kd,
            out_min=-max_speed,
            out_max=max_speed,
        )
        self.max_speed = max_speed
        self._last_angle: float = 0.0

    # ── Interface publique ────────────────────────────────────────────────────
    def update(self, dt: float) -> float:
        """Met à jour la boucle de balance.

        Args:
            dt: Temps écoulé depuis le dernier appel (secondes).

        Returns:
            Commande de vitesse de base en RPM.
            Positif = avancer, négatif = reculer.
        """
        angle = self._imu.get_tilt_angle()
        self._last_angle = angle
        # setpoint = 0 ° (robot vertical)
        speed_cmd = self._pid.compute(error=angle, dt=dt)
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
