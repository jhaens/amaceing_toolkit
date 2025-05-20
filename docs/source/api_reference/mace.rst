MACE API
========

The MACE API provides functions for creating MACE input files programmatically.

Function Reference
-----------------

.. py:function:: amaceing_toolkit.mace_api(run_type=None, config=None)

   API function for MACE input file creation.
   
   :param run_type: Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'FINETUNE', 'FINETUNE_MULTIHEAD', 'RECALC')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import mace_api
       
       # MD simulation example
       config = {
           'project_name': 'test_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': 'mace_mp',
           'model_size': 'small',
           'dispersion_via_mace': 'n',
           'temperature': '300',
           'pressure': '1.0',
           'thermostat': 'Langevin',
           'nsteps': 1000,
           'write_interval': 10,
           'timestep': 0.5,
           'log_interval': 100,
           'print_ase_traj': 'y'
       }
       
       # Create a molecular dynamics input file
       mace_api(run_type='MD', config=config)
       
       # Fine-tuning example
       finetune_config = {
           'project_name': 'test_finetune',
           'train_file': 'train_data.xyz',
           'device': 'cuda',
           'stress_weight': 0.0,
           'forces_weight': 10.0,
           'energy_weight': 0.1,
           'foundation_model': 'mace_mp',
           'model_size': 'small',
           'prevent_catastrophic_forgetting': 'y',
           'batch_size': 5,
           'valid_fraction': 0.1,
           'valid_batch_size': 2,
           'max_num_epochs': 200,
           'seed': 1,
           'lr': 1e-2,
           'xc_functional_of_dataset': 'PBE',
           'dir': 'MACE_models'
       }
       
       # Create a fine-tuning input file
       mace_api(run_type='FINETUNE', config=finetune_config)

Configuration Parameters
-----------------------

MD
~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': 'mace_off/mace_anicc/mace_mp/PATH',
       'model_size': 'small/medium/large/none',
       'dispersion_via_mace': 'y/n',
       'temperature': 'FLOAT',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'pressure': 'FLOAT/None',
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
       'foundation_model': ['NAME/PATH', 'NAME/PATH', ...],
       'model_size': ['small/medium/large/none', 'small/medium/large/none', ...],
       'dispersion_via_mace': ['y/n', 'y/n', ...],
       'temperature': 'FLOAT',
       'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT',
       'pressure': 'FLOAT/None',
       'nsteps': INT,
       'timestep': FLOAT,
       'write_interval': INT,
       'log_interval': INT,
       'print_ase_traj': 'y/n'
   }

GEO_OPT
~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'max_iter': INT,
       'foundation_model': 'NAME/PATH',
       'model_size': 'small/medium/large/none',
       'dispersion_via_mace': 'y/n'
   }

CELL_OPT
~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'max_iter': INT,
       'foundation_model': 'NAME/PATH',
       'model_size': 'small/medium/large/none',
       'dispersion_via_mace': 'y/n'
   }

FINETUNE
~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'train_file': 'FILE',
       'device': 'cuda/cpu',
       'stress_weight': FLOAT,
       'forces_weight': FLOAT,
       'energy_weight': FLOAT,
       'foundation_model': 'NAME/PATH',
       'model_size': 'small/medium/large/none',
       'prevent_catastrophic_forgetting': 'y/n',
       'batch_size': INT,
       'valid_fraction': FLOAT,
       'valid_batch_size': INT,
       'max_num_epochs': INT,
       'seed': INT,
       'lr': FLOAT,
       'xc_functional_of_dataset': 'BLYP/PBE/BLYP_SR/PBE_SR',
       'dir': 'PATH'
   }

FINETUNE_MULTIHEAD
~~~~~~~~~~~~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'train_file': ['FILE', 'FILE', ...],
       'device': 'cuda/cpu',
       'stress_weight': FLOAT,
       'forces_weight': FLOAT,
       'energy_weight': FLOAT,
       'foundation_model': 'NAME/PATH',
       'model_size': 'small/medium/large/none',
       'batch_size': INT,
       'valid_fraction': FLOAT,
       'valid_batch_size': INT,
       'max_num_epochs': INT,
       'seed': INT,
       'lr': FLOAT,
       'xc_functional_of_dataset': ['BLYP/PBE/BLYP_SR/PBE_SR', ...],
       'dir': 'PATH'
   }

RECALC
~~~~~~

.. code-block:: python
   
   {
       'project_name': 'NAME',
       'coord_file': 'FILE',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'foundation_model': 'NAME/PATH',
       'model_size': 'small/medium/large/none',
       'dispersion_via_mace': 'y/n'
   }
