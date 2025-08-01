ORB Module
===============

The ORB module is a component of the aMACEing toolkit designed to facilitate the creation of input files for ORB simulations.

`ORB Repository <https://github.com/orbital-materials/orb-models>`_

Capabilities
------------

The ORB module supports the creation of input files (ASE/LAMMPS) for the following calculation types:

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

    amaceing_orb

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the calculation type
4. Selecting the foundation model
5. Setting calculation-specific parameters

**Direct Command Line Usage:**

.. code-block:: bash

    amaceing_orb -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE

For MD:

.. code-block:: bash

    amaceing_orb -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'foundation_model': 'orb_v2', 'temperature': '300', 'thermostat': 'Langevin', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'dispersion_via_simenv': 'n', 'print_ext_traj': 'y'}"

For FINETUNE:

.. code-block:: bash

    amaceing_orb -rt="FINETUNE" -c="{'project_name': 'NAME', 'foundation_model': 'orb_v2', 'train_file': 'FILE', 'batch_size': 'INT', 'epochs': 'INT', 'seed': '1', 'lr': '0.01'}"

For RECALC:

.. code-block:: bash

    amaceing_orb -rt="RECALC" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'dispersion_via_simenv': 'n', 'foundation_model': 'orb_v3_conservative_inf', 'modal': 'omat'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Python API
~~~~~~~~~~

.. code-block:: python

    from amaceing_toolkit.workflow import sevennet_api
    
    config = {
        'project_name': 'koh_h2o_geoopt',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 100,
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
        'dispersion_via_simenv': 'n'
    }

    sevennet_api(run_type='GEO_OPT', config=config)

Output Files
------------

The module generates:

* Python script for the calculation (`<runtype>_sevennet.py`)
* HPC runscripts for execution (`runscript.sh` and `gpu_script.job`)
* For fine-tuning: YAML configuration file (`config_finetune.yml`)
* Log file with configuration parameters (`sevennet_input.log`)
* For recalculation: Files with recalculated energies and forces
* For multi-configuration MD: Directory structure with files for each configuration

Foundation Models
-----------------

The module supports various foundation models:

* **orb_v3_conservative_inf**: (recommended) model trained on Materials Project data, Alexandria data (modal: **mpa**) and Meta Open Materials 2024 (modal: **omat**) data
* **orb_v2**: model trained on Materials Project and Alexandria data (default model, only model available for fine-tuning)
* **custom**: User-provided model path or model from the model logger

Technical Details
-----------------

* Thermostats: Langevin, NoseHooverChainNVT, Bussi and NPT
* Environment management: Runs in a separate conda environment to avoid package conflicts
* Dispersion corrections: Optional inclusion of dispersion via ASE (**But**: Only available for orb_v2)
* Model Logger: Automatic tracking of fine-tuned models
