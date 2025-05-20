Utilities API
============

The Utilities API provides functions for various helper utilities in the aMACEing toolkit.

Function Reference
-----------------

.. py:function:: amaceing_toolkit.utils_api(run_type=None, config=None, logger=None)

   API function for various utilities.
   
   :param run_type: Type of utility to run ('EVAL_ERROR', 'PREPARE_EVAL_ERROR', 'EXTRACT_XYZ', 'MACE_CITATIONS', 'BENCHMARK')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :param logger: Logger to display ('run', 'model', 'runexport')
   :type logger: str, optional
   :returns: None - Runs the requested utility
   
   **Examples**::
   
       from amaceing_toolkit import utils_api
       
       # Evaluate error between reference and model predictions
       config = {
           'ener_filename_ground_truth': 'dft_energies.xyz',
           'force_filename_ground_truth': 'dft_forces.xyz',
           'ener_filename_compare': 'mace_energies.txt',
           'force_filename_compare': 'mace_forces.xyz'
       }
       utils_api(run_type='EVAL_ERROR', config=config)
       
       # Show model logger
       utils_api(logger='model')
       
       # Extract frames from trajectory
       extract_config = {
           'coord_file': 'traj.xyz', 
           'each_nth_frame': 10
       }
       utils_api(run_type='EXTRACT_XYZ', config=extract_config)

Configuration Parameters
-----------------------

EVAL_ERROR
~~~~~~~~~~

.. code-block:: python
   
   {
       'ener_filename_ground_truth': 'PATH',
       'force_filename_ground_truth': 'PATH',
       'ener_filename_compare': 'PATH',
       'force_filename_compare': 'PATH'
   }

PREPARE_EVAL_ERROR
~~~~~~~~~~~~~~~~~

.. code-block:: python
   
   {
       'traj_file': 'PATH',
       'each_nth_frame': INT,
       'start_cp2k': 'y/n',
       'log_file': 'PATH/None',
       'xc_functional': 'BLYP/PBE/BLYP_SR/PBE_SR'
   }

EXTRACT_XYZ
~~~~~~~~~~

.. code-block:: python
   
   {
       'coord_file': 'PATH',
       'each_nth_frame': INT
   }

MACE_CITATIONS
~~~~~~~~~~~~~

.. code-block:: python
   
   {
       'log_file': 'PATH'
   }

BENCHMARK
~~~~~~~~

.. code-block:: python
   
   {
       'mode': 'MD/RECALC',
       'coord_file': 'PATH',
       'pbc_list': [FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT],
       'force_nsteps': INT,  # If mode is MD
       'force_nsteps': 'PATH',  # If mode is RECALC (path to force file)
       'mace_model': ['mace_mp/mace_off/mace_anicc', 'small/medium/large'],
       'mattersim_model': 'small/large',
       'sevennet_model': ['7net-mf-ompa/7net-omat/7net-l3i5/7net-0', 'mpa/oma24/None']
   }

Logger Options
-------------

- **run**: Displays the run logger, showing information about all runs performed with the toolkit
- **model**: Displays the model logger, showing information about all fine-tuned models
- **runexport**: Exports the run log to a PDF file
