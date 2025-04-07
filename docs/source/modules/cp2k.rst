CP2K Module
===========

Overview
--------

The CP2K module is a core component of the aMACEing toolkit designed to facilitate the creation of CP2K input files through a user-friendly interface. It allows users to generate correctly formatted CP2K input files for various types of simulations without requiring extensive knowledge of CP2K's input syntax.

Capabilities
------------

The CP2K module supports the creation of input files for the following calculation types:

Geometry Optimization (GEO_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Optimizes atomic positions to find the minimum energy structure
* Configurable convergence criteria and iteration limits
* Options for printing forces during optimization

Cell Optimization (CELL_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Optimizes both atomic positions and cell parameters
* Supports various symmetry constraints (cubic, triclinic, etc.)
* Customizable convergence settings

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

* Supports different ensembles (NVE, NVT, NPT_F, NPT_I)
* Configurable timestep, temperature, and run length
* Options for equilibration runs prior to production
* Customizable output frequency for forces and velocities

Reference Trajectory Recalculation (REFTRAJ)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Recomputes energies and forces along an existing trajectory
* Configurable stride for processing only specific frames
* Options for forces and velocities output

Single Point Energy Calculation (ENERGY)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Quick energy evaluation without geometry changes
* Uses high accuracy SCF settings

Usage
-----

The CP2K module can be used in two ways:

Q&A Session
~~~~~~~~~~~

Start an interactive Q&A session with:

.. code-block:: bash

    amaceing_cp2k

This guides you through:

1. Selecting a coordinate file
2. Defining the simulation box
3. Choosing the type of calculation
4. Setting calculation-specific parameters
5. Configuring optional settings

The system will then generate:
- The CP2K input file
- A runscript for executing the calculation
- A log file documenting your choices

Command-line Usage
~~~~~~~~~~~~~~~~~~

Create input files directly with a single command:

.. code-block:: bash

    amaceing_cp2k -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Where RUN_TYPE is one of: GEO_OPT, CELL_OPT, MD, REFTRAJ, ENERGY

Parameters vary by run type:

For GEO_OPT:

.. code-block:: bash

    amaceing_cp2k -rt="GEO_OPT" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'max_iter': '200', 'print_forces': 'ON', 'xc_functional': 'PBE', 'cp2k_newer_than_2023x': 'y'}"

For CELL_OPT:

.. code-block:: bash

    amaceing_cp2k -rt="CELL_OPT" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'max_iter': '200', 'keep_symmetry': 'TRUE', 'symmetry': 'CUBIC', 'xc_functional': 'PBE', 'cp2k_newer_than_2023x': 'y'}"

For MD:

.. code-block:: bash

    amaceing_cp2k -rt="MD" -c="{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[10 10 10]', 'ensemble': 'NVT', 'nsteps': '10000', 'timestep': '0.5', 'temperature': '300', 'print_forces': 'ON', 'print_velocities': 'ON', 'xc_functional': 'PBE', 'cp2k_newer_than_2023x': 'y'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.

Output Files
------------

The module generates:

* CP2K input file (e.g., `geoopt_cp2k.inp`, `md_cp2k.inp`, etc.)
* HPC runscript (`runscript.sh`)
* Log file with configuration parameters (`cp2k_input.log`)
* For MD with equilibration, additional equilibration input and runscript files

Technical Details
-----------------

* Exchange-correlation functionals: Supports PBE, BLYP and others with optional D3 dispersion correction
* Basis sets: MOLOPT basis sets used by default
* SCF: OT method with DIIS minimizer and FULL_SINGLE_INVERSE preconditioner
* MD ensembles: Supports NVT, NPT_F (flexible cell), NPT_I (isotropic cell)
* For MD simulations, global thermostats are used for production, massive thermostats for equilibration
