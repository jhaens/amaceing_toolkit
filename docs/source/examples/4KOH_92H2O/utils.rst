Utils Examples
==============

Overview
--------

The Utils module in the aMACEing toolkit provides utility functions for evaluating model performance, preparing data for calculations, and comparing different interatomic potential models. This example demonstrates using these utilities with the 4KOH_92H2O system.

Example Commands
----------------

The ``utils_test.sh`` script demonstrates six different utility functions:

Evaluate Errors (EVAL_ERROR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compares energies and forces from a machine learning model with reference DFT data:

.. code-block:: bash

    amaceing_utils --run_type="EVAL_ERROR" --config="{'ener_filename_ground_truth': '../../data/dft_energies.xyz', 'force_filename_ground_truth': '../../data/dft_forces.xyz', 'ener_filename_compare': '../../data/mace_energies.txt', 'force_filename_compare': '../../data/mace_forces.xyz'}"

Prepare Data for Error Evaluation (PREPARE_EVAL_ERROR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Processes a trajectory file to prepare data for error evaluation:

.. code-block:: bash

    amaceing_utils --run_type="PREPARE_EVAL_ERROR" --config="{'traj_file': '../../data/trajectory.traj', 'each_nth_frame': '1', 'start_cp2k': 'y', 'log_file': '../../data/mace_input.log', 'xc_functional': 'BLYP'}"

Extract XYZ Frames (EXTRACT_XYZ)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extracts every second frame from an XYZ trajectory file:

.. code-block:: bash

    amaceing_utils --run_type="EXTRACT_XYZ" --config="{'coord_file': '../../data/ref_trajectory.xyz', 'each_nth_frame': '2'}"

Citations Generator (CITATIONS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generates proper citations for the models used in a MACE simulation:

.. code-block:: bash

    amaceing_utils --run_type="CITATIONS" --config="{'log_file': '../../data/mace_input.log'}"

Benchmarking MD (BENCHMARK)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Benchmarks the performance of different ML models for molecular dynamics:

.. code-block:: bash

    amaceing_utils --run_type="BENCHMARK" --config="{'mode': 'MD', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'force_nsteps': '10', 'mace_model': '['mace_mp' 'small']', 'mattersim_model': 'large', 'sevennet_model': '['7net-mf-ompa' 'mpa']', 'orb_model': '['orb_v3_conservative_inf' 'omat']'}"

Benchmarking Recalculation (BENCHMARK)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Benchmarks the performance of different ML models for energy recalculation:

.. code-block:: bash

    amaceing_utils --run_type="BENCHMARK" --config="{'mode': 'RECALC', 'coord_file': '../../data/dft_energies.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'force_nsteps': '../../data/dft_forces.xyz', 'mace_model': '['mace_mp' 'small']', 'mattersim_model': 'large', 'sevennet_model': '['7net-mf-ompa' 'mpa']', 'orb_model': '['orb_v3_conservative_inf' 'omat']'}"

Running the Examples
--------------------

You can run all Utils examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/utils_test.sh

Alternatively, you can use the interactive Q&A interface by running ``amaceing_utils`` without command-line parameters and following the prompts.

Output Files
------------

After running these examples, each utility function will create its own directory with specific output files:

EVAL_ERROR
~~~~~~~~~~

.. code-block:: none

    utils/
    ├── EVAL_ERROR/
    │   ├── utils.log               # Log file with the details of the utils run
    │   └── error.txt               # Energy and force errors

PREPARE_EVAL_ERROR
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    utils/
    ├── PREPARE_EVAL_ERROR/
    │   ├── cp2k_inputs/           # Generated CP2K input files for each frame
    │   ├── energies.xyz           # Extracted energy data
    │   ├── forces.xyz             # Extracted force data
    │   └── utils.log              # Log of the preparation process

EXTRACT_XYZ
~~~~~~~~~~~

.. code-block:: none

    utils/
    ├── EXTRACT_XYZ/
    │   ├── utils.log              # Log file with the details of the utils run
    │   └── extracted_frames.xyz   # XYZ file with extracted frames

CITATIONS
~~~~~~~~~

.. code-block:: none

    utils/
    ├── CITATIONS/
    │   └── utils.log             # Log file with the details of the utils run

BENCHMARK_MD
~~~~~~~~~~~~

.. code-block:: none

    utils/
    ├── BENCHMARK_MD/
    │   ├── utils.log              # Log file with the details of the utils run
    │   ├── mace/                  # MACE run
    │   ├── mattersim/             # MatterSim run
    │   ├── sevennet/              # SevenNet run
    │   └── orb/                   # Orb run

BENCHMARK_RECALC
~~~~~~~~~~~~~~~~

.. code-block:: none

    utils/
    ├── BENCHMARK_RECALC/
    │   ├── utils.log              # Log file with the details of the utils run
    │   ├── mace/                  # MACE run
    │   ├── mattersim/             # MatterSim run
    │   ├── sevennet/              # SevenNet run
    │   └── orb/                   # Orb run

Technical Details
-----------------

* The utility functions can process trajectory data from any of the supported simulation engines
* Error evaluation compares energies in eV and forces in eV/Å
* The benchmark function compares MACE, MatterSim, and SevenNet models
* For the EXTRACT_XYZ function, every Nth frame is extracted based on the user-defined interval
* The citation generator supports automatic citation generation for all models in the toolkit

API Usage Example
-----------------

The same functionality can be accessed programmatically through the Python API:

.. code-block:: python

    from amaceing_toolkit.workflow import utils_api

    # Evaluate errors
    eval_error_config = {
        'ener_filename_ground_truth': 'dft_energies.xyz',
        'force_filename_ground_truth': 'dft_forces.xyz',
        'ener_filename_compare': 'mace_energies.txt',
        'force_filename_compare': 'mace_forces.xyz'
    }
    utils_api(run_type='EVAL_ERROR', config=eval_error_config)

    # Benchmark models
    benchmark_config = {
        'mode': 'MD',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 14.2067, 14.2067],
        'force_nsteps': 10,
        'mace_model': ['mace_mp', 'small'],
        'mattersim_model': 'large',
        'sevennet_model': ['7net-mf-ompa', 'mpa']
        'orb_model': ['orb_v3_conservative_inf', 'omat']
    }
    utils_api(run_type='BENCHMARK', config=benchmark_config)
