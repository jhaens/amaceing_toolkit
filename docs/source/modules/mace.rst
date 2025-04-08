MACE Module
===========

Overview
--------

The MACE module is a core component of the aMACEing toolkit designed to facilitate the creation of input files for MACE-torch simulations. It provides a user-friendly interface for preparing various machine learning-based molecular dynamics simulations and model fine-tuning tasks.

Capabilities
------------

The MACE module supports the creation of input files for the following calculation types:

Geometry Optimization (GEO_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Optimizes atomic positions to find the minimum energy structure
* Uses MACE foundation models for energy and force calculations
* Configurable convergence settings and maximum iterations

Cell Optimization (CELL_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Optimizes both atomic positions and cell parameters
* Uses hydrostatic strain filtering
* Supports periodic boundary conditions

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

* Supports various thermostats (Langevin, Nose-Hoover Chain, Bussi, NPT)
* Configurable temperature, timestep, and run length
* Options for trajectory output and logging frequency

Multi-Configuration Molecular Dynamics (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Runs multiple MD calculations with different foundation models
* Allows comparison of performance across different models
* Uses the same simulation settings for consistent comparison

Fine-tuning of Foundation Models (FINETUNE)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Fine-tunes MACE foundation models with custom datasets
* Configurable training parameters (learning rate, batch size, etc.)
* Options to prevent catastrophic forgetting
* Automatic E0 detection for supported exchange-correlation functionals

Multihead Fine-tuning (FINETUNE_MULTIHEAD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Trains multiple model heads for different data types
* Supports various exchange-correlation functionals
* Flexible dataset configuration for each head

Reference Trajectory Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Recomputes energies and forces along an existing trajectory
* Useful for evaluating model performance on reference trajectories
* Outputs energies and forces for comparison with reference data

Usage
-----

The MACE module can be used in two ways:

Q&A Session
~~~~~~~~~~~

Start an interactive Q&A session with:

.. code-block:: bash

    amaceing_mace

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the calculation type
4. Selecting the foundation model and size
5. Setting calculation-specific parameters

The system will then generate:

- Python script for the selected calculation
- Configuration file for fine-tuning (if applicable)
- A runscript for executing the calculation
- A log file documenting your choices

Command-line Usage
~~~~~~~~~~~~~~~~~~

Create input files directly with a single command:

.. code-block:: bash

    amaceing_mace -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: GEO_OPT, CELL_OPT, MD, MULTI_MD, FINETUNE, FINETUNE_MULTIHEAD, RECALC

For GEO_OPT:

.. code-block:: bash

    amaceing_mace -rt="GEO_OPT" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'max_iter': '200', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_mace': 'y'}"

For MD:

.. code-block:: bash

    amaceing_mace -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_mace': 'y', 'temperature': '300', 'thermostat': 'Langevin', 'pressure': 'None', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ase_traj': 'y'}"

For FINETUNE:

.. code-block:: bash

    amaceing_mace -rt="FINETUNE" -c="{'project_name': 'NAME', 'train_file': 'FILE', 'device': 'cuda', 'stress_weight': '1.0', 'forces_weight': '1000.0', 'energy_weight': '1.0', 'foundation_model': 'mace_mp', 'model_size': 'small', 'prevent_catastrophic_forgetting': 'y', 'batch_size': '5', 'valid_fraction': '0.1', 'valid_batch_size': '10', 'max_num_epochs': '50', 'seed': '42', 'lr': '1e-4', 'xc_functional_of_dataset': 'PBE', 'dir': 'models'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Output Files
------------

The module generates:

* Python script for the calculation (e.g., `geoopt_mace.py`, `md_mace.py`, etc.)
* For fine-tuning: YAML configuration file (e.g., `config_model_name.yml`)
* HPC runscript for execution (`runscript.sh` and `gpu_script.job`)
* Log file with configuration parameters (`mace_input.log`)
* For recalculation: Files with recalculated energies and forces

Foundation Models
-----------------

The module supports various foundation models:

* **mace_mp**: Materials Project foundation model (small, medium, large)
* **mace_off**: Organic molecules foundation model (small, medium, large)
* **mace_anicc**: ANI-CC foundation model
* **custom**: User-provided model path

Technical Details
-----------------

* Box configuration: Supports specification of cubic and orthorhombic simulation cells
* Thermostats: Langevin, NoseHooverChainNVT, Bussi, and NPT (for constant pressure)
* Dispersion corrections: Optional inclusion of dispersion via MACE
* Acceleration: Optional support for cuequivariance for faster calculations
* Model Logger: Automatic tracking of fine-tuned models
