MatterSim Examples
==================

Overview
--------

This example demonstrates using MatterSim with the 4KOH_92H2O system to perform various types of calculations.

Example Commands
----------------

The ``mattersim_test.sh`` script demonstrates four different types of MatterSim calculations:

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

Runs an MD simulation using the large MatterSim foundation model:

.. code-block:: bash

    amaceing_mattersim --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'large', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '10', 'write_interval': 10, 'timestep': 0.5, 'log_interval': 100, 'print_ext_traj': 'y'}"

Multi-Configuration MD (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs multiple MD simulations with different MatterSim model sizes for comparison:

.. code-block:: bash

    amaceing_mattersim --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['small' 'large']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '10', 'write_interval': 10, 'timestep': 0.5, 'log_interval': 100, 'print_ext_traj': 'y'}"

Fine-tuning (FINETUNE)
~~~~~~~~~~~~~~~~~~~~~~

Fine-tunes a MatterSim foundation model with custom training data:

.. code-block:: bash

    amaceing_mattersim --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'train_file': '../../data/train_file_ms.xyz', 'device': 'cuda', 'force_loss_ratio': 100.0, 'foundation_model': 'small', 'batch_size': 5, 'save_checkpoint': 'y', 'ckpt_interval': 25, 'epochs': 2, 'seed': 1, 'lr': 0.01, 'save_path': 'MatterSim_models', 'early_stopping': 'n'}"

Energy Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recomputes energies for a trajectory using a MatterSim model:

.. code-block:: bash

    amaceing_mattersim --run_type="RECALC" --config="{'project_name': '4koh_92h2o_recalc', 'coord_file': '../../data/dft_energies.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'large'}"

Running the Examples
--------------------

You can run all MatterSim examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/mattersim_test.sh

Alternatively, you can use the interactive Q&A interface by running ``amaceing_mattersim`` without command-line parameters and following the prompts.

Output Files
------------

After running these examples, each calculation type will create its own directory with the following files:

Molecular Dynamics
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mattersim/
    ├── MD/
    │   ├── md_mattersim.py          # Python script for molecular dynamics
    │   ├── runscript.sh             # HPC runscript
    │   └── mattersim_input.log      # Log of choices

Multi-Configuration MD
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mattersim/
    ├── MULTI_MD/
    │   ├── md_mattersim_1/          # Directory for first configuration (small model)
    │   │   ├── md_mattersim.py
    │   │   └── runscript.sh
    │   ├── md_mattersim_2/          # Directory for second configuration (large model)
    │   │   ├── md_mattersim.py
    │   │   └── runscript.sh
    │   └── mattersim_input.log      # Log of choices

Fine-tuning
~~~~~~~~~~~

.. code-block:: none

    mattersim/
    ├── FINETUNE/
    │   ├── finetune_mattersim.py    # Python script for fine-tuning
    │   ├── runscript.sh             # HPC runscript
    │   └── mattersim_input.log      # Log of choices

Energy Recalculation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mattersim/
    ├── RECALC/
    │   ├── recalc_mattersim.py      # Python script for energy recalculation
    │   ├── runscript.sh             # HPC runscript
    │   └── mattersim_input.log      # Log of choices

Technical Details
-----------------

* The simulation cell is cubic with dimensions 14.2067 × 14.2067 × 14.2067 Å³
* Both small and large MatterSim foundation models are demonstrated
* For molecular dynamics, the timestep is set to 0.5 fs
* The system temperature is set to 300 K
* The Langevin thermostat is used for temperature control
* CUDA is used for GPU acceleration in fine-tuning

API Usage Example
-----------------

The same functionality can be accessed programmatically through the Python API:

.. code-block:: python

    from amaceing_toolkit import mattersim_api

    # Molecular dynamics simulation
    md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'large',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ext_traj': 'y'
    }

    mattersim_api(run_type='MD', config=md_config)

    # Fine-tuning
    ft_config = {
        'project_name': '4koh_92h2o_ft',
        'train_file': 'train_file_ms.xyz',
        'device': 'cuda',
        'force_loss_ratio': 100.0,
        'foundation_model': 'small',
        'batch_size': 5,
        'save_checkpoint': 'y',
        'ckpt_interval': 25,
        'epochs': 2,
        'seed': 1,
        'lr': 0.01,
        'save_path': 'MatterSim_models',
        'early_stopping': 'n'
    }

    mattersim_api(run_type='FINETUNE', config=ft_config)
