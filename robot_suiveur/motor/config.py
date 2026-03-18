
DEGREES_PER_CIRCLE = 360
DIRECTION_FORWARD = 1
DIRECTION_BACKWARD = 0


DEFAULT_STEPS_PER_REV = 200
DEFAULT_MICROSTEP = 16
DEFAULT_SPEED_RPM = 9.375


MOTOR1_STEP_PIN = 12
MOTOR1_DIR_PIN = 16
MOTOR1_DIRECTION = DIRECTION_FORWARD   # moteur gauche

MOTOR2_STEP_PIN = 13
MOTOR2_DIR_PIN = 6
# ⚠️  Le moteur droit est monté en miroir → direction inversée pour aller "en avant"
MOTOR2_DIRECTION = DIRECTION_BACKWARD

# ── Limites de vitesse ─────────────────────────────────────────────────────────
MAX_SPEED_RPM: float = 40.0   # réduit pour débuter — monter progressivement

# ── PID Balance (boucle interne) ───────────────────────────────────────────────
# ⚠️  Commencer TOUJOURS avec KI=0, KD=0 puis monter KP doucement depuis 3.
# Montée typique : 3 → 5 → 8 → 10 → 12 (selon le robot).
# Dès que ça oscille, revenir en arrière de 20 %.
BALANCE_KP: float = 5.0    # ← point de départ sûr pour des moteurs pas-à-pas
BALANCE_KI: float = 0.0    # ← garder à 0 pendant le réglage de KP/KD
BALANCE_KD: float = 0.8

# ── PID Ligne (boucle externe) ─────────────────────────────────────────────────
LINE_KP: float = 8.0
LINE_KI: float = 0.0
LINE_KD: float = 0.5

# ── Filtre complémentaire IMU ──────────────────────────────────────────────────
ALPHA: float = 0.98

# Décalage mécanique en degrés (mesurer avec --calibrate sur sol plat)
ANGLE_OFFSET: float = 0.0

# Seuil IR pour la détection de la ligne noire (Volts)
LINE_THRESHOLD: float = 1.5

# Vitesse de rotation quand la ligne est perdue
SEARCH_SPEED_RPM: float = 8.0
