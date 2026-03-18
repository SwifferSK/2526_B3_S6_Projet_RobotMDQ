"""IMU Fusion — Filtre complémentaire pour l'angle de tangage.

Utilise le gyroscope (intégration) + accéléromètre (valeur absolue) 
via un filtre complémentaire pour estimer l'angle de tangage (pitch).

Usage:
    from imu.imu_fusion import IMUFusion
    imu = IMUFusion()
    angle = imu.get_tilt_angle()   # degrés, 0 = vertical
"""
from __future__ import annotations

import math
import time
import smbus2

# ── Registres LSM6DSOW ────────────────────────────────────────────────────────
_LSM6DSOW_ADDR   = 0x6A
_I2C_BUS         = 1
_CTRL1_XL        = 0x10   # Accel config
_CTRL2_G         = 0x11   # Gyro config
_CTRL3_C         = 0x12   # General config (BDU, auto-incr)
_OUTX_L_G        = 0x22   # Gyro data start (6 bytes)
_OUTX_L_XL       = 0x28   # Accel data start (6 bytes)
_NUM_BYTES       = 6      # NOTE: n'utilise PAS la variable built-in `bytes`

# Config ODR  104 Hz, ±2 g  /  104 Hz, ±245 dps
_ACCEL_CFG  = 0x40 | 0x00  # FQ104HZ | FS_2G
_GYRO_CFG   = 0x40 | 0x00  # FQ_G_104HZ | FS_G_245DPS
_CTRL3_INIT = 0x44          # BDU=1, IF_INC=1

# Facteurs de conversion raw→unité physique
_ACCEL_SCALE = 0.000061     # g/LSB  (±2 g range)
_GYRO_SCALE  = 0.00875      # dps/LSB (±245 dps range)
_G_TO_MS2    = 9.80665

# Fréquence d'échantillonnage IMU (Hz) — doit correspondre à _ACCEL_CFG/_GYRO_CFG
_SAMPLE_RATE = 104.0


class IMUFusion:
    """Filtre complémentaire gyro+accél + filtre passe-bas de sortie.

    Args:
        alpha: Poids du gyroscope dans le filtre complémentaire (0.95–0.99).
        output_beta: Coefficient du filtre passe-bas de sortie (EMA).
                     0.0 = pas de filtrage, 0.5 = attenuation forte des HF.
                     Une valeur de 0.5–0.7 élimine le bruit des vibrations steppers.
        angle_offset: Décalage mécanique à soustraire (calibrer sur sol plat).
        i2c_bus: Bus I2C (1 sur Raspberry Pi).
        address: Adresse I2C du LSM6DSOW (0x6A ou 0x6B).
    """

    def __init__(
        self,
        alpha: float = 0.98,
        output_beta: float = 0.5,
        angle_offset: float = 0.0,
        i2c_bus: int = _I2C_BUS,
        address: int = _LSM6DSOW_ADDR,
    ) -> None:
        self.alpha = float(alpha)
        self.output_beta = float(output_beta)   # EMA de sortie (bruit HF steppers)
        self.angle_offset = float(angle_offset)
        self._bus = smbus2.SMBus(i2c_bus)
        self._addr = address
        self._angle: float = 0.0           # angle brut du filtre complémentaire
        self._filtered_angle: float = 0.0  # angle lissé par EMA de sortie
        self._last_time: float = time.monotonic()

        self._init_sensor()

        # Chauffe le filtre (quelques lectures pour converger)
        for _ in range(20):
            self.get_tilt_angle()

    # ── Initialisation ────────────────────────────────────────────────────────
    def _init_sensor(self) -> None:
        self._bus.write_byte_data(self._addr, _CTRL1_XL, _ACCEL_CFG)
        self._bus.write_byte_data(self._addr, _CTRL2_G,  _GYRO_CFG)
        self._bus.write_byte_data(self._addr, _CTRL3_C,  _CTRL3_INIT)
        time.sleep(0.02)

    # ── Lecture raw ───────────────────────────────────────────────────────────
    def _read_raw(self, reg: int) -> tuple[int, int, int]:
        """Lit 6 registres consécutifs et renvoie (x, y, z) signés 16-bit."""
        data = self._bus.read_i2c_block_data(self._addr, reg, _NUM_BYTES)
        x = _twos_comp((data[1] << 8) | data[0])
        y = _twos_comp((data[3] << 8) | data[2])
        z = _twos_comp((data[5] << 8) | data[4])
        return x, y, z

    def read_accel_g(self) -> tuple[float, float, float]:
        """Accélération en g (ax, ay, az)."""
        x, y, z = self._read_raw(_OUTX_L_XL)
        return x * _ACCEL_SCALE, y * _ACCEL_SCALE, z * _ACCEL_SCALE

    def read_gyro_dps(self) -> tuple[float, float, float]:
        """Vitesse angulaire en degrés/s (gx, gy, gz)."""
        x, y, z = self._read_raw(_OUTX_L_G)
        return x * _GYRO_SCALE, y * _GYRO_SCALE, z * _GYRO_SCALE

    # ── Filtre complémentaire ─────────────────────────────────────────────────
    def get_tilt_angle(self) -> float:
        """Retourne l'angle de tangage (pitch) estimé en degrés.

        Positif = robot penché vers l'avant, négatif = vers l'arrière.
        """
        now = time.monotonic()
        dt = now - self._last_time
        # Clamp dt pour éviter les gros sauts au démarrage
        dt = min(dt, 0.05)
        self._last_time = now

        ax, ay, az = self.read_accel_g()
        gx, gy, gz = self.read_gyro_dps()

        # Angle d'inclinaison depuis l'accéléromètre (degrés)
        # atan2(-ax, az) suppose que az=1 g quand le robot est vertical
        accel_angle = math.degrees(math.atan2(-ax, az))

        # Filtre complémentaire gyro + accél
        self._angle = (
            self.alpha * (self._angle + gy * dt)
            + (1.0 - self.alpha) * accel_angle
        )

        # Filtre EMA de sortie — élimine le bruit haute fréquence des vibrations
        # beta=0 : pas de filtrage   beta=0.7 : lissage fort
        raw = self._angle - self.angle_offset
        self._filtered_angle = (
            self.output_beta * self._filtered_angle
            + (1.0 - self.output_beta) * raw
        )
        return self._filtered_angle

    def calibrate_offset(self, samples: int = 100) -> float:
        """Mesure l'offset mécanique en tenant le robot en position debout.

        Appeler une fois avant la boucle principale et stocker dans ANGLE_OFFSET.
        """
        total = 0.0
        for _ in range(samples):
            total += self.get_tilt_angle()
            time.sleep(0.01)
        self.angle_offset = total / samples
        return self.angle_offset

    def close(self) -> None:
        self._bus.close()


# ── Utilitaire ────────────────────────────────────────────────────────────────
def _twos_comp(val: int, bits: int = 16) -> int:
    """Convertit un entier non-signé en valeur signée (complément à 2)."""
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val
