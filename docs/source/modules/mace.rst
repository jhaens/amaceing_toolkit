MACE Module
===========

The MACE module is a core component of the aMACEing toolkit designed to facilitate the creation of input files for MACE-torch ASE/LAMMPS simulations. It provides a user-friendly interface for preparing various machine learning-based molecular dynamics simulations and model fine-tuning tasks.

`MACE Repository <https://mace-docs.readthedocs.io>`_

`MACE Documentation <https://github.com/ACEsuit/mace>`_

Capabilities
------------

The MACE module supports the creation of input files for the following calculation types:

* Geometry Optimization (GEO_OPT)
* Cell Optimization (CELL_OPT)
* Molecular Dynamics (MD)
* Multi-Configuration Molecular Dynamics (MULTI_MD)
* Reference Trajectory Recalculation (RECALC): Recomputes energies and forces along an existing trajectory
* Fine-tuning of Foundation Models (FINETUNE)
* Multihead Fine-tuning (FINETUNE_MULTIHEAD): Trains multiple model heads on different datasets


Usage
-----

The MACE module can be used in two ways:

Command-line Usage
~~~~~~~~~~~~~~~~~~

**Interactive Q&A session:**

.. code-block:: bash

    amaceing_mace

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the calculation type
4. Selecting the foundation model and size
5. Setting calculation-specific parameters

**Direct Command Line Usage:**
.. code-block:: bash

    amaceing_mace -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: GEO_OPT, CELL_OPT, MD, MULTI_MD, FINETUNE, FINETUNE_MULTIHEAD, RECALC

For GEO_OPT:

.. code-block:: bash

    amaceing_mace -rt="GEO_OPT" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'max_iter': '200', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_simenv': 'y', 'simulation_environment': 'ase'}"

For MD:

.. code-block:: bash

    amaceing_mace -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_simenv': 'y', 'temperature': '300', 'thermostat': 'Langevin', 'pressure': 'None', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

For FINETUNE:

.. code-block:: bash

    amaceing_mace -rt="FINETUNE" -c="{'project_name': 'NAME', 'train_file': 'FILE', 'device': 'cuda', 'stress_weight': '0.0', 'forces_weight': '10.0', 'energy_weight': '1.0', 'foundation_model': 'mace_mp', 'model_size': 'small', 'prevent_catastrophic_forgetting': 'n', 'batch_size': '5', 'valid_fraction': '0.1', 'valid_batch_size': '2', 'max_num_epochs': '200', 'seed': '42', 'lr': '0.01', 'xc_functional_of_dataset': 'PBE', 'dir': 'models'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Python API
~~~~~~~~~~

.. code-block:: python

    from amaceing_toolkit.workflow import mace_api
    
    config = {
        'project_name': 'koh_h2o_geoopt',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 100,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_simenv': 'y',
        'simulation_environment': 'ase'
    }

    mace_api(run_type='GEO_OPT', config=config)

Output Files
------------

The module generates:

* Python script for the calculation (`<runtype>_mace.py`)
* LAMMPS input file for MACE-torch simulations (`lammps_<runtype>.inp`)
* For fine-tuning: YAML configuration file (`config_<project_name>.yml`)
* HPC runscript for execution (`runscript.sh` and/or `gpu_script.job`)
* Log file with configuration parameters (`mace_input.log`)
* For recalculation: Files with recalculated energies and forces
* For multi-MD: Directory structure with files for each configuration

Foundation Models
-----------------

The module supports various foundation models:

* **mace_mp**: Materials Project foundation model (small, medium, large, medium-mpa-0)
* Additional **mace_mp** variants: (small-omat-0, medium-omat-0, medium-matpes-pbe-0, medium-matpes-r2scan-0) *NEW SINCE v0.3.13 and v.0.3.11*
* **mace_omol**: Organic molecules foundation model (extra-large) *NEW SINCE v0.3.14*
* **mace_off**: Organic molecules foundation model (small, medium, large)
* **mace_anicc**: ANI-CC foundation model
* **custom**: User-provided model path

Technical Details
-----------------

* Thermostats: Langevin, NoseHooverChainNVT, Bussi, and NPT
* Dispersion corrections: Optional inclusion of dispersion via MACE
* Acceleration: Optional support for cuequivariance for faster calculations
* Model Logger: Automatic tracking of fine-tuned models