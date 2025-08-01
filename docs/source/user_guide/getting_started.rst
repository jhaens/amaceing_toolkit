Getting Started
===============

aMACEing_toolkit provides several command-line tools and Python APIs for creating input files, running simulations, and analyzing results. This guide will help you get started with the basic usage patterns.

Command-Line Interface
----------------------

The toolkit offers interactive Q&A sessions for creating input files and configuring simulations. This is the easiest way for beginners to use the toolkit.

Basic Commands
~~~~~~~~~~~~~~

.. code-block:: bash

    amaceing_cp2k          # CP2K input creation
    amaceing_mace          # MACE input creation
    amaceing_mattersim     # MatterSim input creation 
    amaceing_sevennet      # SevenNet input creation
    amaceing_orb           # ORB input creation
    amaceing_grace         # Grace input creation
    amaceing_ana           # Trajectory analysis
    amaceing_utils         # Utility functions

Interactive Usage
~~~~~~~~~~~~~~~~~
To create a CP2K input file interactively, run:

.. code-block:: bash

    amaceing_cp2k

This will start an interactive session where you can answer questions about your simulation setup, such as the type of simulation (e.g., geometry optimization, molecular dynamics), the system's coordinates, periodic boundary conditions, and other parameters.

Non-Interactive Usage
~~~~~~~~~~~~~~~~~~~~~

For automated workflows or batch processing, you can use one-line commands:

.. code-block:: bash

    amaceing_cp2k -rt="GEO_OPT" -c="{'project_name': 'test', 'coord_file': 'system.xyz', 'pbc_list': [14.2067 0 0 0 14.2067 0 0 0 14.2067], 'max_iter': 100, 'xc_functional': 'BLYP', 'print_forces': 'OFF', 'cp2k_newer_than_2023x': 'y'}"

.. warning::
   When using the one-line command format, do **NOT** use double quotes inside the dictionary or commas inside lists in the dictionary. The dictionary is passed as a string and nested double quotes are not allowed.

Python API
----------

For more programmatic control or integration into your own Python scripts, you can use the Python API:

.. code-block:: python

    from amaceing_toolkit.workflow import cp2k_api
    
    # Generate CP2K geometry optimization input
    config = {
        'project_name': 'system_geoopt',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 100,
        'xc_functional': 'BLYP',
        'print_forces': 'OFF',
        'cp2k_newer_than_2023x': 'y'
    }
    cp2k_api(run_type='GEO_OPT', config=config)

Core Functionality
------------------

The toolkit supports different simulation types for various engines:

CP2K Workflows (``amaceing_cp2k``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``GEO_OPT``: Geometry optimization
* ``CELL_OPT``: Cell optimization
* ``MD``: Molecular dynamics
* ``REFTRAJ``: Recalculation of a reference trajectory
* ``ENERGY``: Single point energy calculation

MACE Workflows (``amaceing_mace``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Simulation**: ``GEO_OPT``, ``CELL_OPT``, ``MD``, ``MULTI_MD``, ``RECALC`` 
* **Training**: ``FINETUNE``, ``FINETUNE_MULTIHEAD``
* **Output formats**: ASE and LAMMPS

MatterSim Workflows (``amaceing_mattersim``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Simulation**: ``GEO_OPT``, ``CELL_OPT``, ``MD``, ``MULTI_MD``, ``RECALC``
* **Training**: ``FINETUNE``
* **Output formats**: ASE

SevenNet Workflows (``amaceing_sevennet``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Simulation**: ``GEO_OPT``, ``CELL_OPT``, ``MD``, ``MULTI_MD``, ``RECALC``
* **Training**: ``FINETUNE``
* **Output formats**: ASE, LAMMPS

ORB Workflows (``amaceing_orb``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Simulation**: ``GEO_OPT``, ``CELL_OPT``, ``MD``, ``MULTI_MD``, ``RECALC``
* **Training**: ``FINETUNE``
* **Output formats**: ASE

Grace Workflows (``amaceing_grace``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Simulation**: ``GEO_OPT``, ``CELL_OPT``, ``MD``, ``MULTI_MD``, ``RECALC``
* **Training**: ``FINETUNE``
* **Output formats**: ASE, LAMMPS

Trajectory Analysis (``amaceing_ana``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The analyzer supports:

* Single and multiple trajectory analysis
* Radial distribution function (RDF) 
* Mean square displacement (MSD)
* Single-particle mean square displacement (sMSD)
* Vector autocorrelation function (VACF)
* Visualization of results
* LaTeX report generation

Utility Functions (``amaceing_utils``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Model evaluation against reference trajectories
* Frame extraction from trajectories
* Citation management
* Benchmarking of different machine learning interatomic potentials (MLIPs)
* Run and model logging
