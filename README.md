<!-- ===================================================== -->
<!--                        HERO                            -->
<!-- ===================================================== -->

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=230&color=0:0d1117,100:111827&text=Robot%20Suiveur%20de%20Ligne&fontColor=E5E7EB&fontSize=44&fontAlign=50&fontAlignY=36&desc=Manel%20%E2%80%A2%20Damien%20%E2%80%A2%20Quentin%20%" width="100%" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=17&pause=900&center=true&vCenter=true&width=900&lines=Projet+Bachelor+ENSEA+%E2%80%94+Ann%C3%A9e+3;Line+Follower+Robot%E2%80%A2" />
</p>

<!-- ===================================================== -->
<!--                       BADGES                           -->
<!-- ===================================================== -->

<p align="center">
  <a href="https://discord.gg/eySWAjkd">
    <img src="https://img.shields.io/badge/Discord-Bachelor%20ENSEA-5865F2?style=for-the-badge&logo=discord&logoColor=white" />
  </a>

  <a href="https://www.youtube.com">
    <img src="https://img.shields.io/badge/Demo-%C3%80%20venir-111827?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-In%20Progress-F59E0B?style=for-the-badge&logo=clock&logoColor=white" />

  <a href="https://www.kicad.org">
    <img src="https://img.shields.io/badge/KiCad-9.0.7-2563EB?style=for-the-badge&logo=kicad&logoColor=white" />
  </a>

  <img src="https://img.shields.io/badge/Type-Robotics-374151?style=for-the-badge&logo=gear&logoColor=white" />

  <a href="https://www.raspberrypi.com">
    <img src="https://img.shields.io/badge/Plateforme-RPi%20Zero%202W-111827?style=for-the-badge&logo=raspberrypi&logoColor=white" />
  </a>
</p>

