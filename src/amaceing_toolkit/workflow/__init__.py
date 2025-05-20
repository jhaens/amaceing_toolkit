from .cp2k_input_writer import atk_cp2k
from .mace_input_writer import atk_mace
from .mattersim_input_writer import atk_mattersim
from .mace_input_writer import mace_citations
from .utils import atk_utils
from .utils import print_logo
from .utils import string_to_dict
from .utils import string_to_dict_multi
from .utils import string_to_dict_multi2
from .utils import cite_amaceing_toolkit
from .utils import create_dataset
from .utils import e0_wrapper
from .utils import frame_counter
from .utils import extract_frames
from .utils import equi_to_md
from .utils import ask_for_float_int
from .utils import ask_for_int
from .utils import ask_for_yes_no
from .utils import ask_for_yes_no_pbc
from .utils import ask_for_non_cubic_pbc

# API functions for direct programmatic use
def cp2k_api(run_type=None, config=None):
    """
    API function for CP2K input file creation
    
    Parameters
    ----------
    run_type : str, optional
        Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'REFTRAJ', 'ENERGY')
    config : dict, optional
        Dictionary with the configuration parameters
        
    Returns
    -------
    None
        Creates input files in the current directory
        
    Examples
    --------
    >>> from amaceing_toolkit.workflow import cp2k_api
    >>> config = {
    ...     'project_name': 'test_geo',
    ...     'coord_file': 'system.xyz',
    ...     'pbc_list': [10.0, 0, 0, 0, 10.0, 0, 0, 0, 10.0],  # Will be formatted correctly for the command line
    ...     'max_iter': 1000,
    ...     'print_forces': 'OFF',
    ...     'xc_functional': 'BLYP',
    ...     'cp2k_newer_than_2023x': 'y'
    ... }
    >>> cp2k_api(run_type='GEO_OPT', config=config)
    """
    import sys
    import copy
    old_args = sys.argv
    try:
        sys.argv = ["amaceing_cp2k"]
        if run_type is not None:
            sys.argv.extend(["-rt", run_type])
        if config is not None:
            # Make a deep copy to avoid modifying the original
            config_copy = copy.deepcopy(config)
            
            # Handle the pbc_list special format
            if 'pbc_list' in config_copy and isinstance(config_copy['pbc_list'], list):
                config_copy['pbc_list'] = f"[{' '.join(str(x) for x in config_copy['pbc_list'])}]"
                
            sys.argv.extend(["-c", str(config_copy)])
        atk_cp2k()
    finally:
        sys.argv = old_args

def mace_api(run_type=None, config=None):
    """
    API function for MACE input file creation
    
    Parameters
    ----------
    run_type : str, optional
        Type of calculation to run ('GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'FINETUNE', 'FINETUNE_MULTIHEAD', 'RECALC')
    config : dict, optional
        Dictionary with the configuration parameters
        
    Returns
    -------
    None
        Creates input files in the current directory
        
    Examples
    --------
    >>> from amaceing_toolkit.workflow import mace_api
    >>> config = {
    ...     'project_name': 'test_md',
    ...     'coord_file': 'system.xyz',
    ...     'pbc_list': [14.0, 0, 0, 0, 14.0,0, 0, 0, 14.0],  # Will be formatted correctly for the command line
    ...     'foundation_model': 'mace_mp',
    ...     'model_size': 'small',
    ...     'dispersion_via_mace': 'n',
    ...     'temperature': '300',
    ...     'pressure': '1.0',
    ...     'thermostat': 'Langevin',
    ...     'nsteps': 1000,
    ...     'write_interval': 10,
    ...     'timestep': 0.5,
    ...     'log_interval': 100,
    ...     'print_ase_traj': 'y'
    ... }
    >>> mace_api(run_type='MD', config=config)
    """
    import sys
    import copy
    old_args = sys.argv
    try:
        sys.argv = ["amaceing_mace"]
        if run_type is not None:
            sys.argv.extend(["-rt", run_type])
        if config is not None:
            # Make a deep copy to avoid modifying the original
            config_copy = copy.deepcopy(config)
            
            # Handle the pbc_list special format
            if 'pbc_list' in config_copy and isinstance(config_copy['pbc_list'], list):
                config_copy['pbc_list'] = f"[{' '.join(str(x) for x in config_copy['pbc_list'])}]"
            
            # Handle special cases for MULTI_MD with lists
            if run_type == 'MULTI_MD':
                for key in ['foundation_model', 'model_size', 'dispersion_via_mace']:
                    if key in config_copy and isinstance(config_copy[key], list):
                        config_copy[key] = ' '.join(str(x).strip('"') for x in config_copy[key])
            
            # Handle special cases for FINETUNE_MULTIHEAD with lists
            if run_type == 'FINETUNE_MULTIHEAD':
                for key in ['train_file', 'xc_functional_of_dataset']:
                    if key in config_copy and isinstance(config_copy[key], list):
                        config_copy[key] = ' '.join(str(x).strip('"') for x in config_copy[key])
                
            sys.argv.extend(["-c", str(config_copy)])
        atk_mace()
    finally:
        sys.argv = old_args

