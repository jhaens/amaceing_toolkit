aMACEing toolkit
================

**aMACEing_toolkit**: A Unified Interface for Machine-Learning Molecular Dynamics

.. image:: https://img.shields.io/github/v/release/jhaens/amaceing_toolkit
   :alt: GitHub Release
   :target: https://github.com/jhaens/amaceing_toolkit/releases

.. image:: https://img.shields.io/github/issues/jhaens/amaceing_toolkit
   :alt: GitHub Issues or Pull Requests
   :target: https://github.com/jhaens/amaceing_toolkit/issues

.. image:: https://app.readthedocs.org/projects/amaceing-toolkit/badge/
   :alt: Documentation Status
   :target: https://amaceing-toolkit.readthedocs.io/en/latest/

Overview
--------

aMACEing_toolkit is a scientific software package that facilitates the creation, execution, and analysis of molecular dynamics simulations using multiple simulation engines. It provides a unified workflow for quantum-mechanical calculations with CP2K and machine-learned interatomic potentials (MLIPs) including MACE, MatterSim, SevenNet, and ORB.

Key features:

* **Input Generation**: Easy-to-use interactive interfaces and API functions for creating input files for multiple simulation engines
* **Workflow Management**: Consistent workflow across different software packages
* **Trajectory Analysis**: Fast tools for analyzing simulation outputs (RDF, MSD, SMSD, vector autocorrelation)
* **Model Evaluation**: Utilities to assess and compare MLIP performance against reference data
* **Run Logging**: Tracking and documentation of simulation runs and fine-tuned models

.. list-table:: Supported Simulation Engines
   :header-rows: 1

   * - Framework
     - Simulation Types
     - Simulation Environments
   * - CP2K
     - GEO_OPT, CELL_OPT, MD, REFTRAJ, ENERGY
     - Input files
   * - MACE
     - GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE, FINETUNE_MULTIHEAD
     - ASE, LAMMPS
   * - MatterSim
     - GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE
     - ASE
   * - SevenNet
     - GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE
     - ASE, LAMMPS
   * - ORB
     - GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE
     - ASE
   * - Grace
     - GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE
     - ASE, LAMMPS

Resources
---------

* **GitHub Repository**: `aMACEing Toolkit GitHub <https://github.com/jhaens/amaceing_toolkit>`_
* **PyPI Package**: `aMACEing Toolkit PyPI <https://pypi.org/project/amaceing-toolkit/>`_
* **Interactive Tutorials**: 
  `Tutorial Notebook A <https://colab.research.google.com/drive/17sz84cj8PTPJPxAjs4IHuFamNq2g5mBM?usp=sharing>`_ | 
  `Tutorial Notebook B <https://colab.research.google.com/drive/1laGokzPIKxsPjj3GXn383Cu22Fq_ihb2?usp=sharing>`_

Contents
--------

.. toctree::
   :maxdepth: 1
   :caption: User Guide

   user_guide/installation
   user_guide/getting_started
   user_guide/workflow_overview
   user_guide/configuration

.. toctree::
   :maxdepth: 1
   :caption: Module Reference

   modules/cp2k
   modules/mace
   modules/mattersim
   modules/sevennet
   modules/orb
   modules/grace
   modules/analyzer
   modules/utils

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api_reference

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples/4KOH_92H2O/index
   examples/other
   examples/analyzer_example
