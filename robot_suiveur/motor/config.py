
DEGREES_PER_CIRCLE = 360
DIRECTION_FORWARD = 1
DIRECTION_BACKWARD = 0


DEFAULT_STEPS_PER_REV = 200
DEFAULT_MICROSTEP = 16
DEFAULT_SPEED_RPM = 9.375


MOTOR1_STEP_PIN = 12
MOTOR1_DIR_PIN = 16
MOTOR1_DIRECTION = DIRECTION_FORWARD

MOTOR2_STEP_PIN = 13
MOTOR2_DIR_PIN = 6
MOTOR2_DIRECTION = DIRECTION_FORWARD

# ── Limites de vitesse ─────────────────────────────────────────────────────────
# Vitesse maximale en RPM envoyée aux moteurs (±)
MAX_SPEED_RPM: float = 60.0

# ── PID Balance (boucle interne) ───────────────────────────────────────────────
# Ajuster KP en premier (partant de 20, monter jusqu'à oscillation)
# Puis KD pour amortir, enfin KI très petit pour corriger l'offset statique.
BALANCE_KP: float = 30.0
BALANCE_KI: float = 0.5
BALANCE_KD: float = 1.5

# ── PID Ligne (boucle externe) ─────────────────────────────────────────────────
# Error ∈ [-3.5, +3.5], output = steering_offset en RPM ajouté/soustrait
LINE_KP: float = 8.0
LINE_KI: float = 0.0
LINE_KD: float = 0.5

# ── Filtre complémentaire IMU ──────────────────────────────────────────────────
# ALPHA proche de 1 → favorise le gyro (moins de bruit, plus de dérive)
ALPHA: float = 0.98

# Décalage mécanique en degrés (mesuré sur sol plat avec calibrate_offset())
ANGLE_OFFSET: float = 0.0

# Seuil IR pour la détection de la ligne noire (Volts, ADC 3.3 V)
LINE_THRESHOLD: float = 1.5

# Vitesse de recherche quand la ligne est perdue (RPM, rotation sur soi-même)
SEARCH_SPEED_RPM: float = 10.0