def utils_api(run_type=None, config=None, logger=None):
    """
    API function for utilities
    
    Parameters
    ----------
    run_type : str, optional
        Type of utility to run ('EVAL_ERROR', 'PREPARE_EVAL_ERROR', 'EXTRACT_XYZ', 'MACE_CITATIONS', 'BENCHMARK')
    config : dict, optional
        Dictionary with the configuration parameters
    logger : str, optional
        Logger to display ('run', 'model', 'runexport')
        
    Returns
    -------
    None
        Runs the requested utility
        
    Examples
    --------
    >>> from amaceing_toolkit.workflow import utils_api
    >>> config = {
    ...     'ener_filename_ground_truth': 'dft_energies.xyz',
    ...     'force_filename_ground_truth': 'dft_forces.xyz',
    ...     'ener_filename_compare': 'mace_energies.txt',
    ...     'force_filename_compare': 'mace_forces.xyz'
    ... }
    >>> utils_api(run_type='EVAL_ERROR', config=config)
    """
    import sys
    import copy
    old_args = sys.argv
    try:
        sys.argv = ["amaceing_utils"]
        if run_type is not None:
            sys.argv.extend(["-rt", run_type])
        if config is not None:
            # Make a deep copy to avoid modifying the original
            config_copy = copy.deepcopy(config)
            
            # Handle the pbc_list special format for BENCHMARK
            if run_type == 'BENCHMARK' and 'pbc_list' in config_copy and isinstance(config_copy['pbc_list'], list):
                config_copy['pbc_list'] = f"[{' '.join(str(x) for x in config_copy['pbc_list'])}]"
            
            # Handle special multi-model formats for BENCHMARK
            if run_type == 'BENCHMARK':
                for key in ['mace_model', 'sevennet_model']:
                    if key in config_copy and isinstance(config_copy[key], list):
                        if isinstance(config_copy[key][0], list):  # Nested list case
                            formatted_list = []
                            for sublist in config_copy[key]:
                                formatted_list.append(f"[{' '.join(repr(x) for x in sublist)}]")
                            config_copy[key] = f"[{' '.join(formatted_list)}]"
                        else:  # Simple list case
                            config_copy[key] = f"[{' '.join(repr(x) for x in config_copy[key])}]"
            
            sys.argv.extend(["-c", str(config_copy)])
        if logger is not None:
            sys.argv.extend(["--logger", logger])
        atk_utils()
    finally:
        sys.argv = old_args

def mattersim_api(run_type=None, config=None):
    """
    API function for MatterSim input file creation
    
    Parameters
    ----------
    run_type : str, optional
        Type of calculation to run ('MD', 'MULTI_MD', 'FINETUNE', 'RECALC')
    config : dict, optional
        Dictionary with the configuration parameters
        
    Returns
    -------
    None
        Creates input files in the current directory
        
    Examples
    --------
    >>> from amaceing_toolkit.workflow import mattersim_api
    >>> config = {
    ...     'project_name': 'test_md',
    ...     'coord_file': 'system.xyz',
    ...     'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],  # Will be formatted correctly for the command line
    ...     'foundation_model': 'small',
    ...     'temperature': '300',
    ...     'pressure': '1.0',
    ...     'nsteps': 1000,
    ...     'write_interval': 10,
    ...     'timestep': 0.5,
    ... }
    >>> mattersim_api(run_type='MD', config=config)
    """
    import sys
    import copy
    old_args = sys.argv
    try:
        sys.argv = ["amaceing_mattersim"]
        if run_type is not None:
            sys.argv.extend(["-rt", run_type])
        if config is not None:
            # Make a deep copy to avoid modifying the original
            config_copy = copy.deepcopy(config)
            
            # Handle the pbc_list special format
            if 'pbc_list' in config_copy and isinstance(config_copy['pbc_list'], list):
                config_copy['pbc_list'] = f"[{' '.join(str(x) for x in config_copy['pbc_list'])}]"
            
            # Handle special cases for MULTI_MD with lists
            if run_type == 'MULTI_MD':
                for key in ['foundation_model']:
                    if key in config_copy and isinstance(config_copy[key], list):
                        config_copy[key] = ' '.join(str(x).strip('"') for x in config_copy[key])
                
            sys.argv.extend(["-c", str(config_copy)])
        atk_mattersim()
    finally:
        sys.argv = old_args