---
## 🧭 Menu
- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Structure du dépôt](#structure-du-dépôt-branches)
- [Architecture](#architecture)
- [Hardware](#hardware)
- [Dashboard](#dashboard)
- [Demo](#demo)
- [Équipe](#équipe)

---

## Présentation

                              

Ce projet consiste à concevoir un **robot autonome bipède** capable de suivre une ligne tracée au sol.        

Le robot utilise ses **capteurs** pour comprendre sa position et ajuste en permanence ses **moteurs** afin de ne pas tomber pendant le déplacement.

L’ensemble du système est contrôlé par une **Raspberry Pi Zero 2W**, qui traite les informations et prend les décisions en temps réel.




---

## Fonctionnalités
<div align="center">
  <table align="center" cellspacing="0" cellpadding="14">
    <tr>
      <td width="300" align="center" valign="top">
        <h3>🛤️ Suivi de ligne</h3>
        <p>
          Détection du trajet via des photorésistances/ligne<br/>
          Seuils + calibration<br/>
          Lecture analogique via ADC
        </p>
      </td>
      <td width="300" align="center" valign="top">
        <h3>🧠 Stabilisation </h3>
        <p>
          IMU (acc + gyro)<br/>
          Filtrage <br/>
          Donnée envoyer en I2C au MCU<br/>
        </p>
      </td>
      <td width="300" align="center" valign="top">
        <h3>⚙️ Contrôle</h3>
        <p>
          Boucle temps réel (PID prévu)<br/>
          Commande moteurs fluide<br/>
          Sécurités (tilt / cutoff)
        </p>
      </td>
    </tr>
  </table>
</div>

---
##  Structure du Dépôt (Branches)

Le projet est organisé de manière modulaire. La branche `main` contient le système complet, tandis que les branches de développement permettent de tester chaque composant indépendamment :

* **`main`** : Schéma électrique complet,
* **`Kicad_RPI_IMU`** :Schéma électrique de l'**IMU LSM6DSOX**.
* **`Kicad_MCP3208`** : Schéma électrique du **MCP3208** et lecture des photorésistances pour la détection de ligne.
* **`Kicad_TMC2225`** : Schéma électrique de **TMC2225** pour le contrôle des moteurs pas à pas. .
* **`merged-code`** : Fusion des 3 firmwares.
* **`Firmware_MCP3208`** : Firmmware du **MCP3208**.
* **`Firmware_LSM6DSOX`** :Firmmware du l'**IMU LSM6DSOX**.
* **`Firmware_TMC2225`** : Firmmware du **TMC2225** .
---

## Architecture

<div align="center">


  <tr>
    <td width="540" valign="top">
      <h3 align="center">🔌 Chaîne matérielle</h3>
      <p align="center">
        Capteurs optiques → <b>MCP3208 (ADC)</b><br/>
        IMU → <b>I2C/SPI</b> → <b>Raspberry Pi Zero 2W</b><br/>
        RPi → <b>GPIO</b> → <b>TMC2225</b> → Moteurs pas à pas
      </p>
    </td>
    <td width="540" valign="top">
      <h3 align="center">🧠 Chaîne de contrôle</h3>
      <p align="center">
        Acquisition → Filtrage → Estimation<br/>
        Contrôle (PID) → Commande moteurs<br/>
      </p>
    </td>
  </tr>


</div>

---

## Hardware

<div align="center">

<table align="center">
  <tr>
    <th align="left">Composant</th>
    <th align="left">Rôle</th>
    <th align="left">Interface</th>
  </tr>
  <tr>
    <td><b>Raspberry Pi Zero 2W</b></td>
    <td>Contrôleur principal</td>
    <td>GPIO / SPI / I2C</td>
  </tr>
  <tr>
    <td><b>LSM6DSOX</b></td>
    <td>IMU (acc + gyro)</td>
    <td>I2C / SPI</td>
  </tr>
  <tr>
    <td><b>MCP3208</b></td>
    <td>Convertisseur ADC</td>
    <td>SPI</td>
  </tr>
  <tr>
    <td><b>TMC2225 (x2)</b></td>
    <td>Drivers moteurs pas à pas</td>
    <td>STEP / DIR</td>
  </tr>
  <tr>
    <td><b>Capteurs optiques</b></td>
    <td>Détection de ligne</td>
    <td>Analogique</td>
  </tr>
</table>

</div>

---

## Dashboard
<div align="center">


<p align="center">
  <a href="https://github.com/SwifferSK/2526_B3_S6_Projet_RobotMDQ/issues">
    <img src="https://img.shields.io/github/issues/SwifferSK/2526_B3_S6_Projet_RobotMDQ?style=for-the-badge&label=Issues&color=111827" />
  </a>
  <a href="https://github.com/SwifferSK/2526_B3_S6_Projet_RobotMDQ/commits/main">
    <img src="https://img.shields.io/github/last-commit/SwifferSK/2526_B3_S6_Projet_RobotMDQ?style=for-the-badge&label=Last%20commit&color=111827" />
  </a>
</p>


  </a>
  <a href="https://github.com/SwifferSK/2526_B3_S6_Projet_RobotMDQ/releases">
    <img src="https://img.shields.io/github/v/release/SwifferSK/2526_B3_S6_Projet_RobotMDQ?include_prereleases=true&style=for-the-badge&label=Release&color=0d1117" />
  </a>
  <a href="https://github.com/SwifferSK/2526_B3_S6_Projet_RobotMDQ">
    <img src="https://img.shields.io/github/languages/top/SwifferSK/2526_B3_S6_Projet_RobotMDQ?style=for-the-badge&label=Top%20lang&color=0d1117" />
  </a>
</p>

<table align="center">
  <tr>
    <td align="center" width="520">
      <img src="https://repobeats.axiom.co/api/embed/d7c7f47506a43028bca250a53c7e58a2328f7b16.svg" alt="RepoBeats" width="100%"/>
    </td>
   
  </tr>
</table>

</div>

---

## Demo

<p align="center">
  <img src="https://img.shields.io/badge/Demo-%C3%80%20venir-111827?style=for-the-badge" />
</p>

<p align="center">
  <!-- <img src="assets/demo.gif" width="820" alt="Demo" /> -->
</p>

---

## Équipe

<p align="center">
  <img src="ban.jpg" width="100%" />
</p>
<p align="center">
  <b> Damien Theas • Manel Benboujemaa  • Quentin Bechler</b><br/>
  <sub>Bachelor ENSEA — Robotique • Design matériel</sub>
</p>
