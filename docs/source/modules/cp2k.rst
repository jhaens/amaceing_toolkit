CP2K Module
===========

The CP2K module provides tools for generating CP2K input files for a small set of calculations.

`CP2K Website <https://www.cp2k.org/>`_

`CP2K Documentation <https://manual.cp2k.org/trunk/>`_


Supported Calculation Types
---------------------------

* Geometry Optimization (GEO_OPT)
* Cell Optimization (CELL_OPT)
* Molecular Dynamics (MD)
* Reference Trajectory Recalculation (REFTRAJ)
* Single Point Energy Calculation (ENERGY)

Usage
-----

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

**Interactive Q&A Mode**:

.. code-block:: bash

    amaceing_cp2k

**Direct Command Line Mode**:

.. code-block:: bash

    amaceing_cp2k -rt="RUN_TYPE" -c="{'parameter1': 'value1', 'parameter2': 'value2', ...}"

Example for GEO_OPT:

.. code-block:: bash

    amaceing_cp2k --run_type="GEO_OPT" --config="{'project_name': 'koh_h2o_geoopt', 'coord_file': 'system.xyz', 'pbc_list': '[14.20670 0 0 0 14.2067 0 0 0 14.2067]', 'max_iter': 10, 'xc_functional': 'BLYP', 'print_forces': 'OFF', 'cp2k_newer_than_2023x': 'y'}"

Python API
~~~~~~~~~~

.. code-block:: python

    from amaceing_toolkit.workflow import cp2k_api
    
    config = {
        'project_name': 'koh_h2o_geoopt',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 100,
        'print_forces': 'OFF',
        'cp2k_newer_than_2023x': 'y',
        'xc_functional': 'BLYP'
    }
    
    cp2k_api(run_type='GEO_OPT', config=config)

Key Parameters
--------------

Common Parameters
~~~~~~~~~~~~~~~~~

* ``project_name``: Name for the calculation (used for output files)
* ``coord_file``: Path to the input geometry file (.xyz format)
* ``pbc_list``: Periodic boundary conditions, as a list of 9 values representing the cell vectors
* ``xc_functional``: Exchange-correlation functional (e.g., 'PBE', 'BLYP', 'PBE_SR', 'BLYP_SR')
* ``cp2k_newer_than_2023x``: Flag to enable features for CP2K versions newer than 2023.x

Run Type-Specific Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**GEO_OPT**:
  * ``max_iter``: Maximum optimization iterations
  * ``print_forces``: Whether to print forces ('ON'/'OFF')

**CELL_OPT**:
  * ``max_iter``: Maximum optimization iterations
  * ``keep_symmetry``: Whether to preserve cell symmetry ('TRUE'/'FALSE')
  * ``symmetry``: Type of cell symmetry to maintain ('CUBIC', 'ORTHORHOMBIC', 'TRICLINIC', ...)

**MD**:
  * ``ensemble``: Type of ensemble ('NVE', 'NVT', 'NPT_F', 'NPT_I')
  * ``nsteps``: Number of MD steps
  * ``timestep``: MD timestep in fs
  * ``temperature``: Target temperature in K
  * ``equilibration_run``: Whether to perform equilibration ('y'/'n')
  * ``equilibration_steps``: Number of equilibration steps

**REFTRAJ**:
  * ``ref_traj``: Path to the reference trajectory file
  * ``nsteps``: Number of steps to process
  * ``stride``: Step interval for processing
  * ``print_forces``: Whether to print forces ('ON'/'OFF')

**ENERGY**:
  * No additional required parameters

Output Files
------------

The module generates:

* A CP2K input file (``<run_type>_cp2k.inp``)
* A runscript for job submission (``runscript.sh``) 
* A log file documenting the configuration (``cp2k_input.log``)
* For MD with equilibration, additional equilibration input, runscript files and a python script that extracts the last step from the equilibration trajectory

For MD:

.. code-block:: bash

    amaceing_cp2k --run_type="MD" --config="{'project_name': 'koh_h2o_md', 'coord_file': 'system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'ensemble': 'NVT', 'nsteps': '10', 'timestep': 0.5, 'temperature': 300, 'print_forces': 'ON', 'print_velocities': 'OFF', 'xc_functional': 'BLYP', 'equilibration_run': 'y', 'equilibration_steps': '5', 'cp2k_newer_than_2023x': 'y'}"

.. note::
   Do **NOT** use double quotes inside the dictionary. Also do **NOT** use commas inside of lists in the dictionary.


Implementation Details
----------------------

The CP2K module uses templates and configuration defaults that are stored in:

* ``amaceing_toolkit/default_configs/cp2k_configs.py``: Default settings for all CP2K calculations
* ``amaceing_toolkit/default_configs/kind_data_functionals.py``: Basis sets and pseudopotentials for different elements and functionals


Technical Details
-----------------

* Exchange-correlation functionals: Supports PBE, BLYP and others with optional short-range (SR) variants
* Basis sets: MOLOPT basis sets used by default
* SCF: OT method with DIIS minimizer and FULL_SINGLE_INVERSE preconditioner
* For MD simulations, global thermostats are used for production, massive thermostats for equilibration