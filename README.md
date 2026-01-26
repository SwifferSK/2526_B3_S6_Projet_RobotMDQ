<!-- ===================================================== -->
<!--                        HERO                            -->
<!-- ===================================================== -->

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=230&color=0:0d1117,100:111827&text=Robot%20Suiveur%20de%20Ligne&fontColor=E5E7EB&fontSize=44&fontAlign=50&fontAlignY=36&desc=Hardware%20%E2%80%A2%20Robotics%20%E2%80%A2%20KiCad%20%E2%80%A2%20Raspberry%20Pi&descAlign=50&descAlignY=58" width="100%" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=17&pause=900&center=true&vCenter=true&width=900&lines=Projet+Bachelor+ENSEA+%E2%80%94+Ann%C3%A9e+3;Line+Follower+Robot+%E2%80%A2+IMU+%2B" />
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

<!-- ===================================================== -->
<!--                   PREMIUM KPI CARDS                    -->
<!-- ===================================================== -->

<div align="center">

<table align="center">
  <tr>
    <td width="260" valign="top">
      <h3 align="center">⚡ Focus</h3>
      <p align="center">
        Design PCB<br/>
        Architecture contrôle<br/>
        Intégration capteurs
      </p>
    </td>
    <td width="260" valign="top">
      <h3 align="center">🧠 Capteurs</h3>
      <p align="center">
        IMU (acc + gyro)<br/>
        MCP3208<br/>
        ADC SPI
      </p>
    </td>
    <td width="260" valign="top">
      <h3 align="center">⚙️ Actionneurs</h3>
      <p align="center">
        Moteurs pas à pas<br/>
        Drivers TMC
      </p>
    </td>
    <td width="260" valign="top">
      <h3 align="center">📈 Qualité</h3>
      <p align="center">
        Logging & télémétrie<br/>
        Calibration prévue<br/>
        Sécurités
      </p>
    </td>
  </tr>
</table>

</div>

---

## 🧭 Menu
- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Hardware](#hardware)
- [Software](#software)
- [Dashboards](#dashboards)
- [Demo](#demo)
- [Roadmap](#roadmap)
- [Équipe](#équipe)

---

## Présentation

Ce projet consiste en la conception d’un **robot autonome suiveur de ligne**, orienté **design matériel** et **architecture de contrôle**.

<div align="center">
  <img src="https://progress-bar.dev/38/?title=Avancement%20global&width=720&color=1f2937&suffix=%25" />
</div>

---

## Fonctionnalités

<div align="center">

<table align="center">
  <tr>
    <td width="360" valign="top">
      <h3 align="center">🛤️ Suivi de ligne</h3>
      <p align="center">
        Détection contraste sol/ligne<br/>
        Seuils + calibration<br/>
        Lecture analogique via ADC
      </p>
    </td>
    <td width="360" valign="top">
      <h3 align="center">🧠 Estimation</h3>
      <p align="center">
        IMU (acc + gyro)<br/>
        Filtrage prévu (fusion)<br/>
        Données prêtes pour tuning
      </p>
    </td>
    <td width="360" valign="top">
      <h3 align="center">⚙️ Contrôle</h3>
      <p align="center">
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

<table align="center">
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
        Logging → Analyse → Tuning
      </p>
    </td>
  </tr>
</table>

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

## Software

<div align="center">

<table align="center">
  <tr>
    <td width="540" valign="top">
      <h3 align="center">📦 Modules (prévu)</h3>
      <ul>
        <li><b>acquisition/</b> (IMU + ADC)</li>
        <li><b>filters/</b> (fusion / lissage)</li>
        <li><b>control/</b> (PID + sécurité)</li>
        <li><b>telemetry/</b> (CSV logs + live)</li>
        <li><b>tools/</b> (calibration / tests)</li>
      </ul>
    </td>
    <td width="540" valign="top">
      <h3 align="center">🧪 Qualité</h3>
      <ul>
        <li>Tests subsystem (indépendants)</li>
        <li>Profils config (stable / agressif)</li>
        <li>Arrêt d’urgence + limites d’inclinaison</li>
        <li>Logs “plot-ready” pour tuning</li>
      </ul>
    </td>
  </tr>
</table>

</div>

---

## Dashboards

<p align="center">
  <!-- Stats profil (dark) -->
  <img height="170" src="https://github-readme-stats.vercel.app/api?username=manelbenboujemaa&show_icons=true&hide_border=true&bg_color=0d1117&title_color=e5e7eb&text_color=9ca3af&icon_color=8b5cf6" />
  <img height="170" src="https://github-readme-streak-stats.herokuapp.com/?user=manelbenboujemaa&hide_border=true&background=0D1117&ring=8B5CF6&fire=F59E0B&currStreakLabel=E5E7EB&sideLabels=9CA3AF&dates=6B7280&currStreakNum=E5E7EB&sideNums=E5E7EB" />
</p>

<p align="center">
  <!-- Graphe d’activité (dark) -->
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=manelbenboujemaa&bg_color=0d1117&color=9ca3af&line=8b5cf6&point=f59e0b&area=true&hide_border=true" width="95%"/>
</p>

<p align="center">
  <!-- Option premium si tu actives "github-profile-3d-contrib" : le fichier sera généré dans ton repo -->
  <!-- <img src="profile-3d-contrib/profile-night-green.svg" width="95%" /> -->
</p>

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
  <b>Manel Benboujemaa • Damien THEAS • Quentin Bechler</b><br/>
  <sub>Bachelor ENSEA — Robotique • Design matériel</sub>
</p>
