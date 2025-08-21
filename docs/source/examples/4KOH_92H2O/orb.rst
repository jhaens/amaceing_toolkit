ORB Examples
============

Overview
--------

This example demonstrates using ORB with the 4KOH_92H2O system to perform various types of calculations.

Example Commands
----------------

The ``orb_test.sh`` script demonstrates four different types of ORB calculations:

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

Runs an MD simulation using the orb_v3_conservative_inf foundation model with omat modal:

.. code-block:: bash

    amaceing_orb --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'orb_v3_conservative_inf', 'modal': 'omat', 'dispersion_via_simenv': 'n', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y'}"

Multi-Configuration MD (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs multiple MD simulations with different ORB models for comparison:

.. code-block:: bash

    amaceing_orb --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['orb_v2' 'orb_v3_conservative_inf']', 'dispersion_via_simenv': '['n' 'n']', 'modal': '['' 'omat']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y'}"

Fine-tuning (FINETUNE)
~~~~~~~~~~~~~~~~~~~~~~

Fine-tunes an ORB foundation model with custom training data:

.. code-block:: bash

    amaceing_orb --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'train_file': '../../data/train_file_7net.xyz', 'foundation_model': 'orb_v2', 'epochs': 2, 'batch_size': 4, 'seed': 1, 'lr': 0.0003, 'force_loss_ratio': 1.0}"

Energy Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recomputes energies for structures using an ORB model:

.. code-block:: bash

    amaceing_orb --run_type="RECALC" --config="{'project_name': '4koh_92h2o_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'orb_v3_conservative_inf', 'modal': 'omat', 'dispersion_via_simenv': 'n'}"

Running the Examples
--------------------

You can run all ORB examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/orb_test.sh

Alternatively, you can use the interactive Q&A interface by running ``amaceing_orb`` without command-line parameters and following the prompts.

Output Files
------------

After running these examples, each calculation type will create its own directory with the following files:

Molecular Dynamics
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── MD/
    │   ├── md_orb.py             # Python script for molecular dynamics
    │   ├── runscript.sh          # HPC runscript
    │   └── orb_input.log         # Log of choices

Multi-Configuration MD
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── MULTI_MD/
    │   ├── 4koh_92h2o_md_run-1/  # Directory for first configuration (orb_v2)
    │   │   ├── md_orb.py
    │   │   └── runscript.sh
    │   ├── 4koh_92h2o_md_run-2/  # Directory for second configuration (orb_v3_conservative_inf)
    │   │   ├── md_orb.py
    │   │   └── runscript.sh
    │   └── orb_input.log         # Log of choices

Fine-tuning
~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── FINETUNE/
    │   ├── finetune_orb.py       # Python script for fine-tuning
    │   ├── runscript.sh          # HPC runscript
    │   └── orb_input.log         # Log of choices

Energy Recalculation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── RECALC/
    │   ├── recalc_orb.py         # Python script for energy recalculation
    │   └── orb_input.log         # Log of choices

Technical Details
-----------------

* The simulation cell is cubic with dimensions 14.2067 × 14.2067 × 14.2067 Å³
* Both orb_v2 and orb_v3_conservative_inf foundation models are demonstrated
* For molecular dynamics, the timestep is set to 0.5 fs
* The system temperature is set to 300 K
* The Langevin thermostat is used for temperature control
* The omat modal is used with the orb_v3_conservative_inf foundation model

API Usage Example
-----------------

The same functionality can be accessed programmatically through the Python API:

.. code-block:: python

    from amaceing_toolkit.workflow import orb_api

    # Molecular dynamics simulation
    md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
        'dispersion_via_simenv': 'n',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y'
    }

    orb_api(run_type='MD', config=md_config)

    # Fine-tuning
    ft_config = {
        'project_name': '4koh_92h2o_ft',
        'train_file': 'train_file_7net.xyz',
        'foundation_model': 'orb_v2',
        'epochs': 2,
        'batch_size': 4,
        'seed': 1,
        'lr': 0.0003,
        'force_loss_ratio': 1.0
    }

    orb_api(run_type='FINETUNE', config=ft_config)
