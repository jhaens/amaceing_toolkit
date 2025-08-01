API Reference
=============

This comprehensive API reference documents all the functions available in the aMACEing toolkit. The toolkit provides a Pythonic interface for molecular simulations with various engines and trajectory analysis.

Core Simulation APIs
--------------------

CP2K API
~~~~~~~~

.. py:function:: amaceing_toolkit.cp2k_api(run_type=None, config=None)

   API function for CP2K input file creation.
   
   :param run_type: Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'REFTRAJ', 'ENERGY')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import cp2k_api
       
       # Geometry optimization
       config = {
           'project_name': 'test_geo',
           'coord_file': 'system.xyz',
           'pbc_list': [10.0, 0, 0, 0, 10.0, 0, 0, 0, 10.0],
           'max_iter': 100,
           'print_forces': 'OFF',
           'xc_functional': 'BLYP',
           'cp2k_newer_than_2023x': 'y'
       }
       
       cp2k_api(run_type='GEO_OPT', config=config)

MACE API
~~~~~~~~

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
       md_config = {
           'project_name': 'test_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': 'mace_mp',
           'model_size': 'small',
           'dispersion_via_ase': 'n',
           'temperature': 300,
           'nsteps': 10000,
           'timestep': 0.5,
           'thermostat': 'Langevin',
           'write_interval': 10,
           'log_interval': 100,
           'print_ext_traj': 'y',
       }
       
       mace_api(run_type='MD', config=md_config)

MatterSim API
~~~~~~~~~~~~~

.. py:function:: amaceing_toolkit.mattersim_api(run_type=None, config=None)

   API function for MatterSim input file creation.
   
   :param run_type: Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'FINETUNE', 'RECALC')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import mattersim_api
       
       # MD simulation example
       md_config = {
           'project_name': 'mattersim_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': 'large',
           'temperature': 300,
           'nsteps': 10000,
           'timestep': 0.5,
           'thermostat': 'Langevin',
           'timestep': 0.5,
           'write_interval': 10,
           'log_interval': 100,
           'print_ext_traj': 'y',
       }
       
       mattersim_api(run_type='MD', config=md_config)

SevenNet API
~~~~~~~~~~~~

.. py:function:: amaceing_toolkit.sevennet_api(run_type=None, config=None)

   API function for SevenNet input file creation.
   
   :param run_type: Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'RECALC')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import sevennet_api
       
       # MD simulation example
       md_config = {
           'project_name': 'sevennet_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': '7net-0',
           'modal': 'omat',
           'temperature': 300,
           'nsteps': 10000,
           'timestep': 0.5,
           'write_interval': 10,
           'log_interval': 100,
           'print_ext_traj': 'y'
       }
       
       sevennet_api(run_type='MD', config=md_config)

ORB API
~~~~~~~

.. py:function:: amaceing_toolkit.orb_api(run_type=None, config=None)

   API function for ORB input file creation.
   
   :param run_type: Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import orb_api
       
       # MD simulation example
       md_config = {
           'project_name': 'orb_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': 'orb_v3_conservative_inf',
           'modal': 'omat',
           'temperature': 300,
           'nsteps': 10000,
           'timestep': 0.5,
           'thermostat': 'Langevin',
           'write_interval': 10,
           'log_interval': 100,
           'print_ext_traj': 'y'
       }
       
       orb_api(run_type='MD', config=md_config)

Grace API
~~~~~~~~~

.. py:function:: amaceing_toolkit.grace_api(run_type=None, config=None)

   API function for Grace input file creation.
   
   :param run_type: Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'FINETUNE', 'RECALC')
   :type run_type: str, optional
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Creates input files in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import grace_api
       
       # MD simulation example
       md_config = {
           'project_name': 'grace_md',
           'coord_file': 'system.xyz',
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
           'foundation_model': 'GRACE-1L-OMAT',
           'temperature': 300,
           'nsteps': 10000,
           'timestep': 0.5,
           'thermostat': 'Langevin',
           'write_interval': 10,
           'log_interval': 100,
           'print_ext_traj': 'y'
       }
       
       grace_api(run_type='MD', config=md_config)

Trajectory Analysis
-------------------

Analyzer API
~~~~~~~~~~~~

