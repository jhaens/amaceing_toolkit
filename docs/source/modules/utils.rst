Utilities Module
================

Overview
--------

The Utilities module provides a set of helpful tools for working with machine learning potentials and molecular dynamics trajectories. It includes functions for evaluating model accuracy, preparing datasets, manipulating trajectories, and citing relevant software packages.

Capabilities
------------

The Utilities module includes the following tools:

Model Error Evaluation (EVAL_ERROR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Calculates errors between machine learning potential predictions and reference data
* Computes mean absolute error (MAE) for both forces and energies
* Provides relative force errors for assessing model quality
* Outputs detailed error statistics to a text file

Reference Data Preparation (PREPARE_EVAL_ERROR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Extracts frames from a trajectory file at specified intervals
* Creates input files for CP2K reference calculations
* Prepares necessary files for model evaluation
* Generates runscripts for obtaining reference data

Trajectory Frame Extraction (EXTRACT_XYZ)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Extracts frames from XYZ trajectory files at specified intervals
* Creates a new XYZ file with the extracted frames
* Preserves all metadata from the original trajectory
* Useful for reducing trajectory size for analysis or visualization

Citation Generation (MACE_CITATIONS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Provides proper citations for the toolkit and underlying methods
* Extracts model information from log files
* Generates BibTeX-formatted citations for publications
* Ensures proper attribution of methods used in calculations

Benchmarking (BENCHMARK)
~~~~~~~~~~~~~~~~~~~~~~~~

* Creates a structured directory for benchmarking multiple ML potentials
* Supports MACE, MatterSim, and SevenNet potentials
* Enables direct comparison of performance across models
* Provides two operating modes:
  - MD: Forward simulation with identical starting conditions
  - RECALC: Recalculation of forces/energies from a reference trajectory
* Automatically generates comparison statistics when using RECALC mode

Logger Access
~~~~~~~~~~~~~

* Provides access to the run logger and model logger
* Displays summaries of previous calculations
* Lists available fine-tuned models
* Helps track project history and available resources

Usage examples:

.. code-block:: bash

    amaceing_utils -l=model  # Shows fine-tuned models
    amaceing_utils -l=run    # Shows run history

Usage
-----

The Utilities module can be accessed in two ways:

Q&A Session
~~~~~~~~~~~

Start an interactive Q&A session with:

.. code-block:: bash

    amaceing_utils

This guides you through:

1. Selecting the utility function to use
2. Providing necessary inputs for the selected function
3. Configuring parameters specific to that function

Command-line Usage
~~~~~~~~~~~~~~~~~~

Access utilities directly with a single command:

.. code-block:: bash

    amaceing_utils -rt="FUNCTION_NAME" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where FUNCTION_NAME is one of: EVAL_ERROR, PREPARE_EVAL_ERROR, EXTRACT_XYZ, MACE_CITATIONS, BENCHMARK

For model error evaluation:

.. code-block:: bash

    amaceing_utils -rt="EVAL_ERROR" -c="{'ener_filename_ground_truth': 'eval_run-pos-1.xyz', 'force_filename_ground_truth': 'force.xyz', 'ener_filename_compare': 'mace_coord.xyz', 'force_filename_compare': 'mace_force.xyz'}"

For trajectory frame extraction:

.. code-block:: bash

    amaceing_utils -rt="EXTRACT_XYZ" -c="{'coord_file': 'trajectory.xyz', 'each_nth_frame': '10'}"

For benchmarking:

.. code-block:: bash

    amaceing_utils -rt="BENCHMARK" -c="{'mode': 'MD', 'coord_file': 'coord.xyz', 'pbc_list': '[10 10 10]', 'force_nsteps': '20000', 'mace_model': '['mace_mp' 'small']', 'mattersim_model': 'small', 'sevennet_model': '['7net-mf-ompa' 'mpa']'}"

To view logger information:

.. code-block:: bash

    amaceing_utils -l=model  # Shows fine-tuned models
    amaceing_utils -l=run    # Shows run history

Output and File Structure
-------------------------

Each utility function produces different outputs:

* **EVAL_ERROR**: Creates ``errors.txt`` with statistics on force and energy errors
* **PREPARE_EVAL_ERROR**: Creates ``mace_coord.xyz``, ``mace_force.xyz``, and ``pbc`` files
* **EXTRACT_XYZ**: Creates a new XYZ file with extracted frames
* **BENCHMARK**: Creates directories ``mace/``, ``mattersim/``, and ``sevennet/`` with input files

Technical Details
-----------------

* Force units: eV/Å (converted from Hartree/Bohr when reading CP2K output)
* Energy units: eV (converted from Hartree when reading CP2K output)
* Frame extraction uses consistent time intervals based on frame numbers
* Error statistics include both absolute and relative errors
* Benchmarking supports both forward simulation and reference trajectory recalculation
