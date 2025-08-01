MACE Examples
=============

Overview
--------

This example demonstrates using MACE with the 4KOH_92H2O system to perform various types of calculations.

Example Commands
----------------

The ``mace_test.sh`` script demonstrates seven different types of MACE calculations:

Geometry Optimization (GEO_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimizes atomic positions using the MACE Materials Project foundation model (small size):

.. code-block:: bash

    amaceing_mace --run_type="GEO_OPT" --config="{'project_name': '4koh_92h2o_geoopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_simenv': 'n', 'max_iter': '10', 'simulation_environment': 'ase'}"

Cell Optimization (CELL_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimizes both atomic positions and cell parameters using the MACE Materials Project foundation model:

.. code-block:: bash

    amaceing_mace --run_type="CELL_OPT" --config="{'project_name': '4koh_92h2o_geoopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_simenv': 'n', 'max_iter': '10', 'simulation_environment': 'ase'}"

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

Runs an MD simulation at 300K using the Langevin thermostat with the MACE Materials Project small model:

.. code-block:: bash

    amaceing_mace --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_simenv': 'n', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '20', 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

Multi-Configuration MD (MULTI_MD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs multiple MD calculations with different foundation models in parallel for comparison:

.. code-block:: bash

    amaceing_mace --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_multimd', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['mace_mp' 'mace_mp' 'mace_off']', 'model_size': '['small' 'medium' 'small']', 'dispersion_via_simenv': '['n' 'n' 'n']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '10', 'write_interval': '1', 'timestep': 0.5, 'log_interval': '1', 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"

This demonstrates the ability to compare three different models:
- MACE Materials Project (small)
- MACE Materials Project (medium)
- MACE Off (small)

Fine-tuning (FINETUNE)
~~~~~~~~~~~~~~~~~~~~~~

Fine-tunes a MACE foundation model with custom training data:

.. code-block:: bash

    amaceing_mace --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'train_file': '../../data/train_file.xyz', 'device': 'cuda', 'stress_weight': 0.0, 'forces_weight': 10.0, 'energy_weight': 0.1, 'foundation_model': 'mace_mp', 'model_size': 'small', 'batch_size': 5, 'prevent_catastrophic_forgetting': 'n', 'valid_fraction': 0.1, 'valid_batch_size': 2, 'epochs': '2', 'seed': 1, 'lr': 0.01, 'dir': 'MACE_models', 'xc_functional_of_dataset' : 'BLYP'}"

This example fine-tunes the MACE Materials Project small model on BLYP-calculated data with higher weight for forces (10.0) than energies (0.1).

Multihead Fine-tuning (FINETUNE_MULTIHEAD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fine-tunes a model with multiple datasets simultaneously:

.. code-block:: bash

    amaceing_mace --run_type="FINETUNE_MULTIHEAD" --config="{'project_name': '4koh_92h2o_mhft', 'train_file': '['../../data/train_file.xyz' '../../data/train_file2.xyz']', 'device': 'cuda', 'stress_weight': 0.0, 'forces_weight': 10.0, 'energy_weight': 0.1, 'foundation_model': 'mace_mp', 'model_size': 'small', 'batch_size': 5, 'valid_fraction': 0.1, 'valid_batch_size': 2, 'epochs': 2, 'seed': 1, 'lr': 0.01, 'xc_functional_of_dataset': '['BLYP' 'BLYP']', 'dir': 'MACE_models'}"

Energy Recalculation (RECALC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recomputes energies for a trajectory using a MACE model:

.. code-block:: bash

    amaceing_mace --run_type="RECALC" --config="{'project_name': '4koh_92h2o', 'coord_file': '../../data/dft_energies.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_simenv': 'n', 'simulation_environment': 'ase'}"

Running the Examples
--------------------

You can run all MACE examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/mace_test.sh

Alternatively, you can use the interactive Q&A interface by running ``amaceing_mace`` without command-line parameters and following the prompts.

Output Files
------------

After running these examples, each calculation type will create its own directory with the following files:

Geometry Optimization
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mace/
    ├── GEO_OPT/
    │   ├── geoopt_mace.py           # Python script for geometry optimization
    │   ├── runscript.sh             # HPC runscript
    │   └── mace_input.log           # Log of choices

Cell Optimization
~~~~~~~~~~~~~~~~~

.. code-block:: none

    mace/
    ├── CELL_OPT/
    │   ├── cellopt_mace.py          # Python script for cell optimization
    │   ├── runscript.sh             # HPC runscript
    │   └── mace_input.log           # Log of choices

Molecular Dynamics
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mace/
    ├── MD/
    │   ├── md_mace.py               # Python script for molecular dynamics
    │   ├── runscript.sh             # HPC runscript
    │   └── mace_input.log           # Log of choices

Multi-Configuration MD
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mace/
    ├── MULTI_MD/
    │   ├── md_mace_1/               # Directory for first configuration
    │   │   ├── md_mace.py
    │   │   └── runscript.sh
    │   ├── md_mace_2/               # Directory for second configuration
    │   ├── md_mace_3/               # Directory for third configuration
    │   └── mace_input.log           # Log of choices

Fine-tuning
~~~~~~~~~~~

.. code-block:: none

    mace/
    ├── FINETUNE/
    │   ├── finetune_mace.py         # Python script for fine-tuning
    │   ├── runscript.sh             # HPC runscript
    │   └── mace_input.log           # Log of choices

Multihead Fine-tuning
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mace/
    ├── FINETUNE_MULTIHEAD/
    │   ├── finetune_multihead_mace.py # Python script for multihead fine-tuning
    │   ├── runscript.sh             # HPC runscript
    │   └── mace_input.log           # Log of choices

Energy Recalculation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    mace/
    ├── RECALC/
    │   ├── recalc_mace.py           # Python script for energy recalculation
    │   ├── runscript.sh             # HPC runscript
    │   └── mace_input.log           # Log of choices

Technical Details
-----------------

* The simulation cell is cubic with dimensions 14.2067 × 14.2067 × 14.2067 Å³
* The MACE Materials Project foundation model is used with small and medium sizes
* For molecular dynamics, the timestep is set to 0.5 fs
* The system temperature is set to 300 K
* The Langevin thermostat is used for temperature control
* ASE is used as the simulation environment

API Usage Example
-----------------

The same functionality can be accessed programmatically through the Python API:

.. code-block:: python

    from amaceing_toolkit import mace_api

    # Molecular dynamics simulation
    md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_simenv': 'n',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 20,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y',
        'simulation_environment': 'ase'
    }

    mace_api(run_type='MD', config=md_config)

    # Fine-tuning
    ft_config = {
        'project_name': '4koh_92h2o_ft',
        'train_file': 'train_file.xyz',
        'device': 'cuda',
        'stress_weight': 0.0,
        'forces_weight': 10.0,
        'energy_weight': 0.1,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'batch_size': 5,
        'prevent_catastrophic_forgetting': 'n',
        'valid_fraction': 0.1,
        'valid_batch_size': 2,
        'epochs': 2,
        'seed': 1,
        'lr': 0.01,
        'dir': 'MACE_models',
        'xc_functional_of_dataset': 'BLYP'
    }

    mace_api(run_type='FINETUNE', config=ft_config)