.. py:function:: amaceing_toolkit.analyzer_api(file=None, pbc=None, timestep=None, visualize='y', rdf_pairs=None, msd_list=None, smsd_list=None, autocorr_pairs=None)

    API function for trajectory analysis.

    :param file: [OPTIONAL] Path(s) to the trajectory file(s). Multiple paths possible (e.g., 'coord1.xyz, coord2.xyz').
    :type file: str or list of str, optional
    :param pbc: [OPTIONAL] Path(s) to the PBC file(s). Multiple paths possible (e.g., 'pbc1, pbc2').
    :type pbc: str or list of str, optional
    :param timestep: [OPTIONAL] Timestep(s) in fs. Multiple values possible (e.g., '0.5, 1.0').
    :type timestep: str or list of str, optional
    :param visualize: [OPTIONAL] Visualize the analysis ('y' or 'n'). Default is 'y'.
    :type visualize: str, optional
    :param rdf_pairs: [OPTIONAL] RDF pairs to consider. Multiple values possible (e.g., 'O-H, H-H').
    :type rdf_pairs: str or list of str, optional
    :param msd_list: [OPTIONAL] MSD atoms to consider. Multiple values possible (e.g., 'O, H').
    :type msd_list: str or list of str, optional
    :param smsd_list: [OPTIONAL] sMSD atoms to consider. Multiple values possible (e.g., 'O, H').
    :type smsd_list: str or list of str, optional
    :param autocorr_pairs: [OPTIONAL] Autocorrelation pairs to consider. Multiple values possible (e.g., 'O-H, H-H').
    :type autocorr_pairs: str or list of str, optional
    :returns: None - Performs analysis and saves results in the current directory

    **Examples**::

         from amaceing_toolkit import analyzer_api

         # Analyze a trajectory with visualization
         analyzer_api(file='traj.xyz', pbc='pbc.txt', timestep='0.5', visualize='y', rdf_pairs='O-H', msd_list='O', smsd_list='H', autocorr_pairs='O-H')
       

Utility Functions
-----------------

.. py:function:: amaceing_toolkit.amaceing_utils(operation, config=None)

   API function for various utility operations.
   
   :param operation: Type of operation (EVAL_ERROR, PREPARE_EVAL_ERROR, EXTRACT_XYZ, CITATIONS, BENCHMARK)
   :type operation: str
   :param config: Dictionary with the configuration parameters
   :type config: dict, optional
   :returns: None - Performs the specified utility operation
   
**Examples**::

     from amaceing_toolkit import amaceing_utils

     # Evaluate error between ground truth and comparison files
     eval_config = {
          'ener_filename_ground_truth': 'ref_energies.txt',
          'force_filename_ground_truth': 'ref_forces.txt',
          'ener_filename_compare': 'test_energies.txt',
          'force_filename_compare': 'test_forces.txt'
     }
     amaceing_utils('EVAL_ERROR', config=eval_config)

     # Prepare files for error evaluation from a trajectory
     prep_config = {
          'traj_file': 'traj.traj',
          'each_nth_frame': 200,
          'start_cp2k': 'y',
          'log_file': 'mace_input.log',
          'xc_funtional': 'BLYP'
     }
     amaceing_utils('PREPARE_EVAL_ERROR', config=prep_config)

     # Extract XYZ coordinates from a trajectory
     extract_config = {
          'coord_file': 'traj.xyz',
          'each_nth_frame': 10
     }
     amaceing_utils('EXTRACT_XYZ', config=extract_config)

     # Get citations from a log file
     citations_config = {
          'log_file': 'xxx_input.log'
     }
     amaceing_utils('CITATIONS', config=citations_config)

     # Benchmark example
     benchmark_config = {
          'mode': 'MD',
          'coord_file': 'system.xyz',
          'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],
          'force_nsteps': 10000,
          'mace_model': ['mace_mp', 'small'],
          'mattersim_model': 'large',
          'sevennet_model': ['7net-mf-ompa', 'mpa'],
          'orb_model': ['orb_v3_conservative_inf', 'omat'],
          'grace_model': ['GRACE-1L-OMAT']
     }
     amaceing_utils('BENCHMARK', config=benchmark_config)