def sevennet_api(run_type=None, config=None):
    """
    API function for SevenNet input file creation
    
    Parameters
    ----------
    run_type : str, optional
        Type of calculation to run ('MD', 'MULTI_MD', 'FINETUNE', 'RECALC') 
    config : dict, optional
        Dictionary with the configuration parameters
        
    Returns
    -------
    None
        Creates input files in the current directory
        
    Examples
    --------
    >>> from amaceing_toolkit.workflow import sevennet_api
    >>> config = {
    ...     'project_name': 'test_md',
    ...     'coord_file': 'system.xyz',
    ...     'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0, 14.0],  # Will be formatted correctly for the command line
    ...     'foundation_model': '7net-0',
    ...     'modal': 'mpa',
    ...     'temperature': '300',
    ...     'pressure': '1.0',
    ...     'nsteps': 1000,
    ...     'write_interval': 10,
    ...     'timestep': 0.5,
    ... }
    >>> sevennet_api(run_type='MD', config=config)
    """
    import sys
    import copy
    old_args = sys.argv
    try:
        sys.argv = ["amaceing_sevennet"]
        if run_type is not None:
            sys.argv.extend(["-rt", run_type])
        if config is not None:
            # Make a deep copy to avoid modifying the original
            config_copy = copy.deepcopy(config)
            
            # Handle the pbc_list special format
            if 'pbc_list' in config_copy and isinstance(config_copy['pbc_list'], list):
                config_copy['pbc_list'] = f"[{' '.join(str(x) for x in config_copy['pbc_list'])}]"
            
            # Handle special cases for MULTI_MD with lists
            if run_type == 'MULTI_MD':
                for key in ['foundation_model', 'modal', 'dispersion_via_ase']:
                    if key in config_copy and isinstance(config_copy[key], list):
                        config_copy[key] = ' '.join(str(x).strip('"') for x in config_copy[key])
                
            sys.argv.extend(["-c", str(config_copy)])
        from .sevennet_input_writer import atk_sevennet
        atk_sevennet()
    finally:
        sys.argv = old_args

def analyzer_api(file=None, pbc=None, timestep=None, visualize=None):
    """
    API function for trajectory analysis
    
    Parameters
    ----------
    file : str, optional
        Path to trajectory file(s), comma separated for multiple files
    pbc : str, optional
        Path to PBC file(s), comma separated for multiple files
    timestep : float, optional
        Timestep in fs
    visualize : str, optional
        Whether to generate visualization ('y' or 'n')
        
    Returns
    -------
    None
        Creates analysis files and plots in the current directory
        
    Examples
    --------
    >>> from amaceing_toolkit.workflow import analyzer_api
    >>> analyzer_api(file='traj.xyz', pbc='pbc_file', timestep=50.0, visualize='y')
    """
    import sys
    old_args = sys.argv
    try:
        sys.argv = ["amaceing_ana"]
        if file is not None:
            sys.argv.extend(["--file", file])
        if pbc is not None:
            sys.argv.extend(["--pbc", pbc])
        if timestep is not None:
            sys.argv.extend(["--timestep", str(timestep)])
        if visualize is not None:
            sys.argv.extend(["--visualize", visualize])
        from ..trajec_ana import atk_analyzer
        atk_analyzer()
    finally:
        sys.argv = old_args

# Export API functions
__all__ = ["atk_cp2k", "atk_mace", "atk_mattersim", "atk_utils", "print_logo", "string_to_dict", 
           "string_to_dict_multi", "string_to_dict_multi2", "e0_wrapper", "frame_counter", 
           "cite_amaceing_toolkit", "create_dataset", "ask_for_float_int", "ask_for_int", 
           "ask_for_yes_no", "ask_for_yes_no_pbc", "extract_frames", "equi_to_md", "mace_citations",
           "cp2k_api", "mace_api", "utils_api", "mattersim_api", "sevennet_api", "analyzer_api"]
