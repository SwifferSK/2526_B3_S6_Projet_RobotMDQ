# CONTEXT — Robot Bipède Suiveur de Ligne Auto-Stable

> Ce fichier est le **référentiel de contexte** pour toutes les sessions IA futures.  
> Mettre à jour après chaque modification matérielle ou logicielle importante.

---

## Objectif du projet

Construire un robot bipède (2 roues) qui :
1. **Suit une ligne noire** sur fond blanc (8 capteurs IR)
2. **Se stabilise seul** grâce à une IMU (filtre complémentaire + PID cascade)

Plateforme cible : **Raspberry Pi Zero 2W** — Python 3, pas d'Arduino.

---

## Architecture logicielle

```
Capteurs IR (MCP3208 SPI) ──►  PID Ligne  ──►  steer_cmd (RPM)
                                                      │
IMU (LSM6DSOW I2C) ────────►  PID Balance ──►  speed_cmd (RPM)
                                                      │
                              speed_left  = speed_cmd + steer_cmd
                              speed_right = speed_cmd - steer_cmd
                                                      │
                              Moteurs (TMC2225 STEP/DIR via GPIO)
```

**3 boucles imbriquées :**

| Boucle | Capteur | Fréquence | Sortie |
|--------|---------|-----------|--------|
| **Balance** (interne) | IMU (gyro+accél) | ~100 Hz | `speed_cmd` RPM |
| **Ligne** (externe) | 8× IR / MCP3208 | ~20–50 Hz | `steer_cmd` RPM |
| *(optionnel)* **Vitesse** | (encodeurs absents) | — | — |

---

## Hardware

### Raspberry Pi Zero 2W
- **OS** : Raspberry Pi OS Lite (64-bit recommandé)
- **I2C bus 1** : SDA=GPIO 2, SCL=GPIO 3
- **SPI bus 0** : MOSI=GPIO 10, MISO=GPIO 9, CLK=GPIO 11, CE0=GPIO 8
- Activer I2C et SPI via `raspi-config`

### Moteurs — TMC2225 (STEP/DIR)

| Paramètre | Valeur |
|-----------|--------|
| Moteur 1 (gauche) — STEP | GPIO **12** |
| Moteur 1 (gauche) — DIR | GPIO **16** |
| Moteur 2 (droite) — STEP | GPIO **13** |
| Moteur 2 (droite) — DIR | GPIO **6** |
| Pas/tour | 200 (moteur) |
| Microstepping | ×16 → **3 200 µpas/tour** |
| Vitesse defaut | 9.375 RPM |
| Vitesse max | 60 RPM (réglable dans `config.py`) |

> **Convention de direction** :
> - Moteur 1 (gauche) = `DIRECTION_FORWARD`
> - Moteur 2 (droite) = `DIRECTION_BACKWARD` ⚠️ — monté en miroir, doit être inversé
> - Vitesse négative ⇒ le driver inverse automatiquement la direction.

### Capteurs IR — MCP3208 (ADC 12 bits, SPI)

8 capteurs sur CH0..CH7 à 3.3 V :

| Canal | Position | Position normalisée |
|-------|----------|---------------------|
| CH0 | Très gauche | -3.0 |
| CH1 | Gauche | -2.0 |
| CH2 | Gauche proche | -1.0 |
| CH3 | Centre gauche | -0.5 |
| CH4 | Centre droite | +0.5 |
| CH5 | Droite proche | +1.0 |
| CH6 | Droite | +2.0 |
| CH7 | Très droite | +3.0 |

- **Ligne noire** détectée quand la tension est **< THRESHOLD** (défaut 1.5 V)
- `get_line_error()` retourne un barycentre pondéré ∈ [-3.5, +3.5] (0 = centré)
- `None` si aucun capteur ne détecte la ligne

### IMU — LSM6DSOW (I2C)

| Paramètre | Valeur |
|-----------|--------|
| Adresse I2C | `0x6A` (SA0 = GND) ou `0x6B` |
| Bus | I2C 1 |
| ODR | 104 Hz |
| Accéléromètre | ±2 g → scale 0.000061 g/LSB |
| Gyroscope | ±245 dps → scale 0.00875 dps/LSB |
| Axe de tangage (pitch) | **axe Y du gyro**, `-ax` et `az` pour l'accél |

**Filtre complémentaire** :
```
angle = α × (angle + gy × dt) + (1-α) × atan2(-ax, az)
```
`ALPHA = 0.98` par défaut.

---

## Structure du projet (branche `Merge-codeV2`)

```
robot_suiveur/
├── main.py                    # ancien suiveur de ligne (référence)
├── main_imu.py                # ancien test IMU (référence)
├── main_balance_line.py       # ✅ POINT D'ENTRÉE PRINCIPAL
│
├── imu/
│   ├── drv_lsm6dsow.py        # driver bas niveau (bugs connus, ne pas utiliser seul)
│   ├── imu_fusion.py          # ✅ filtre complémentaire — à utiliser
│   └── setting.py             # constantes registres LSM6DSOW
│
├── sensors/
│   ├── MCP3208.py             # driver SPI ADC
│   └── line_detector.py       # ✅ get_line_error() + detect_line() (compat.)
│
├── motor/
│   ├── config.py              # ✅ TOUS les paramètres réglables ici
│   ├── driver.py              # driver TMC2225 STEP/DIR (threading)
│   ├── controller.py          # DualMotorController
│   └── utils.py               # utilitaires moteur
│
└── control/
    ├── pid.py                 # ✅ PID générique avec anti-windup
    └── balance_controller.py  # ✅ boucle de balance (IMU + PID)
```

---

## Paramètres réglables — `motor/config.py`

