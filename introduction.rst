.. introduction.rst

    Copyright The Persistent-1 Contributors.

    Persistent-1 Documentation

    This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
    International License. To view a copy of this license,
    visit http://creativecommons.org/licenses/by-sa/4.0/.

.. _ch:introduction:

************
Introduction
************

The FloripaSat-1 and FloripaSat-2 platforms were developed to facilitate the development of CubeSats. While FloripaSat-1 marked the pioneering use of this platform, FloripaSat-2 served as the basis for other missions, such as GOLDS-UFSC, Constelação Catarina and Aldebaran-1. However, it is important to note that these platforms were not initially designed with a focus on tolerance to radiation effects or reliability, with some internal redundancies. Their main objective was to offer functionality and practicality. In applications that demand greater reliability and robustness, it is necessary to employ a different set of subsystems to make up the service module. In this context, the development of a new EPS for this platform, the Reliability Enhanced Electrical Power System (RE²PS), was initiated, as the EPS is known to be the subsystem most susceptible to failure in systems based on CubeSats. To ensure its proper evaluation, OBDH and TMTC systems are also being developed to comprehensively integrate this new platform.

Mission Description
===================

Mission Statement
-----------------

Approved in the event of Mission Definition Review (MDR), the mission statement for Persistent-1 is as follows:

.. epigraph::

   The Persistent-1 mission aims to test in a space environment an EPS module designed for small satellites, and primarily composed of fully analog circuits, along with other subsystems and techniques to enhance the reliability and durability of electronic circuits operating in space.

The EPS module referred to in the mission statement is the RE²PS.

.. _sec:mission_objectives:

Mission objectives
------------------

:numref:`tab:eps-goals-objectives` describes the goals and objectives of the EPS development project.

.. _tab:eps-goals-objectives:

.. list-table:: Goals and objectives of the EPS development project.
   :header-rows: 1
   :widths: 8 37 10 45

   * - ID
     - **Goal**
     - ID
     - **Objective**
   * - G.1
     - Develop a reliable and efficient EPS for CubeSats up to 6U
     - O.1.1
     - Define the EPS requirements for typical LEO missions with a minimum lifetime of 12 months
   * - 
     - 
     - O.1.2
     - Analyze the FloripaSat EPS and identify opportunities for improvement
   * - 
     - 
     - O.1.3
     - Design, manufacture, and test the new EPS
   * - G.2
     - Validate the new EPS under representative mission conditions
     - O.2.1
     - Integrate the new EPS into the FloripaSat platform for functional validation
   * - 
     - 
     - O.2.2
     - Validate the EPS in an environmental data collection satellite
   * - G.3
     - Strengthen national space capabilities
     - O.3.1
     - Promote national space technology, industry, and human resource development

Project Members
---------------

The project involves a multidisciplinary team comprising students, professors, and researchers from the Federal University of Santa Catarina (UFSC).

.. _tab:team-members:

.. list-table:: Contributions of team members.
   :header-rows: 1

   * - **Name**
     - **Contribution**
     - **Institution**
     - **Position**
   * - Eduardo Augusto Bezerra
     - Project management
     - UFSC
     - Professor
   * - Adroaldo Raizer
     - Technical Advisor
     - UFSC
     - Professor
   * - Anderson Wedderhoff Spengler
     - Technical Advisor
     - UFSC
     - Professor
   * - Fernando Rangel de Sousa
     - Technical Advisor
     - UFSC
     - Professor
   * - Héctor Pettenghi Roldán
     - Technical Advisor
     - UFSC
     - Professor
   * - Kleber Vieira de Paiva
     - Technical Advisor
     - UFSC
     - Professor
   * - Laio Oriel Seman
     - Technical Advisor
     - UFSC
     - Professor
   * - Richard Demo Souza
     - Technical Advisor
     - UFSC
     - Professor
   * - Samir Ahmad Mussa
     - Technical Advisor
     - UFSC
     - Professor
   * - Xisto Lucas Travassos Junior
     - Technical Advisor
     - UFSC
     - Professor
   * - Gabriel Mariano Marcelino
     - Technical Advisor
     - UFSC
     - Researcher
   * - Caique Sales de Miranda Gomes
     - Mechanical subsystem
     - UFSC
     - Student
   * - Carlos Porto
     - OBDH
     - UFSC
     - Student
   * - Eduardo Dutra Bittencourt
     - EPS
     - UFSC
     - Student
   * - Fernanda Paiva de Morais
     - EPS
     - UFSC
     - Student
   * - Felipe Juliano
     - ADCS
     - UFSC
     - Student
   * - Gabriel Cabral
     - EPS
     - UFSC
     - Student
   * - João Cláudio Elsen Barcellos
     - System Engineering
     - UFSC
     - Student
   * - Maria Eduarda Rezende
     - Mechanical subsystem
     - UFSC
     - Student
   * - Miguel Boing
     - OBDH/2U
     - UFSC
     - Student
   * - Vitória Beatriz Bianchin
     - TMTC/2U
     - UFSC
     - Student
   * - Ramon Araujo Borba
     - EPS
     - UFSC
     - Student
   * - Rebecca Quintino Do Ó
     - RE²PS
     - UFSC
     - Student

Cycle of Revisions
------------------

The review cycle is based on the **ECSS** (European Cooperation for Space Standardization) standard, as presented in :numref:`tab:revision-cycle`.

.. _tab:revision-cycle:

.. list-table:: Cycle of revisions.
   :header-rows: 1

   * - **Acronym**
     - **Revision**
     - **Revision's description**
   * - MDR
     - Mission Definition Review
     - The MDR examines the proposed requirements and mission's architecture
   * - PDR
     - Preliminary Design Review
     - The PDR demonstrates that preliminary design meets all system requirements with acceptable risk and within cost and time constraints.
   * - CDR
     - Critical Design Review
     - The CDR demonstrates that the maturity of the design is appropriate to support the proceeding with full-scale fabrication, assembly, integration and test.
   * - AR
     - Acceptance Review
     - The AR demonstrates that a mission can be conducted
