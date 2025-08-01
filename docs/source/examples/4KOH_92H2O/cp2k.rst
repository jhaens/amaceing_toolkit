CP2K Examples
=============

Overview
--------

The CP2K framework in the aMACEing toolkit provides quantum-chemical calculations based on density functional theory (DFT). This example demonstrates using CP2K with the 4KOH_92H2O system to perform various types of calculations.

Example Commands
----------------

The ``cp2k_test.sh`` script demonstrates five different types of CP2K calculations for the 4KOH_92H2O system:

Geometry Optimization (GEO_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimizes atomic positions to find the minimum energy structure using the BLYP exchange-correlation functional with a limited number of steps (10) to showcase functionality.

.. code-block:: bash

    amaceing_cp2k --run_type="GEO_OPT" --config="{'project_name': '4koh_92h2o_geoopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.20670 0 0 0 14.2067 0 0 0 14.2067]', 'max_iter': 10, 'xc_functional': 'BLYP', 'print_forces': 'OFF', 'cp2k_newer_than_2023x': 'y'}"

Cell Optimization (CELL_OPT)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimizes both atomic positions and cell parameters while maintaining cubic symmetry:

.. code-block:: bash

    amaceing_cp2k --run_type="CELL_OPT" --config="{'project_name': '4koh_92h2o_cellopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'max_iter': '10', 'keep_symmetry': 'OFF', 'symmetry': 'CUBIC', 'xc_functional': 'BLYP', 'cp2k_newer_than_2023x': 'y'}"

Molecular Dynamics (MD)
~~~~~~~~~~~~~~~~~~~~~~~

Runs an NVT ensemble simulation at 300K with equilibration (5 steps) and production (10 steps) phases. The script demonstrates force printing and temperature control:

.. code-block:: bash

    amaceing_cp2k --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'ensemble': 'NVT', 'nsteps': '10', 'timestep': 0.5, 'temperature': 300, 'print_forces': 'ON', 'print_velocities': 'OFF', 'xc_functional': 'BLYP', 'equilibration_run': 'y', 'equilibration_steps': '5', 'pressure_b': 1.0, 'cp2k_newer_than_2023x': 'y'}"

Reference Trajectory Recalculation (REFTRAJ)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recalculates energies and forces for frames from a reference trajectory. This is useful for creating training data for machine learning potentials:

.. code-block:: bash

    amaceing_cp2k --run_type="REFTRAJ" --config="{'project_name': '4koh_92h2o_reftraj', 'ref_traj': '../../data/ref_trajectory.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'nsteps': '10', 'stride': '1', 'print_forces': 'ON', 'print_velocities': 'OFF', 'xc_functional': 'BLYP', 'cp2k_newer_than_2023x': 'y'}"

Energy Calculation (ENERGY)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Performs a single-point energy calculation with the BLYP functional:

.. code-block:: bash

    amaceing_cp2k --run_type="ENERGY" --config="{'project_name': '4koh_92h2o_energy', 'coord_file': 'system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'xc_functional': 'BLYP', 'cp2k_newer_than_2023x': 'y'}"

Running the Examples
--------------------

You can run all CP2K examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/cp2k_test.sh

Alternatively, you can use the interactive Q&A interface by running ``amaceing_cp2k`` without command-line parameters and following the prompts.

Output Files
------------

After running these examples, each calculation type will create its own directory with the following files:

Geometry Optimization
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    cp2k/
    ├── GEO_OPT/
    │   ├── geoopt_cp2k.inp          # CP2K input file
    │   ├── runscript.sh             # HPC runscript
    │   └── cp2k_input.log           # Log of choices

Cell Optimization
~~~~~~~~~~~~~~~~~

.. code-block:: none

    cp2k/
    ├── CELL_OPT/
    │   ├── cellopt_cp2k.inp         # CP2K input file
    │   ├── runscript.sh             # HPC runscript
    │   └── cp2k_input.log           # Log of choices

Molecular Dynamics
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    cp2k/
    ├── MD/
    │   ├── equi_md_cp2k.inp         # Equilibration run input
    │   ├── runscript_equi.sh        # Equilibration runscript
    │   ├── md_cp2k.inp              # Production run input
    │   ├── runscript.sh             # Production runscript
    │   └── cp2k_input.log           # Log of choices

Reference Trajectory
~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    cp2k/
    ├── REFTRAJ/
    │   ├── reftraj_cp2k.inp         # CP2K input file
    │   ├── runscript.sh             # HPC runscript
    │   └── cp2k_input.log           # Log of choices

Energy Calculation
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    cp2k/
    ├── ENERGY/
    │   ├── energy_cp2k.inp          # CP2K input file
    │   ├── runscript.sh             # HPC runscript
    │   └── cp2k_input.log           # Log of choices

Technical Details
-----------------

* The simulation cell is cubic with dimensions 14.2067 × 14.2067 × 14.2067 Å³
* The BLYP exchange-correlation functional is used for all CP2K calculations
* For molecular dynamics, the timestep is set to 0.5 fs
* The system temperature is set to 300 K
* The calculation is designed to work with CP2K versions newer than 2023x

API Usage Example
-----------------

The same functionality can be accessed programmatically through the Python API:

.. code-block:: python

    from amaceing_toolkit import cp2k_api

    # Geometry optimization
    geo_opt_config = {
        'project_name': '4koh_92h2o_geoopt',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 10,
        'xc_functional': 'BLYP',
        'print_forces': 'OFF',
        'cp2k_newer_than_2023x': 'y'
    }

    cp2k_api(run_type='GEO_OPT', config=geo_opt_config)

    # Molecular dynamics
    md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': 'system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'ensemble': 'NVT',
        'nsteps': 10,
        'timestep': 0.5,
        'temperature': 300,
        'print_forces': 'ON',
        'print_velocities': 'OFF',
        'xc_functional': 'BLYP',
        'equilibration_run': 'y',
        'equilibration_steps': 5,
        'pressure_b': 1.0,
        'cp2k_newer_than_2023x': 'y'
    }

    cp2k_api(run_type='MD', config=md_config)
