GRACE Examples
==============

Overview
--------

This example demonstrates using GRACE with the 4KOH_92H2O system to perform various types of calculations.

Example Commands
----------------

The ``grace_test.sh`` script demonstrates four different types of GRACE calculations:

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

Runs an MD simulation using the GRACE-1L-OMAT foundation model:

.. code-block:: bash

    amaceing_grace --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'GRACE-1L-OMAT', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

Multi-Configuration MD (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs multiple MD simulations with different GRACE models for comparison:

.. code-block:: bash

    amaceing_grace --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['GRACE-1L-OMAT' 'GRACE-1L-OAM']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

Fine-tuning (FINETUNE)
~~~~~~~~~~~~~~~~~~~~~~

Fine-tunes a GRACE foundation model with custom training data:

.. code-block:: bash

    amaceing_grace --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'train_file': '../../data/train_file_7net.xyz', 'foundation_model': 'GRACE-1L-OAM', 'epochs': 2, 'batch_size': 4, 'seed': 1, 'lr': 0.01, 'force_loss_ratio': 1.0}"

Energy Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recomputes energies for structures using a GRACE model:

.. code-block:: bash

    amaceing_grace --run_type="RECALC" --config="{'project_name': '4koh_92h2o_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'GRACE-1L-OMAT', 'simulation_environment': 'ase'}"

Running the Examples
--------------------

You can run all GRACE examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/grace_test.sh

Alternatively, you can use the interactive Q&A interface by running ``amaceing_grace`` without command-line parameters and following the prompts.

Output Files
------------

After running these examples, each calculation type will create its own directory with the following files:

Molecular Dynamics
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── MD/
    │   ├── md_grace.py          # Python script for molecular dynamics
    │   ├── runscript.sh         # HPC runscript
    │   └── grace_input.log      # Log of choices

Multi-Configuration MD
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── MULTI_MD/
    │   ├── 4koh_92h2o_md_run-1/ # Directory for first configuration (GRACE-1L-OMAT)
    │   │   ├── md_grace.py
    │   │   └── runscript.sh
    │   ├── 4koh_92h2o_md_run-2/ # Directory for second configuration (GRACE-1L-OAM)
    │   │   ├── md_grace.py
    │   │   └── runscript.sh
    │   └── grace_input.log      # Log of choices

Fine-tuning
~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── FINETUNE/
    │   ├── runscript.sh         # HPC runscript with start command
    │   └── grace_input.log      # Log of choices

Energy Recalculation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── RECALC/
    │   ├── recalc_grace.py      # Python script for energy recalculation
    │   └── grace_input.log      # Log of choices

Technical Details
-----------------

* The simulation cell is cubic with dimensions 14.2067 × 14.2067 × 14.2067 Å³
* For molecular dynamics, the timestep is set to 0.5 fs
* The system temperature is set to 300 K
* The Langevin thermostat is used for temperature control
* Force loss ratio of 1.0 is used for fine-tuning

API Usage Example
-----------------

The same functionality can be accessed programmatically through the Python API:

.. code-block:: python

    from amaceing_toolkit.workflow import grace_api

    # Molecular dynamics simulation
    md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'GRACE-1L-OMAT',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y',
        'simulation_environment': 'ase'
    }

    grace_api(run_type='MD', config=md_config)

    # Fine-tuning
    ft_config = {
        'project_name': '4koh_92h2o_ft',
        'train_file': 'train_file_7net.xyz',
        'foundation_model': 'GRACE-1L-OAM',
        'epochs': 2,
        'batch_size': 4,
        'seed': 1,
        'lr': 0.01,
        'force_loss_ratio': 1.0
    }

    grace_api(run_type='FINETUNE', config=ft_config)