GRACE Module
===============

The GRACE module is a component of the aMACEing toolkit designed to facilitate the creation of input files for GRACE simulations and finetuning.

`GRACE Repository <https://github.com/ICAMS/grace-tensorpotential>`_

`Grace Documentation <https://gracemaker.readthedocs.io/en/latest/>`_

Capabilities
------------

The GRACE module supports the creation of input files (ASE/LAMMPS) for the following calculation types:

* Geometry Optimization (GEO_OPT)
* Cell Optimization (CELL_OPT)
* Molecular Dynamics (MD)
* Multi-Configuration Molecular Dynamics (MULTI_MD)
* Reference Trajectory Recalculation (RECALC): Recomputes energies and forces along an existing trajectory
* Fine-tuning of Foundation Models (FINETUNE)

Usage
-----

Command-line Usage
~~~~~~~~~~~~~~~~~~

**Interactive Q&A session:**

.. code-block:: bash

    amaceing_grace

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the calculation type
4. Selecting the foundation model
5. Setting calculation-specific parameters

**Direct Command Line Usage:**

.. code-block:: bash

    amaceing_grace -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE

For MD:

.. code-block:: bash

    amaceing_grace -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'foundation_model': 'GRACE-1L-OMAT', 'temperature': '300', 'thermostat': 'Langevin', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

For FINETUNE:

.. code-block:: bash

    amaceing_grace -rt="FINETUNE" -c="{'project_name': 'NAME', 'foundation_model': 'GRACE-1L-OAM', 'train_file': 'FILE', 'batch_size': 'INT', 'epochs': 'INT', 'seed': '1', 'lr': '0.01', 'force_loss_ratio': 1.0}"

For RECALC:

.. code-block:: bash

    amaceing_grace -rt="RECALC" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'foundation_model': 'GRACE-1L-OMAT', 'simulation_environment': 'ase'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Python API
~~~~~~~~~~

.. code-block:: python

    from amaceing_toolkit.workflow import grace_api
    
    config = {
        'project_name': 'koh_h2o_geoopt',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 100,
        'foundation_model': 'GRACE-1L-OMAT',
        'simulation_environment': 'ase'
    }

    grace_api(run_type='GEO_OPT', config=config)

Output Files
------------

The module generates:

* Python script for the calculation (`<runtype>_grace.py`)
* HPC runscripts for execution (`runscript.sh` and `gpu_script.job`)
* For fine-tuning: YAML configuration file (`config_finetune.yml`), but no Python script (run it with `gracemaker config_finetune.yaml`)
* Log file with configuration parameters (`grace_input.log`)
* For recalculation: Files with recalculated energies and forces
* For multi-configuration MD: Directory structure with files for each configuration

Foundation Models
-----------------

The module supports various `foundation models <https://gracemaker.readthedocs.io/en/latest/gracemaker/foundation>`_:

* **GRACE-1L-OMAT**: (recommended) 1-layer model trained on Meta Open Materials 2024 data
* **GRACE-1L-OAM**: 1-layer model pre-fitted on the Meta Open Materials 2024 dataset and fine-tuned on the sAlex and MPTraj
* **GRACE-2L-OMAT**: (recommended) 2-layer model trained on Meta Open Materials 2024 data
* **GRACE-2L-OAM**: 2-layer model pre-fitted on the Meta Open Materials 2024 dataset and fine-tuned on the sAlex and MPTraj
* **custom**: User-provided model path or model from the model logger (only input the path to the main folder of the model files)

Technical Details
-----------------

* Thermostats: Langevin, NoseHooverChainNVT, Bussi and NPT
* Environment management: Runs in a separate conda environment to avoid package conflicts
* Dispersion corrections: Not available in this module
* Model Logger: Automatic tracking of fine-tuned models
* Available for both ASE and LAMMPS simulation environments