#  Robot Suiveur de Ligne Auto-Équilibré

Ce projet consiste en la conception et la réalisation d'un robot bipède capable de maintenir son équilibre vertical tout en suivant une ligne tracée au sol. Le cerveau du robot est une **Raspberry Pi Zero 2W**.

##  Fonctionnalités
* **Auto-équilibrage** : Maintien de la position verticale.
* **Suivi de ligne** : Détection du trajet via des photorésistances.

---
##  Structure du Dépôt (Branches)

Le projet est organisé de manière modulaire. La branche `main` contient le système complet, tandis que les branches de développement permettent de tester chaque composant indépendamment :

* **`main`** : Schéma électrique complet,
* **`Kicad_RPI_IMU`** :Schéma électrique de l'**IMU LSM6DSOX**.
* **`Kicad_MCP3208`** : Schéma électrique du **MCP3208** et lecture des photorésistances pour la détection de ligne.
* **`Kicad_TMC2225`** : Schéma électrique de **TMC2225** pour le contrôle des moteurs pas à pas. .
---

##  Matériel (Hardware)

Le robot repose sur les composants suivants :

| Composant | Rôle |
| :--- | :--- |
| **Raspberry Pi Zero 2W** | Unité centrale de traitement (Linux) |
| **IMU LSM6DSOX** | Capteur de mouvement (Accéléromètre + Gyroscope) |
| **MCP3208** | Convertisseur Analogique-Numérique (ADC) |
| **2x TMC2225** | Drivers de moteurs pas à pas (Steppers)  |

---

##  Architecture du Système

### 1. Gestion de l'Équilibre
Le robot utilise l'**IMU LSM6DSOX** pour mesurer l'angle d'inclinaison. Un contrôleur **PID** calcule la correction nécessaire pour que les moteurs se déplacent sous le centre de gravité.

### 2. Détection de Ligne
Les photorésistances sont connectées au **MCP3208**. Ce dernier communique en SPI avec la Raspberry Pi pour fournir des valeurs numériques précises sur l'intensité lumineuse réfléchie par le sol.

### 3. Motorisation
Les drivers **TMC2225** permettent de piloter les moteurs avec une grande résolution (micro-stepping), ce qui est crucial pour éviter les secousses qui pourraient déstabiliser le robot.

---
