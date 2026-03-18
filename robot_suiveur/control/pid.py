"""PID Controller générique avec anti-windup.

Usage:
    from control.pid import PID
    pid = PID(kp=30.0, ki=0.5, kd=1.5, out_min=-60, out_max=60)
    output = pid.compute(error=angle, dt=0.01)
"""
from __future__ import annotations


class PID:
    """Contrôleur PID standard avec anti-windup par saturation de l'intégrale.

    Args:
        kp: Gain proportionnel.
        ki: Gain intégral.
        kd: Gain dérivé.
        out_min: Limite basse de la sortie.
        out_max: Limite haute de la sortie.
        integral_limit: Limite de l'intégrale (anti-windup). Si None, dérivé
                        de out_min/out_max.
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        out_min: float = -100.0,
        out_max: float = 100.0,
        integral_limit: float | None = None,
    ) -> None:
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        self.out_min = float(out_min)
        self.out_max = float(out_max)
        self._integral_limit = float(integral_limit) if integral_limit is not None else abs(out_max)

        self._integral: float = 0.0
        self._prev_error: float = 0.0

    # ── Interface publique ────────────────────────────────────────────────────
    def compute(self, error: float, dt: float) -> float:
        """Calcule la commande PID pour l'erreur et le pas de temps donnés.

        Args:
            error: Erreur actuelle (setpoint - mesure).
            dt:    Pas de temps en secondes depuis le dernier appel.

        Returns:
            Commande saturée entre out_min et out_max.
        """
        if dt <= 0:
            return 0.0

        # Terme proportionnel
        p = self.kp * error

        # Terme intégral avec anti-windup (saturation)
        self._integral += error * dt
        self._integral = _clamp(self._integral, -self._integral_limit, self._integral_limit)
        i = self.ki * self._integral

        # Terme dérivé (sur l'erreur, pas sur la mesure)
        d = self.kd * (error - self._prev_error) / dt
        self._prev_error = error

        output = p + i + d
        return _clamp(output, self.out_min, self.out_max)

    def reset(self) -> None:
        """Remet à zéro l'intégrale et l'erreur précédente (ex: après une pause)."""
        self._integral = 0.0
        self._prev_error = 0.0

    def set_gains(self, kp: float, ki: float, kd: float) -> None:
        """Met à jour les gains à chaud."""
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)

    def __repr__(self) -> str:
        return (
            f"PID(kp={self.kp}, ki={self.ki}, kd={self.kd}, "
            f"out=[{self.out_min}, {self.out_max}])"
        )


# ── Utilitaire ────────────────────────────────────────────────────────────────
def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