```python
MAX_SPEED_RPM  = 40.0    # vitesse max moteurs (RPM) — à augmenter progressivement

# PID Balance (boucle interne — AJUSTER EN PREMIER)
# ⚠️ Commencer PETIT — KP=30 sur des steppers Python → vibrations !
BALANCE_KP     = 5.0     # point de départ sûr, monter par pas de 1-2
BALANCE_KI     = 0.0     # garder à 0 pendant le réglage KP/KD
BALANCE_KD     = 0.8

# PID Ligne (boucle externe)
LINE_KP        = 8.0
LINE_KI        = 0.0
LINE_KD        = 0.5

ALPHA          = 0.98    # filtre complémentaire IMU
ANGLE_OFFSET   = 0.0     # offset mécanique (°) — mesurer avec --calibrate
LINE_THRESHOLD = 1.5     # seuil détection ligne (V)
SEARCH_SPEED_RPM = 8.0  # vitesse rotation quand ligne perdue
```

---

## Commandes de démarrage

```bash
# 1. Calibrer l'IMU (une seule fois, robot en position verticale)
python3 main_balance_line.py --calibrate
# → note la valeur, mets-la dans ANGLE_OFFSET dans config.py

# 2. Tester la balance seule
python3 main_balance_line.py --balance

# 3. Mode complet (balance + suivi de ligne)
python3 main_balance_line.py
```

---

## Procédure de réglage PID

> Toujours régler la **balance d'abord**, la ligne ensuite.

### PID Balance

| Étape | Action |
|-------|--------|
| 1 | `KI=0, KD=0` — monter `KP` jusqu'aux oscillations |
| 2 | Réduire `KP` de 20 % |
| 3 | Monter `KD` pour amortir |
| 4 | Ajouter `KI` en petit (0.1–1.0) pour corriger le drift |

### PID Ligne

| Étape | Action |
|-------|--------|
| 1 | `KI=0, KD=0` — monter `KP` jusqu'au suivi sans oscillation |
| 2 | Ajouter `KD` pour stabiliser dans les virages |

---

## Affichage télémétrie en temps réel

`main_balance_line.py` affiche une ligne qui se rafraîchit à ~10 Hz :

```
[BAL] Angle= +2.34°  PID_out= +11.7RPM  Steer= +0.0  L= +11.7RPM  R= +11.7RPM  LINE_ERR=None  dt=10.1ms  Hz=99
```

| Colonne | Signification |
|---------|---------------|
| `Angle` | Angle de tangage IMU (° — 0 = vertical) |
| `PID_out` | Sortie du PID balance (RPM de base) |
| `Steer` | Correction de cap (ligne) en RPM |
| `L` / `R` | Vitesse réelle envoyée à chaque moteur |
| `LINE_ERR` | Erreur de position ligne [-3.5, +3.5] ou None |
| `dt` | Durée du dernier cycle de boucle (ms) |
| `Hz` | Fréquence réelle de la boucle de contrôle |

---

## Dépannage fréquent

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| Les roues tournent en sens opposés | `MOTOR2_DIRECTION` mal configuré | Mettre `MOTOR2_DIRECTION = DIRECTION_BACKWARD` |
| Vibrations / oscillations rapides | `BALANCE_KP` trop élevé | Réduire KP — commencer à 3–5 pour des steppers Python |
| Robot tombe toujours vers l'avant/arrière | `ANGLE_OFFSET` non calibré | Lancer `--calibrate`, mettre la valeur dans `config.py` |
| Robot part toujours dans le même sens | Mauvais axe de tangage IMU | Vérifier orientation physique du LSM6DSOW, ajuster l'axe dans `imu_fusion.py` (`gy` → peut être `gx` ou `-gy`) |
| Fréquence boucle < 50 Hz (Hz affiché) | I2C/SPI trop lents ou sleep() trop long | Réduire `ALPHA` (0.95), désactiver verbose dans les capteurs |

---

## Bugs connus (déjà corrigés)

| Bug | Fichier | Correction |
|-----|---------|------------|
| `time_delay = 1` → boucle à 1 Hz | `imu/setting.py` | Non utilisé dans `imu_fusion.py` |
| `read_i2c_block_data(addr, reg, bytes)` — shadowing builtin `bytes` | `imu/drv_lsm6dsow.py` | Renommé `_NUM_BYTES = 6` |
| Détection IR binaire → PID peu efficace | `sensors/line_detector.py` | Barycentre pondéré continu |
| Double lecture ADC dans `detect_line` verbose | `sensors/line_detector.py` | Réutilisation des readings déjà lus |
| `f"{error:.2f}"` crash si error=None | `sensors/line_detector.py` | `err_str` géré séparément |
| `import sys` inutilisé | `main_balance_line.py` | Supprimé |
| `last_time` non reset après chute → dt énorme | `main_balance_line.py` | Reset explicite après `time.sleep()` |
| `MOTOR2_DIRECTION = DIRECTION_FORWARD` → roues opposées | `motor/config.py` | Changé en `DIRECTION_BACKWARD` |
| `BALANCE_KP=30` → vibrations sur steppers Python | `motor/config.py` | Réduit à 5.0 (point de départ sûr) |


---

## Dépendances Python

```bash
pip3 install smbus2 spidev RPi.GPIO
```

---

## Historique des sessions IA

| Date | Sujet |
|------|-------|
| 2026-03-17 | Implémentation du suiveur de ligne de base (`main.py`) |
| 2026-03-17–18 | Réécriture du système de balance (PID + IMU) |
| 2026-03-18 | ✅ Intégration balance + suivi de ligne (PID cascadé, `main_balance_line.py`) |
| 2026-03-18 | 🔧 Fix direction moteur 2, réduction KP, ajout télémétrie temps réel |

