CP2K API
========

The CP2K API provides functions for creating CP2K input files programmatically.

Function Reference
-----------------

.. py:function:: amaceing_toolkit.cp2k_api(run_type=None, config=None)

   API function for CP2K input file creation.
   
   :param run_type: Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'REFTRAJ', 'ENERGY')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import cp2k_api
       
       config = {
           'project_name': 'test_geo',
           'coord_file': 'system.xyz',
           'pbc_list': [10.0, 0, 0, 0, 10.0, 0, 0, 0, 10.0],
           'max_iter': 1000,
           'print_forces': 'OFF',
           'xc_functional': 'BLYP',
           'cp2k_newer_than_2023x': 'y'
       }
       
       # Create a geometry optimization input file
       cp2k_api(run_type='GEO_OPT', config=config)
       
Configuration Parameters
-----------------------

GEO_OPT
~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'max_iter': INT,
       'print_forces': 'ON/OFF',
       'xc_functional': 'PBE/PBE_SR/BLYP/BLYP_SR',
       'cp2k_newer_than_2023x': 'y/n'
   }

CELL_OPT
~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'max_iter': INT,
       'keep_symmetry': 'TRUE/FALSE',
       'symmetry': 'CUBIC/TRICLINIC/NONE/MONOCLINIC/ORTHORHOMBIC/TETRAGONAL/TRIGONAL/HEXAGONAL',
       'xc_functional': 'PBE/PBE_SR/BLYP/BLYP_SR',
       'cp2k_newer_than_2023x': 'y/n'
   }

MD
~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'ensemble': 'NVE/NVT/NPT_F/NPT_I',
       'nsteps': INT,
       'timestep': FLOAT,
       'temperature': FLOAT,
       'print_forces': 'ON/OFF',
       'print_velocities': 'ON/OFF',
       'xc_functional': 'PBE/PBE_SR/BLYP/BLYP_SR',
       'equilibration_run': 'y/n',
       'equilibration_steps': INT,
       'pressure_b': FLOAT,
       'cp2k_newer_than_2023x': 'y/n'
   }

REFTRAJ
~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'ref_traj': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'nsteps': INT,
       'stride': INT,
       'print_forces': 'ON/OFF',
       'print_velocities': 'ON/OFF',
       'xc_functional': 'PBE/PBE_SR/BLYP/BLYP_SR',
       'cp2k_newer_than_2023x': 'y/n'
   }

ENERGY
~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'xc_functional': 'PBE/PBE_SR/BLYP/BLYP_SR',
       'cp2k_newer_than_2023x': 'y/n'
   }
