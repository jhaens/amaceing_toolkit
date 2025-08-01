MatterSim Module
================

The MatterSim module is a component of the aMACEing toolkit that facilitates the creation of input files for MatterSim simulations.

`MatterSim Repository <https://github.com/microsoft/mattersim>`_

`MatterSim Website <https://https://microsoft.github.io/mattersim>`_

Capabilities
------------

The MatterSim module supports the creation of input files for the following calculation types:

* Geometry Optimization (GEO_OPT)
* Cell Optimization (CELL_OPT)
* Molecular Dynamics (MD)
* Multi-Configuration Molecular Dynamics (MULTI_MD)
* Reference Trajectory Recalculation (RECALC): Recomputes energies and forces along an existing trajectory
* Fine-tuning of Foundation Models (FINETUNE)

Usage
-----

The MatterSim module can be used in two ways:

Command-line Usage
~~~~~~~~~~~~~~~~~~

**Interactive Q&A session:**

.. code-block:: bash

    amaceing_mattersim

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the calculation type
4. Selecting the foundation model
5. Setting calculation-specific parameters

**Direct Command Line Usage:**

.. code-block:: bash

    amaceing_mattersim -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: GEO_OPT, CELL_OPT, MD, MULTI_MD, FINETUNE, RECALC

For MD:

.. code-block:: bash

    amaceing_mattersim -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'foundation_model': 'large', 'temperature': '300', 'thermostat': 'Langevin', 'pressure': 'None', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ext_traj': 'y'}"

For MULTI_MD:

.. code-block:: bash

    amaceing_mattersim -rt="MULTI_MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', 'foundation_model': '['small' 'large']', 'temperature': '300', 'thermostat': 'Langevin', 'nsteps': '10000', 'timestep': '0.5', 'write_interval': '10', 'log_interval': '10', 'print_ext_traj': 'y'}"

For FINETUNE:

.. code-block:: bash

    amaceing_mattersim -rt="FINETUNE" -c="{'project_name': 'NAME', 'train_file': 'FILE', 'device': 'cuda', 'force_loss_ratio': '1.0', 'foundation_model': 'small', 'batch_size': '5', 'save_checkpoint': 'y', 'ckpt_interval': '25', 'epochs': '50', 'seed': '42', 'lr': '5e-4', 'save_path': 'models', 'early_stopping': 'n'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Python API
~~~~~~~~~~

.. code-block:: python

    from amaceing_toolkit.workflow import mattersim_api

    config = {
        'project_name': 'koh_h2o_geoopt',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 100,
        'foundation_model': 'small',
        'simulation_environment': 'ase'
    }

    mattersim_api(run_type='GEO_OPT', config=config)

Output Files
------------

The module generates:

* Python script for the calculation (`<runtype>_mattersim.py`)
* HPC runscripts for execution (`runscript.sh` and `gpu_script.job`)
* Log file with configuration parameters (`mattersim_input.log`)
* For recalculation: Files with recalculated energies and forces
* For multi-MD: Directory structure with files for each configuration

Foundation Models
-----------------

The module supports various foundation models:

* **small**: MatterSim-v1.0.0-1M.pth (1 million parameters)
* **large**: MatterSim-v1.0.0-5M.pth (5 million parameters)
* **custom**: User-provided model path or model from the model logger

Technical Details
-----------------

* Thermostats: Langevin, NoseHooverChainNVT, Bussi, and NPT (for constant pressure)
* Dataset creation: Support for creating training datasets from coordinate and force files
* Model Logger: Automatic tracking of fine-tuned models