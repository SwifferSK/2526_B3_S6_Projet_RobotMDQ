# Robot suiveur de ligne (Raspberry Pi + MCP3208 + STEP/DIR)

## Structure

- `main.py` : le seul fichier à lancer
- `sensors/` : lecture MCP3208 + détection de la position de la ligne
- `motor/` : pilotage des moteurs pas-à-pas (STEP/DIR)
- `imu/` : (optionnel) ton driver LSM6DSO(X) rangé à part

## Lancer

Depuis le dossier `robot_suiveur/` :

```bash
python3 main.py
```

## Réglages importants

Dans `main.py` :

- `THRESHOLD` : seuil de détection (souvent ligne noire => tension plus basse)
- `FORWARD_ANGLE`, `TURN_ANGLE` : taille des corrections

Si ton robot oscille trop : baisse `FORWARD_ANGLE` et `TURN_ANGLE`.

## Câblage (rappel)

### MCP3208 -> Raspberry Pi (SPI0 / CE0)
- MOSI : GPIO10 (pin 19)
- MISO : GPIO9  (pin 21)
- SCLK : GPIO11 (pin 23)
- CE0  : GPIO8  (pin 24)
- 3.3V : pin 1
- GND  : pin 6

Les capteurs se branchent sur CH0..CH7 du MCP3208.
