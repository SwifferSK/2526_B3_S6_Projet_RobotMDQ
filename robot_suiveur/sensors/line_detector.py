"""Détection de ligne — sortie continue (erreur pondérée) pour le PID.

CH0-2  : capteurs gauche  (positions -3, -2, -1)
CH3-4  : capteurs centre  (positions -0.5, +0.5)
CH5-7  : capteurs droite  (positions +1, +2, +3)

Convention : ligne détectée quand tension < seuil (THRESHOLD).
L'erreur retournée par get_line_error() vaut :
  -3.5 (ligne très à gauche) … 0 (centré) … +3.5 (ligne très à droite)
  None si aucun capteur ne voit la ligne.
"""
from __future__ import annotations

from .MCP3208 import MCP3208

# Tension (V) en-dessous de laquelle le capteur « voit » la ligne noire.
# Calibrer selon vos capteurs (typiquement 1.0–2.0 V).
THRESHOLD: float = 1.5

# Position physique de chaque canal (CH0..CH7) sur l'axe transversal.
# Négatif = gauche, positif = droite.
_POSITIONS: list[float] = [-3.0, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, 3.0]


def get_line_error(
    adc: MCP3208, threshold: float = THRESHOLD
) -> tuple[float | None, list[float]]:
    """Calcule l'erreur de position de la ligne par barycentre pondéré.

    Returns:
        (error, readings) :
          error   — Float dans [-3.5, +3.5] si au moins un capteur voit la ligne,
                    None sinon (ligne perdue).
          readings — Liste des 8 tensions lues (réutilisable pour l'affichage).
    """
    readings = adc.read_all_channels()

    weighted_sum = 0.0
    total_weight = 0.0

    for ch, voltage in enumerate(readings):
        if voltage < threshold:
            # Poids inversement proportionnel à la tension (plus noir = plus fort)
            w = threshold - voltage
            weighted_sum += _POSITIONS[ch] * w
            total_weight += w

    if total_weight == 0.0:
        return None, readings  # Aucun capteur actif

    return weighted_sum / total_weight, readings


def detect_line(adc: MCP3208, threshold: float = THRESHOLD, *, verbose: bool = True) -> str:
    """Compatibilité avec l'ancien code — retourne 'left'/'center'/'right'/'none'."""
    error, readings = get_line_error(adc, threshold)

    if error is None:
        pos = "none"
        err_str = "None"
    elif error < -0.5:
        pos = "left"
        err_str = f"{error:.2f}"
    elif error > 0.5:
        pos = "right"
        err_str = f"{error:.2f}"
    else:
        pos = "center"
        err_str = f"{error:.2f}"

    if verbose:
        # Réutilise les readings déjà lus — pas de double lecture ADC
        print(
            " | ".join(f"CH{i}:{v:.2f}V" for i, v in enumerate(readings)),
            f"-> err={err_str} -> {pos}",
        )

    return pos
