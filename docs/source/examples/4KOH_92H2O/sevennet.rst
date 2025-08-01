SevenNet Examples
=================

Overview
--------

This example demonstrates using SevenNet with the 4KOH_92H2O system to perform various types of calculations.

Example Commands
----------------

The ``sevennet_test.sh`` script demonstrates four different types of SevenNet calculations:

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

Runs an MD simulation using the 7net-mf-ompa foundation model with mpa modal:

.. code-block:: bash

    amaceing_sevennet --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '7net-mf-ompa', 'modal': 'mpa', 'dispersion_via_simenv': 'n', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

Multi-Configuration MD (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs multiple MD simulations with different SevenNet models for comparison:

.. code-block:: bash

    amaceing_sevennet --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['7net-0' '7net-mf-ompa']', 'dispersion_via_simenv': '['n' 'n']', 'modal': '['' 'mpa']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

Fine-tuning (FINETUNE)
~~~~~~~~~~~~~~~~~~~~~~

Fine-tunes a SevenNet foundation model with custom training data:

.. code-block:: bash

    amaceing_sevennet --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'device': 'cuda', 'train_file': '../../data/train_file_7net.xyz', 'foundation_model': '7net-0', 'epochs': 2, 'batch_size': 4, 'seed': 1, 'lr': 0.01, 'force_loss_ratio': 1.0}"

Energy Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recomputes energies for structures using a SevenNet model:

.. code-block:: bash

    amaceing_sevennet --run_type="RECALC" --config="{'project_name': '4koh_92h2o_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067', 'foundation_model': '7net-mf-ompa', 'modal': 'mpa', 'dispersion_via_simenv': 'n', 'simulation_environment': 'ase'}"

Running the Examples
--------------------

You can run all SevenNet examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/sevennet_test.sh

Alternatively, you can use the interactive Q&A interface by running ``amaceing_sevennet`` without command-line parameters and following the prompts.

Output Files
------------

After running these examples, each calculation type will create its own directory with the following files:

Molecular Dynamics
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── MD/
    │   ├── md_sevennet.py         # Python script for molecular dynamics
    │   ├── runscript.sh           # HPC runscript
    │   └── sevennet_input.log     # Log of choices

Multi-Configuration MD
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── MULTI_MD/
    │   ├── 4koh_92h2o_md_run-1/   # Directory for first configuration (7net-0)
    │   │   ├── md_sevennet.py
    │   │   └── runscript.sh
    │   ├── 4koh_92h2o_md_run-2/   # Directory for second configuration (7net-mf-ompa)
    │   │   ├── md_sevennet.py
    │   │   └── runscript.sh
    │   └── sevennet_input.log     # Log of choices

Fine-tuning
~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── FINETUNE/
    │   ├── finetune_sevennet.py   # Python script for fine-tuning
    │   ├── runscript.sh           # HPC runscript
    │   └── sevennet_input.log     # Log of choices

Energy Recalculation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    sevennet/
    ├── RECALC/
    │   ├── recalc_sevennet.py     # Python script for energy recalculation
    │   └── sevennet_input.log     # Log of choices

Technical Details
-----------------

* The simulation cell is cubic with dimensions 14.2067 × 14.2067 × 14.2067 Å³
* Both 7net-0 (base model) and 7net-mf-ompa (multifidelity model) are demonstrated
* For molecular dynamics, the timestep is set to 0.5 fs
* The system temperature is set to 300 K
* The Langevin thermostat is used for temperature control
* CUDA is used for GPU acceleration in fine-tuning
* The mpa modal is used with the 7net-mf-ompa foundation model

API Usage Example
-----------------

The same functionality can be accessed programmatically through the Python API:

.. code-block:: python

    from amaceing_toolkit.workflow import sevennet_api

    # Molecular dynamics simulation
    md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': '7net-mf-ompa',
        'modal': 'mpa',
        'dispersion_via_simenv': 'n',
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

    sevennet_api(run_type='MD', config=md_config)

    # Fine-tuning
    ft_config = {
        'project_name': '4koh_92h2o_ft',
        'device': 'cuda',
        'train_file': 'train_file_7net.xyz',
        'foundation_model': '7net-0',
        'epochs': 2,
        'batch_size': 4,
        'seed': 1,
        'lr': 0.01,
        'force_loss_ratio': 1.0
    }

    sevennet_api(run_type='FINETUNE', config=ft_config)
