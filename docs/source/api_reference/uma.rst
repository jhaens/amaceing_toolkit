UMA API
=======

The UMA API provides functions for creating UMA input files programmatically.

Function Reference
-------------------

.. py:function:: amaceing_toolkit.uma_api(run_type=None, config=None)

   API function for UMA input file creation.
   
   :param run_type: Type of calculation to run ('MD', 'MULTI_MD', 'RECALC')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit.workflow import uma_api
       
       # MD simulation example
       config = {
           'project_name': 'test_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': 'omol',
           'temperature': '300',
           'pressure': '1.0',
           'thermostat': 'Langevin',
           'nsteps': 1000,
           'write_interval': 10,
           'timestep': 0.5,
           'log_interval': 10,
           'print_ase_traj': 'y'
       }
       
       # Create a molecular dynamics input file
       uma_api(run_type='MD', config=config)

Configuration Parameters
-------------------------

MD
~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': 'oc20/omat/omol/odac/omc/PATH',
       'temperature': 'FLOAT',
       'pressure': 'FLOAT',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'nsteps': INT,
       'write_interval': INT,
       'timestep': FLOAT,
       'log_interval': INT,
       'print_ase_traj': 'y/n'
   }

MULTI_MD
~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': ['PATH', 'PATH', ...],
       'temperature': 'FLOAT',
       'pressure': 'FLOAT',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'nsteps': INT,
       'write_interval': INT,
       'timestep': FLOAT,
       'log_interval': INT,
       'print_ase_traj': 'y/n'
   }

RECALC
~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': 'oc20/omat/omol/odac/omc/PATH'
   }