MatterSim Module
===============

Overview
--------

The MatterSim module is a component of the aMACEing toolkit that facilitates the creation of input files for MatterSim simulations. MatterSim is a deep learning atomistic model that enables accurate simulations across elements, temperatures, and pressures. This module provides an interface for preparing molecular dynamics simulations and model fine-tuning with MatterSim.

Capabilities
-----------

The MatterSim module supports the creation of input files for the following calculation types:

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~

* Performs standard molecular dynamics simulations
* Supports various thermostats (Langevin, Nose-Hoover Chain, Bussi)
* Configurable temperature, timestep, and run length
* Options for constant pressure simulations (NPT)

Multi-Configuration Molecular Dynamics (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Runs multiple MD calculations with different foundation models
* Allows comparison of performance across different models
* Uses the same simulation settings for consistent comparison
* Creates organized directory structure for each run

Fine-tuning of Foundation Models (FINETUNE)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Fine-tunes MatterSim foundation models with custom datasets
* Configurable training parameters (learning rate, batch size, etc.)
* Options for model checkpointing
* Support for both CPU and GPU training

Reference Trajectory Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Recomputes energies and forces along an existing trajectory
* Useful for evaluating model performance on reference trajectories
* Outputs energies and forces for comparison with reference data

Usage
-----

The MatterSim module can be used in two ways:

Q&A Session
~~~~~~~~~~

Start an interactive Q&A session with:

.. code-block:: bash

    amaceing_mattersim

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the calculation type
4. Selecting the foundation model
5. Setting calculation-specific parameters

The system will then generate:
- Python script for the selected calculation
- Configuration file for fine-tuning (if applicable)
- A runscript for executing the calculation on CPU or GPU
- A log file documenting your choices

Command-line Usage
~~~~~~~~~~~~~~~~

Create input files directly with a single command:

.. code-block:: bash

    amaceing_mattersim -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: MD, MULTI_MD, FINETUNE, RECALC

For MD:

.. code-block:: bash

    amaceing_mattersim -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'foundation_model': 'small', 'dispersion_via_ase': 'y', 'temperature': '300', 'thermostat': 'Langevin', 'pressure': 'None', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ase_traj': 'y'}"

For MULTI_MD:

.. code-block:: bash

    amaceing_mattersim -rt="MULTI_MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'foundation_model': '['small' 'large']', 'dispersion_via_ase': '['y' 'n']', 'temperature': '300', 'thermostat': 'Langevin', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ase_traj': 'y'}"

For FINETUNE:

.. code-block:: bash

    amaceing_mattersim -rt="FINETUNE" -c="{'project_name': 'NAME', 'train_data_path': 'FILE', 'device': 'cuda', 'force_loss_ratio': '1.0', 'load_model_path': 'small', 'batch_size': '5', 'save_checkpoint': 'y', 'ckpt_interval': '25', 'epochs': '50', 'seed': '42', 'lr': '1e-4', 'save_path': 'models'}"

For RECALC:

.. code-block:: bash

    amaceing_mattersim -rt="RECALC" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'foundation_model': 'small', 'dispersion_via_ase': 'y'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Output Files
-----------

The module generates:

* Python script for the calculation (e.g., `md_mattersim.py`, `recalc_mattersim.py`)
* HPC runscripts for execution (`runscript.sh` and `gpu_script.job`)
* Log file with configuration parameters (`mattersim_input.log`)
* For recalculation: Files with recalculated energies and forces
* For multi-configuration MD: Directory structure with files for each configuration

Foundation Models
---------------

The module supports various foundation models:

* **small**: MatterSim-v1.0.0-1M.pth (1 million parameters)
* **large**: MatterSim-v1.0.0-5M.pth (5 million parameters)
* **custom**: User-provided model path or model from the model logger

Technical Details
---------------

* Box configuration: Supports specification of cubic and orthorhombic simulation cells
* Thermostats: Langevin, NoseHooverChainNVT, Bussi, and NPT (for constant pressure)
* Dispersion corrections: Optional inclusion of dispersion via ASE
* Dataset creation: Support for creating training datasets from coordinate and force files
* Model Logger: Automatic tracking of fine-tuned models
* Integration with ASE: Uses ASE for simulation infrastructure and trajectory handling

API Reference
-----------

.. automodule:: amaceing_toolkit.workflow.mattersim_input_writer
   :members:
   :undoc-members:
   :show-inheritance: