SevenNet API
===========

The SevenNet API provides functions for creating SevenNet input files programmatically.

Function Reference
-----------------

.. py:function:: amaceing_toolkit.sevennet_api(run_type=None, config=None)

   API function for SevenNet input file creation.
   
   :param run_type: Type of calculation to run ('MD', 'MULTI_MD', 'FINETUNE', 'RECALC')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import sevennet_api
       
       # MD simulation example
       config = {
           'project_name': 'test_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': '7net-0',
           'modal': 'mpa',
           'temperature': '300',
           'pressure': '1.0',
           'nsteps': 1000,
           'write_interval': 10,
           'timestep': 0.5,
           'simulation_environment': 'ASE'
       }
       
       # Create a molecular dynamics input file
       sevennet_api(run_type='MD', config=config)

Configuration Parameters
-----------------------

MD
~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': '7net-mf-ompa/7net-omat/7net-l3i5/7net-0/PATH',
       'modal': 'mpa/oma24/None',
       'dispersion_via_simenv': 'y/n',
       'temperature': 'FLOAT',
       'pressure': 'FLOAT',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'nsteps': INT,
       'write_interval': INT,
       'timestep': FLOAT,
       'log_interval': INT,
       'print_ext_traj': 'y/n',
       'simulation_environment': 'ASE'
   }

MULTI_MD
~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': ['PATH', 'PATH', ...],
       'modal': ['mpa/oma24/None', 'mpa/oma24/None', ...],
       'dispersion_via_simenv': ['y/n', 'y/n', ...],
       'temperature': 'FLOAT',
       'pressure': 'FLOAT',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'nsteps': INT,
       'write_interval': INT,
       'timestep': FLOAT,
       'log_interval': INT,
       'print_ext_traj': 'y/n',
       'simulation_environment': 'ASE'
   }

FINETUNE
~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'train_file': 'FILE',
       'device': 'cuda/cpu',
       'foundation_model': '7net-mf-ompa/7net-omat/7net-l3i5/7net-0/PATH',
       'modal': 'mpa/oma24/None',
       'batch_size': INT,
       'valid_fraction': FLOAT,
       'valid_batch_size': INT,
       'max_num_epochs': INT,
       'seed': INT,
       'lr': FLOAT,
       'dir': 'PATH'
   }

RECALC
~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': '7net-mf-ompa/7net-omat/7net-l3i5/7net-0/PATH',
       'modal': 'mpa/oma24/None',
       'dispersion_via_simenv': 'y/n'
   }
