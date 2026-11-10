<h1 align="center">
    <a href="https://spacelab.ufsc.br"><img src="_static/spacelab-logo.png" alt="SpaceLab" width="40%"></a>
    <br>
    PERSISTENT-1 MISSION
    <br>
</h1>

<h4 align="center">A compilation of the Persistent-1 mission documents, diagrams and figures.</h4>

<p align="center">
    <a href="https://github.com/spacelab-ufsc/spacelab#versioning">
        <img src="https://img.shields.io/badge/status-in%20development-red?style=for-the-badge">
    </a>
    <a href="#license">
        <img src="https://img.shields.io/badge/open--source-project-lightgray?style=for-the-badge">
    </a>
    <a href="http://ufsc.br">
        <img src="https://img.shields.io/badge/sourced%20by-UFSC-orange?style=for-the-badge">
    </a>
    <a href="https://github.com/spacelab-ufsc/persistent1-doc/actions">
        <img src="https://img.shields.io/github/actions/workflow/status/spacelab-ufsc/persistent1-doc/doc_build.yml?branch=dev&style=for-the-badge">
    </a>
</p>

<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#mission-statement">Statement</a> •
    <a href="#mission-objectives">Objectives</a> •
    <a href="#building-the-documentation">Building</a> •
    <a href="#license">License</a>
</p>

## Overview

Persistent-1 is a 3U CubeSat developed by SpaceLab at the Federal University of Santa Catarina (UFSC). Its main technological payload is the Reliability Enhanced Electrical Power System (RE²PS), an EPS module designed to increase the reliability of power systems for CubeSats without compromising their energy efficiency.

The spacecraft is divided into a 1U sector, containing the service module (based on the FloripaSat-2 platform: EPS 2.0, OBDH 2.0 and TTC 2.0) and INPE's Environmental Data Collector (EDC) payload, and a 2U sector dedicated to the RE²PS payload, the SLCAM camera, an OBDH 2.0 and the TMTC 3.0 module.

This repository contains the sources of the mission documentation (Critical Design Review), written in reStructuredText and built with [Sphinx](https://www.sphinx-doc.org/) into an HTML page and a PDF document.

## Mission Statement

The Persistent-1 mission aims to test in a space environment an EPS module designed for small satellites, and primarily composed of fully analog circuits, along with other subsystems and techniques to enhance the reliability and durability of electronic circuits operating in space.

## Mission Objectives

1. Develop a reliable and efficient EPS for CubeSats up to 6U.
2. Validate the new EPS under representative mission conditions.
3. Strengthen national space capabilities.

## Building the Documentation

### Dependencies

* Python 3 and the packages listed in `requirements.txt`:

```
pip install sphinx -r requirements.txt
```

* For the PDF output: `latexmk` and a TeX Live distribution (`texlive-latex-extra`, `texlive-fonts-extra`, ...).

### HTML page

```
make html
```

The output is generated in `_build/html/`.

### PDF document

```
make latexpdf
```

The output is generated in `_build/latex/`.

## License

The SpaceLab follows a strong open-source approach in order to encourage and promote knowledge. This documentation is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). Firmware and hardware sources of each module are available in their respective repositories, under their specific licenses.
