MatterSim API
============

The MatterSim API provides functions for creating MatterSim input files programmatically.

Function Reference
-----------------

.. py:function:: amaceing_toolkit.mattersim_api(run_type=None, config=None)

   API function for MatterSim input file creation.
   
   :param run_type: Type of calculation to run ('MD', 'MULTI_MD', 'FINETUNE', 'RECALC')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import mattersim_api
       
       # MD simulation example
       config = {
           'project_name': 'test_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': 'large',
           'temperature': '300',
           'pressure': '1.0',
           'nsteps': 1000,
           'write_interval': 10,
           'timestep': 0.5,
       }
       
       # Create a molecular dynamics input file
       mattersim_api(run_type='MD', config=config)

Configuration Parameters
-----------------------

MD
~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT],
       'foundation_model': 'small/large/PATH',
       'temperature': 'FLOAT',
       'pressure': 'FLOAT/None',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'nsteps': INT,
       'timestep': FLOAT,
       'write_interval': INT,
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
       'pressure': 'FLOAT/None',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'nsteps': INT,
       'timestep': FLOAT,
       'write_interval': INT,
       'log_interval': INT,
       'print_ase_traj': 'y/n'
   }

FINETUNE
~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'train_file': 'FILE',
       'device': 'cuda/cpu',
       'foundation_model': 'small/large/PATH',
       'batch_size': INT,
       'valid_fraction': FLOAT,
       'max_num_epochs': INT,
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
       'foundation_model': 'small/large/PATH'
   }
