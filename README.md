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
  <a href="#demo">
    <img src="https://img.shields.io/badge/Demo-%C3%80%20venir-111827?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-In%20Progress-F59E0B?style=for-the-badge&logo=clock&logoColor=white" />
  <img src="https://img.shields.io/badge/KiCad-9.0.7-2563EB?style=for-the-badge&logo=kicad&logoColor=white" />
  <img src="https://img.shields.io/badge/Type-Robotics-374151?style=for-the-badge&logo=gear&logoColor=white" />
  <img src="https://img.shields.io/badge/Plateforme-RPi%20Zero%202W-111827?style=for-the-badge&logo=raspberrypi&logoColor=white" />
</p>

---

## 🧭 Menu
- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Hardware](#hardware)
- [Dashboards](#dashboards)
- [Demo](#demo)
- [Roadmap](#roadmap)
- [Équipe](#équipe)

---

## Présentation

Ce projet consiste en la conception d’un **robot autonome suiveur de ligne bipede** 

<br>
L'obectif est donc de faire un robot capable de suive une ligne tout en restant stable 
La travail a fournir est une carte electronique,un driver unique capable de gerer tout les fonctions du robot et une boitier 3D.
<br><br>
---

## Fonctionnalités
<div align="center">
  <table align="center" cellspacing="0" cellpadding="14">
    <tr>
      <td width="300" align="center" valign="top">
        <h3>🛤️ Suivi de ligne</h3>
        <p>
          Détection contraste sol/ligne<br/>
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
    <td>Drivers moteurs</td>
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


## 👥 Contributors

<div align="center">

<!-- Image contributors automatique (super clean & centré) -->
<img src="https://contrib.rocks/image?2526_B3_S6_Projet_RobotMDQ=SwifferSK/2526_B3_S6_Projet_RobotMDQ" width="92%" alt="Contributors"/>
<p>
  <a href="https://github.com/SwifferSK/2526_B3_S6_Projet_RobotMDQ/graphs/contributors">
    <img src="https://img.shields.io/badge/Voir%20la%20liste%20compl%C3%A8te-GitHub-111827?style=for-the-badge&logo=github&logoColor=white" />
  </a>
</p>

</div>

---

## Demo

<p align="center">
  <img src="https://img.shields.io/badge/Demo-%C3%80%20venir-111827?style=for-the-badge" />
</p>

<p align="center">
  <!-- Quand tu l’as : -->
  <!-- <img src="assets/demo.gif" width="820" alt="Demo GIF" /> -->
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
