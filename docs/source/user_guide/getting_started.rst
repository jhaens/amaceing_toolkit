Usage Guide
===========

This package is designed to be easy to use. You can create input files for CP2K, MACE, MatterSim, and SevenNet via a Q&A session or one-line commands.

Command-Line Usage
------------------

Q&A Session
~~~~~~~~~~~

Run the following commands to start a Q&A session for input creation:

.. code-block:: bash

    amaceing_cp2k          # CP2K input creation
    amaceing_mace          # MACE input creation
    amaceing_mattersim     # MatterSim input creation
    amaceing_sevennet      # SevenNet input creation
    amaceing_uma           # UMA (fairchem) input creation
    amaceing_ana           # Analyzer
    amaceing_utils         # Utilities

One-Line Commands
~~~~~~~~~~~~~~~~~

You can also use one-line commands for input creation:

.. code-block:: bash

    amaceing_<function> -rt="<run_type>" -c="{'project_name': 'test', 'pbc_list': '[10 0 0 0 10 0 0 0 10]', ...}"

.. note::
   **Important**: Do **NOT** use double quotes or commas inside lists in the dictionary.

Available Functions
-------------------

CP2K Input Creation
~~~~~~~~~~~~~~~~~~~

Supports:

* Geometry optimization
* Cell optimization
* Molecular dynamics
* Recalculation of a reference trajectory
* Single point energy calculation

MACE Input Creation
~~~~~~~~~~~~~~~~~~~

Supports:

* Geometry optimization
* Cell optimization
* Molecular dynamics
* Multi-configuration molecular dynamics
* Fine-tuning of a foundation model
* Multihead fine-tuning of a foundation model
* Recalculation of a reference trajectory

MatterSim Input Creation
~~~~~~~~~~~~~~~~~~~~~~~~

Supports:

* Molecular dynamics
* Multi-configuration molecular dynamics
* Fine-tuning of a foundation model
* Recalculation of a reference trajectory

SevenNet Input Creation
~~~~~~~~~~~~~~~~~~~~~~~

Supports:

* Molecular dynamics
* Multi-configuration molecular dynamics
* Fine-tuning of a foundation model
* Recalculation of a reference trajectory

SevenNet Input Creation
~~~~~~~~~~~~~~~~~~~~~~~

Supports:

* Molecular dynamics
* Multi-configuration molecular dynamics
* Recalculation of a reference trajectory

Analyzer
~~~~~~~~

Analyze results with:

* Single Trajectory Analysis
* Multiple Trajectory Analysis
* Radial Distribution Function (RDF)
* Mean Square Displacement (MSD)
* Single Particle MSD (sMSD)

Utilities
~~~~~~~~~

Includes:

* Model error evaluation
* Trajectory preparation
* Frame extraction
* Citation generation
* Benchmarking
* Logger overview