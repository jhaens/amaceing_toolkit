SevenNet Module
==============

Overview
--------

The SevenNet module is a component of the aMACEing toolkit designed to facilitate the creation of input files for SevenNet simulations. SevenNet is a machine learning potential that enables atomistic simulations with high accuracy and efficiency. This module provides an interface for preparing molecular dynamics simulations and model evaluation with SevenNet.

Capabilities
-----------

The SevenNet module supports the creation of input files for the following calculation types:

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~

* Performs standard molecular dynamics simulations
* Supports various thermostats (Langevin, Nose-Hoover Chain, Bussi)
* Configurable temperature, timestep, and run length
* Options for trajectory output frequency

Multi-Configuration Molecular Dynamics (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Runs multiple MD calculations with different foundation models
* Allows comparison of performance across different models
* Uses the same simulation settings for consistent comparison
* Creates organized directory structure for each run

Reference Trajectory Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Recomputes energies and forces along an existing trajectory
* Useful for evaluating model performance on reference trajectories
* Outputs energies and forces for comparison with reference data

.. note::
   Fine-tuning of foundation models with SevenNet will be implemented in the near future.

Usage
-----

The SevenNet module can be used in two ways:

Q&A Session
~~~~~~~~~~

Start an interactive Q&A session with:

.. code-block:: bash

    amaceing_sevennet

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the calculation type
4. Selecting the foundation model
5. Setting calculation-specific parameters

The system will then generate:
- Python script for the selected calculation
- A runscript for executing the calculation
- A log file documenting your choices

Command-line Usage
~~~~~~~~~~~~~~~~

Create input files directly with a single command:

.. code-block:: bash

    amaceing_sevennet -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: MD, MULTI_MD, RECALC

For MD:

.. code-block:: bash

    amaceing_sevennet -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'foundation_model': 'latest', 'temperature': '300', 'thermostat': 'Langevin', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ase_traj': 'y'}"

For MULTI_MD:

.. code-block:: bash

    amaceing_sevennet -rt="MULTI_MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'foundation_model': '['latest' 'custom']', 'temperature': '300', 'thermostat': 'Langevin', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ase_traj': 'y'}"

For RECALC:

.. code-block:: bash

    amaceing_sevennet -rt="RECALC" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'foundation_model': 'latest'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Output Files
-----------

The module generates:

* Python script for the calculation (e.g., `md_sevennet.py`, `recalc_sevennet.py`)
* HPC runscripts for execution (`runscript.sh`)
* Log file with configuration parameters (`sevennet_input.log`)
* For recalculation: Files with recalculated energies and forces
* For multi-configuration MD: Directory structure with files for each configuration

Foundation Models
---------------

The module supports various foundation models:

* **latest**: Latest available SevenNet model
* **custom**: User-provided model path or model from the model logger

Technical Details
---------------

* Box configuration: Supports specification of cubic and orthorhombic simulation cells
* Thermostats: Langevin, NoseHooverChainNVT, Bussi
* Integration with ASE: Uses ASE for simulation infrastructure and trajectory handling
* Environment management: Runs in a separate conda environment to avoid package conflicts

API Reference
-----------

.. automodule:: amaceing_toolkit.workflow.sevennet_input_writer
   :members:
   :undoc-members:
   :show-inheritance: