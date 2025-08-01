import os
import sys
import argparse
import datetime
import textwrap
import numpy as np
from typing import Dict, Any, Optional, Union, List
import readline  # For command line input with tab completion
import glob # For file name tab completion

# Import utilities from the existing workflow
from .utils import print_logo  
from .utils import string_to_dict
from .utils import string_to_dict_multi
from .utils import string_to_dict_multi2
from .utils import cite_amaceing_toolkit
from .utils import ask_for_float_int
from .utils import ask_for_int
from .utils import ask_for_yes_no
from .utils import ask_for_yes_no_pbc
from .utils import ask_for_non_cubic_pbc
from .utils import create_dataset
from .utils import e0_wrapper
from .utils import frame_counter
from .utils import extract_frames

# Import the new generation input generators
from .input_ase import ASEInputGeneratorWrapper
from .input_lammps import LAMMPSInputGeneratorWrapper
from .input_ft import FTInputGenerator

# Import configurations and runscripts
from amaceing_toolkit.default_configs import configs_mace
from amaceing_toolkit.default_configs import configs_mattersim
from amaceing_toolkit.default_configs import configs_sevennet
from amaceing_toolkit.default_configs import configs_orb
from amaceing_toolkit.default_configs import configs_grace
from amaceing_toolkit.default_configs import e0s_functionals 
from amaceing_toolkit.default_configs import available_functionals

# Import model handling
from amaceing_toolkit.runs.model_logger import model_logger
from amaceing_toolkit.runs.model_logger import show_models
from amaceing_toolkit.runs.model_logger import get_model
from amaceing_toolkit.runs.run_logger import run_logger1

#todos:
## try it 
## add more frameworks until everyone is happy


class UniversalMLIPInputWriter:
    """
    Universal wrapper for generating MLIP input files across different frameworks and simulation environments.
    Supports MACE, SevenNet, MatterSim and ...
    Handles Q&A mode, terminal arguments, and proper config passing.
    """
    
    SUPPORTED_FRAMEWORKS = ['mace', 'sevennet', 'mattersim', 'new_mlip']
    SUPPORTED_RUN_TYPES = {
        'mace': {'simulation': ['GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'RECALC'], 'training': ['FINETUNE', 'FINETUNE_MULTIHEAD']},
        'mattersim': {'simulation': ['GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'RECALC'], 'training': ['FINETUNE']},
        'sevennet': {'simulation': ['GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'RECALC'], 'training': ['FINETUNE']},
        'orb': {'simulation': ['GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'RECALC'], 'training': ['FINETUNE']},
        'grace': {'simulation': ['GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'RECALC'], 'training': ['FINETUNE']},
        #'new_mlip': {'simulation': ['MD'], 'training': ['FINETUNE']},
    }
    SUPPORTED_SIM_ENVIRONMENTS = {
        'mace': ['ase', 'lammps'],
        'mattersim': ['ase'],  # MatterSim only supports ASE
        'sevennet': ['ase', 'lammps'],
        'orb': ['ase'],
        'grace': ['ase', 'lammps'],
        #'new_mlip': ['ase'],
    }

    def __init__(self):
        self.config = {}
        self.run_type = None
        self.framework = None
        self.simulation_environment = None
        self.no_questions = False
        
    def main(self):
        """
        Main entry point - decides between command line args or interactive Q&A
        """
        print_logo()
        
        if len(sys.argv) > 1:
            self.no_questions = True
            self._handle_command_line_args()
            
        else:
            self.no_questions = False
            self._interactive_mode()
            
        cite_amaceing_toolkit()
    
    def _handle_command_line_args(self):
        """Handle command line argument processing"""
        parser = self._create_argument_parser()
        args = parser.parse_args()
        
        if not args.config or args.config == ' ':
            print("Error: Configuration required when using command line mode.")
            return

        try:
            self._parse_config_from_args(args)
            self._execute_run()
        except Exception as e:
            print(f"Error processing command line arguments: {e}")
            print("Please check the configuration format.")

        # Write the log file
        self._write_log_file()

    
    def _create_argument_parser(self):
        """Create the argument parser with all supported options"""
        parser = argparse.ArgumentParser(
            description="MLIP input file generator: (1) Interactive Q&A: NO arguments needed! (2) Command line with dictionary: arguments required!",
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        parser.add_argument("-rt", "--run_type", type=str, 
                           help="[REQUIRED] Run type: 'GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'FINETUNE', 'FINETUNE_MULTIHEAD', 'RECALC'", 
                           required=True)
        
        parser.add_argument("-c", "--config", type=str, 
                           help=self._get_config_help_text(), 
                           required=True)
        
        return parser
    
    def _get_config_help_text(self):
        """Comprehensive help text for configuration options"""
        ft_framework = {
            'mace': "'project_name': 'NAME', 'train_file': 'FILE', 'device': 'cuda/cpu', 'stress_weight': 'FLOAT', 'forces_weight': 'FLOAT', 'energy_weight': 'FLOAT', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'prevent_catastrophic_forgetting': 'y/n', 'batch_size': 'INT', 'valid_fraction': 'FLOAT', 'valid_batch_size': 'INT', 'epochs': 'INT', 'seed': 'INT', 'lr': 'FLOAT', 'xc_functional_of_dataset': 'BLYP/PBE', 'dir': 'PATH'",
            'sevennet': "'project_name': 'NAME', 'train_file': 'FILE', 'foundation_model': 'NAME/PATH', 'modal': 'None/mpa/omat24', 'batch_size': 'INT', 'epochs': 'INT', 'seed': 'INT', 'force_loss_ratio': 'FLOAT', 'lr': 'FLOAT'",
            'mattersim': "'project_name': 'NAME', 'train_file': 'FILE', 'foundation_model': 'NAME/PATH', 'batch_size': 'INT', 'epochs': 'INT', 'seed': 'INT', 'force_loss_ratio': 'FLOAT', 'lr': 'FLOAT'",
            'orb': "'project_name': 'NAME', 'train_file': 'FILE', 'foundation_model': 'NAME/PATH', 'modal': 'small/medium/large/none', 'batch_size': 'INT', 'epochs': 'INT', 'seed': 'INT', 'lr': 'FLOAT'",
            'grace': "'project_name': 'NAME', 'train_file': 'FILE', 'foundation_model': 'NAME/PATH', 'batch_size': 'INT', 'epochs': 'INT', 'seed': 'INT', 'lr': 'FLOAT', 'force_loss_ratio': 'FLOAT'"
        }
        return textwrap.dedent("""
        Configuration dictionary for different run types:
        
        \033[1mGEO_OPT/CELL_OPT\033[0m: 
        "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[9 floats]', 'max_iter': 'INT', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'dispersion_via_simenv': 'y/n', 'simulation_environment': 'ase/lammps'}"
        
        \033[1mMD\033[0m: 
        "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[9 floats]', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'dispersion_via_simenv': 'y/n', 'temperature': 'FLOAT', 'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT', 'pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ext_traj': 'y/n', 'simulation_environment': 'ase/lammps'}"
        
        \033[1mMULTI_MD\033[0m: 
        "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[9 floats]', 'foundation_model': '['NAME/PATH', ...]', 'model_size': '['small/medium/large/none', ...]', 'dispersion_via_simenv': '['y/n', ...]', 'temperature': 'FLOAT', 'thermostat': 'THERMOSTAT', 'pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ext_traj': 'y/n', 'simulation_environment': 'ase/lammps'}"
        
        \033[1mFINETUNE\033[0m: 
        "{"""+ft_framework[self.framework]+"""}"
        
        \033[1mFINETUNE_MULTIHEAD\033[0m: 
        "{'project_name': 'NAME', 'train_file': '['FILE', ...]', 'device': 'cuda/cpu', 'stress_weight': 'FLOAT', 'forces_weight': 'FLOAT', 'energy_weight': 'FLOAT', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'batch_size': 'INT', 'valid_fraction': 'FLOAT', 'valid_batch_size': 'INT', 'epochs': 'INT', 'seed': 'INT', 'lr': 'FLOAT', 'xc_functional_of_dataset': '['FUNCTIONAL', ...]', 'dir': 'PATH'}"
        
        \033[1mRECALC\033[0m: 
        "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[9 floats]', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'dispersion_via_simenv': 'y/n', 'simulation_environment': 'ase/lammps'}"
        """)
    
    def _parse_config_from_args(self, args):
        """Parse configuration from command line arguments"""
        self.run_type = args.run_type

        # Framework is set by the chosen entry point

        # Flatten supported run types for checking
        supported_run_types = []
        for fw in self.SUPPORTED_RUN_TYPES:
            for mode in self.SUPPORTED_RUN_TYPES[fw]:
                supported_run_types.extend(self.SUPPORTED_RUN_TYPES[fw][mode])
        if self.run_type not in supported_run_types:
            raise ValueError(f"Unsupported run type ({self.run_type}) for chosen framework ({self.framework})")
        
        # Parse configuration based on run type
        if self.run_type == 'MULTI_MD':
            self.config = string_to_dict_multi(args.config)
        elif self.run_type == 'FINETUNE':
            self.config = string_to_dict(args.config)
            try:
                self.config['E0s'] = e0_wrapper(
                    e0s_functionals(self.config['xc_functional_of_dataset']), 
                    self.config['train_file'], 
                    self.config['xc_functional_of_dataset']
                )
            except KeyError:
                pass # E0s only for MACE
        elif self.run_type == 'FINETUNE_MULTIHEAD':
            self.config = string_to_dict_multi2(args.config)
            try:
                self.config['E0s'] = {}
                for head in range(len(self.config['train_file'])):
                    print(f"Processing head {head}")
                    self.config['E0s'][head] = e0_wrapper(
                        e0s_functionals(self.config['xc_functional_of_dataset'][head]), 
                        self.config['train_file'][head], 
                        self.config['xc_functional_of_dataset'][head]
                    )
            except KeyError:
                pass # E0s only for MACE
        else:
            self.config = string_to_dict(args.config)

        # Validate inputs
        self._validate_config()

        # Backward Compatibility: foundation and model_size or modal together in on list
        try: 
            if 'model_size' in self.config:
                self.config['foundation_model'] = [self.config['foundation_model'], self.config['model_size']]
                del self.config['model_size']
            elif 'modal' in self.config:
                self.config['foundation_model'] = [self.config['foundation_model'], self.config['modal']]
                del self.config['modal']
        except KeyError:
            pass
        
        # Set default simulation environment if not specified
        if self.run_type in self.SUPPORTED_RUN_TYPES[self.framework]['simulation']:
            if 'simulation_environment' not in self.config:
                self.config['simulation_environment'] = 'ase'
            self.simulation_environment = self.config['simulation_environment']

        # Handle PBC formatting
        if 'pbc_list' in self.config:
            if np.size(self.config['pbc_list']) == 3:  # Backward compatibility
                pbc = self.config['pbc_list']
                self.config['pbc_list'] = np.array([[pbc[0], 0, 0], [0, pbc[1], 0], [0, 0, pbc[2]]])
            else:
                self.config['pbc_list'] = np.array(self.config['pbc_list']).reshape(3, 3)

    
    def _interactive_mode(self):
        """Interactive Q&A mode for configuration"""
        print("\n")
        print(f"WELCOME TO THE {self.framework.upper()} INPUT WRITER!")
        print(f"This tool will help you build input files for the {self.framework} framework.")
        print("Please answer the following questions to build the input file.")
        print("\n")
        print("#########################################################################################")
        print("## Set defaults in the config file: /src/amaceing_toolkit/default_configs/*_configs.py ##")
        self.loaded_config = 'default'
        print(f"## Loading config: " + self.loaded_config + "                                                             ##")
        print("#########################################################################################")
        print("\n")
        
        # Load default configuration
        base_config = self._load_framework_config(self.loaded_config)
        
        # Ask for basic parameters
        coord_file = self._ask_for_coordinate_file(base_config)
        pbc_mat = self._ask_for_pbc_matrix(base_config)
        
        # Ask for run type
        self.run_type = self._ask_for_run_type(base_config)
        
        # Ask for simulation environment (for simulation runs)
        if self.run_type in self.SUPPORTED_RUN_TYPES[self.framework]['simulation']:
            if len(self.SUPPORTED_SIM_ENVIRONMENTS[self.framework]) == 1:
                self.simulation_environment = self.SUPPORTED_SIM_ENVIRONMENTS[self.framework][0]
            else:
                self.simulation_environment = self._ask_for_simulation_environment(base_config)
        else:
            self.simulation_environment = 'training'  # Training runs don't use sim environment
            
        # Ask for project name
        project_name = self._ask_for_project_name(self.run_type)
        
        # Run type specific configuration
        if self.run_type == 'FINETUNE':
            self._configure_finetune(coord_file, pbc_mat, project_name, base_config)
        elif self.run_type == 'FINETUNE_MULTIHEAD':
            self._configure_finetune_multihead(coord_file, pbc_mat, project_name, base_config)
        else:
            self._configure_simulation_run(coord_file, pbc_mat, project_name, base_config)

        # Execute the run
        self._execute_run()

        # Write the log file
        self._write_log_file()


    def _ask_for_coordinate_file(self, base_config: dict) -> str:
        """Ask for coordinate file (with tab-completion support if available)"""
        try:
            # Enable tab completion for file names, append '/' for directories
            def complete(text, state):
                matches = glob.glob(text + '*')
                # Append '/' if match is a directory
                matches = [
                    m + '/' if os.path.isdir(m) else m
                    for m in matches
                ]
                matches.append(None)
                return matches[state]

            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(complete)
        except ImportError:
            # If readline is not available, fallback to simple input
            pass

        while True:
            coord_file = input(f"What is the name of the coordinate file? [{base_config['coord_file']}]: ")
            if coord_file == '':
                coord_file = base_config['coord_file']

            if os.path.isfile(coord_file):
                return coord_file
            else:
                print(f"Coordinate file does not exist: {coord_file}. Please try again.")

        try:
            readline.set_completer(None)
        except Exception:
            pass

    def _ask_for_force_file(self, base_config: dict) -> str:
        """Ask for force file (with tab-completion support if available)"""
        try:
            # Enable tab completion for file names, append '/' for directories
            def complete(text, state):
                matches = glob.glob(text + '*')
                # Append '/' if match is a directory
                matches = [
                    m + '/' if os.path.isdir(m) else m
                    for m in matches
                ]
                matches.append(None)
                return matches[state]

            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(complete)
        except ImportError:
            # If readline is not available, fallback to simple input
            pass

        while True:
            force_file = input(f"What is the name of the force file? [{base_config['force_file']}]: ")
            if force_file == '':
                force_file = base_config['force_file']

            if os.path.isfile(force_file):
                return force_file
            else:
                print(f"Force file does not exist: {force_file}. Please try again.")

        try:
            readline.set_completer(None)
        except Exception:
            pass
    
    def _ask_for_pbc_matrix(self, base_config: dict) -> np.ndarray:
        """Ask for PBC matrix configuration"""
        box_cubic = ask_for_yes_no_pbc("Is the box cubic? (y/n/pbc)", base_config['box_cubic'])
        
        if box_cubic == 'y':
            box_xyz = ask_for_float_int("What is the length of the box in Å?", "10.0")
            pbc_mat = np.array([[box_xyz, 0.0, 0.0], [0.0, box_xyz, 0.0], [0.0, 0.0, box_xyz]])
        elif box_cubic == 'n':
            pbc_mat = ask_for_non_cubic_pbc()
        else:
            pbc_mat = np.loadtxt(box_cubic)
        
        return pbc_mat
    
    def _ask_for_run_type(self, base_config: dict) -> str:
        """Ask for run type"""
        run_types = []
        num_list = []
        for mode in self.SUPPORTED_RUN_TYPES.get(self.framework, {}):
            run_types.extend(self.SUPPORTED_RUN_TYPES[self.framework][mode])
        num_list.extend([str(i + 1) for i in range(len(run_types))])
        run_type_dict = {str(i + 1): rt for i, rt in enumerate(run_types)}

        legend = ""
        for i in num_list:
            legend += f"{i}={run_type_dict[i]}, "
        legend = legend[:-2] 
        
        run_type = ''
        while run_type not in num_list:
            prompt = (f"Which type of calculation do you want to run? ({legend}): [{base_config['run_type']}]: ")
            run_type = input(prompt)
            if run_type == '':
                run_type = base_config['run_type']
                break
            elif run_type not in num_list:
                print(f"Invalid input! Please enter {legend}.")
                
        if run_type in run_type_dict:
            return run_type_dict[run_type]
        else:
            return run_type  # Already converted from default
    
    def _ask_for_simulation_environment(self, base_config: dict) -> str:
        """Ask for simulation environment (ASE or LAMMPS)"""
        
        sim_env_default = base_config.get(self.run_type, {}).get('simulation_environment', 'ase')
        sim_env_default_dict = {'ase': 'y', 'lammps': 'n'}
        
        sim_env = ask_for_yes_no(
            "Do you want to use the ASE atomic simulation environment (y) or LAMMPS (n)? (y/n)", 
            sim_env_default_dict.get(sim_env_default, 'y')
        )
        
        if sim_env == 'y':
            print("You chose to create the input file for the ASE atomic simulation environment.")
            return 'ase'
        else:
            print("You chose to create the input file for LAMMPS.")
            return 'lammps'
    
    def _ask_for_project_name(self, run_type: str) -> str:
        """Ask for project name"""
        if run_type in ['FINETUNE', 'FINETUNE_MULTIHEAD']:
            project_name = input("What is the name of the model?: ")
        else:
            project_name = input("What is the name of the project?: ")
            
        if project_name == '':
            project_name = f'{run_type}_{datetime.datetime.now().strftime("%Y%m%d")}'
            
        return project_name
    
    def _configure_simulation_run(self, coord_file: str, pbc_mat: np.ndarray, project_name: str, base_config: dict):
        """Configure simulation runs (GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC)"""
        
        # Ask for default and only small changes
        self.config, use_default = self._default_config_loader()

        self.config['project_name'] = project_name
        self.config['coord_file'] = coord_file
        self.config['pbc_list'] = pbc_mat
        self.config['simulation_environment'] = self.simulation_environment

        if use_default == False:

            # Directly configure multi_md run
            if self.run_type == 'MULTI_MD':
                self._configure_multi_md_parameters(base_config)
                return

            # Ask for foundation model
            foundation_model, model_size = self._ask_for_foundation_model(base_config)
            if model_size is not None:
                self.config['foundation_model'] = [foundation_model, model_size]
            else:
                self.config['foundation_model'] = foundation_model
                
            # Ask for dispersion
            # Integration of dispersion correction is not available for all frameworks and simulation environments
            disp_avail = {'mace': ['ase'], 'sevennet': ['ase', 'lammps'], 'mattersim': []}
            if self.framework in disp_avail and self.simulation_environment in disp_avail[self.framework]:
                self.config['dispersion_via_simenv'] = ask_for_yes_no(
                    "Do you want to include dispersion correction? (y/n)", 
                    base_config.get(self.run_type, {}).get('dispersion_via_simenv', 'n')
                )
            else:
                print(f"Dispersion correction is not available for {self.framework} with {self.simulation_environment}.")
                self.config['dispersion_via_simenv'] = 'n'
            
            # Run type specific parameters
            if self.run_type in ['GEO_OPT', 'CELL_OPT']:
                self.config['max_iter'] = ask_for_int(
                    "What should be the maximum number of iterations?", 
                    str(base_config.get(self.run_type, {}).get('max_iter', 500))
                )
            elif self.run_type == 'MD':
                self._configure_md_parameters(base_config)
        
            # RECALC is already fully configured by the above parameters

        else: 
            foundation_model = self.config['foundation_model']
            model_size = self.config.get('model_size', None)
            if model_size is not None:
                self.config['foundation_model'] = [foundation_model, model_size]
            else:
                self.config['foundation_model'] = foundation_model

        return

    def _configure_md_parameters(self, base_config: dict):
        """Configure MD-specific parameters"""
        if self.run_type != 'MD':
            md_config = base_config.get('MULTI_MD', {})
        else:
            md_config = base_config.get('MD', {})
        
        self.config['temperature'] = ask_for_float_int(
            "Temperature in Kelvin:", str(md_config.get('temperature', 300))
        )
        
        # Thermostat selection
        thermostat_dict = {'1': 'Langevin', '2': 'NoseHooverChainNVT', '3': 'Bussi', '4': 'NPT'}
        thermostat_dict_reversed = {v: k for k, v in thermostat_dict.items()}
        thermostat = ''
        while thermostat not in ['1', '2', '3', '4']:
            thermostat = input(f"Which thermostat do you want to use (or NPT run)? (1=Langevin, 2=NoseHooverChainNVT, 3=Bussi, 4=NPT) [{thermostat_dict_reversed[self.config['thermostat']]}]: ")
            if thermostat not in ['1', '2', '3', '4']:
                print("Invalid input! Please enter '1', '2', '3', or '4'.")
        self.config['thermostat'] = thermostat_dict[thermostat]
        
        if self.config['thermostat'] == 'NPT':
            self.config['pressure'] = ask_for_float_int(
                "Pressure in bar:", str(md_config.get('pressure', 1.0))
            )
        else:
            self.config['pressure'] = None
            
        self.config['nsteps'] = ask_for_int(
            "Number of MD steps:", str(md_config.get('nsteps', 2000000))
        )
        self.config['timestep'] = ask_for_float_int(
            "Timestep in fs:", str(md_config.get('timestep', 0.5))
        )
        self.config['write_interval'] = ask_for_int(
            "Write interval of the trajectory:", str(md_config.get('write_interval', 10))
        )
        self.config['log_interval'] = ask_for_int(
            "Log interval:", str(md_config.get('log_interval', 100))
        )
        self.config['print_ext_traj'] = ask_for_yes_no(
            "Print extended trajectory? (y/n)", md_config.get('print_ext_traj', 'y')
        )
    
    def _configure_multi_md_parameters(self, base_config: dict):
        """Configure MULTI_MD parameters (multiple models)"""
               
        # Ask for multiple models
        num_models = ask_for_int("How many runs do you want to run?", "2")
        
        foundation_models = []
        dispersions = []
        
        for i in range(num_models):
            print(f"\nConfiguring model {i+1}:")
            foundation_model, model_size = self._ask_for_foundation_model(base_config)
            if model_size:
                self.config['foundation_model'] = [foundation_model, model_size]
            else:
                self.config['foundation_model'] = foundation_model
            
            disp_avail = {'mace': ['ase'], 'sevennet': ['ase', 'lammps'], 'mattersim': [], 'orb': ['ase'], 'grace': []}
            if self.framework in disp_avail and self.simulation_environment in disp_avail[self.framework]:
                dispersion = ask_for_yes_no(
                    f"Include dispersion for model {i+1}? (y/n)", 
                    base_config.get('dispersion_via_simenv', 'n')
                )
            else:
                print(f"Dispersion correction is not available for {self.framework} with {self.simulation_environment}.")
                dispersion = 'n'
            dispersions.append(dispersion)

        self.config['foundation_model'] = foundation_models
        self.config['dispersion_via_simenv'] = dispersions

        # Ask for parameters common to all runs
        print("Configuring common parameters for all models:")
        self._configure_md_parameters(base_config)
        
    
    def _configure_finetune(self, coord_file: str, pbc_mat: np.ndarray, project_name: str, base_config: dict):
        """Configure finetuning parameters"""
        # Ask if dataset needs to be created
        dataset_needed = ask_for_yes_no(
            "Do you want to create a training dataset from force & position files (y) or is it already defined (n)?", 
            'y'
        )
        
        if dataset_needed == 'y':
            force_file = self._ask_for_force_file(base_config['FINETUNE'])
            print("Creating the training dataset...")
            path_to_training_file = create_dataset(coord_file, force_file, pbc_mat)
        else:
            path_to_training_file = coord_file

        # Use only a fraction of the dataset
        smaller_dataset = ask_for_yes_no("Do you want to use only a fraction of the dataset (e.g. for testing purposes)? (y/n)", 'n')
        if smaller_dataset == 'y':
            dataset_fraction = ask_for_int("Which n-th frame do you want to use? (e.g. 10 means every 10th frame)", 10)
            if dataset_fraction != 1:
                path_to_training_file = extract_frames(path_to_training_file, dataset_fraction)
            no_frames = frame_counter(path_to_training_file)
            dataset_limit = int(ask_for_int(f"How many frames do you want to use of the {no_frames} available? (0 for all)", 0))
            if dataset_limit > 0 and dataset_limit < no_frames:
                # Extract the number of atoms
                with open(path_to_training_file, 'r') as file:
                    no_atoms = file.readline().strip()
                no_atoms = int(no_atoms.split()[0])
                no_lines = (no_atoms + 2) * dataset_limit
                # Read the first no_lines lines and write them into a new file
                with open(path_to_training_file, 'r') as file:
                    lines = file.readlines()[:no_lines]
                new_file_path = f"{path_to_training_file}_{dataset_limit}f.xyz"
                with open(new_file_path, 'w') as new_file:
                    new_file.writelines(lines)
                path_to_training_file = new_file_path
            else:
                print(f"Using the {no_frames} frames of the datase.")


        if self.framework == 'mace':
            self._configure_ft_mace(pbc_mat, project_name, path_to_training_file, base_config)
        elif self.framework == 'sevennet':
            self._configure_ft_sevennet(pbc_mat, project_name, path_to_training_file, base_config)
        elif self.framework == 'mattersim':
            self._configure_ft_mattersim(pbc_mat, project_name, path_to_training_file, base_config)
        elif self.framework == 'orb':
            self._configure_ft_orb(pbc_mat, project_name, path_to_training_file, base_config)
        elif self.framework == 'grace':
            self._configure_ft_grace(pbc_mat, project_name, path_to_training_file, base_config)
        else:
            raise ValueError(f"Unsupported framework for finetuning: {self.framework}")       

    def _configure_ft_mace(self, pbc_mat: np.ndarray, project_name: str, train_file: str, base_config: dict):
        """Configure finetuning parameters for MACE"""
        # Load default configuration
        self.config, use_default = self._default_config_loader()

        # Basic configuration
        self.config['project_name'] = project_name
        self.config['train_file'] = train_file

        if use_default == False:

            # Get foundation model
            foundation_model, model_size = self._ask_for_foundation_model(base_config)
            if model_size:
                self.config['foundation_model'] = [foundation_model, model_size]
            else:
                self.config['foundation_model'] = foundation_model

            # Ask for training parameters with defaults
            ft_config = base_config.get('FINETUNE', {})
            self.config.update({
                'device': 'cuda' if ask_for_yes_no("Use GPU (CUDA)? (y/n)", 'y') == 'y' else 'cpu',
                'energy_weight': ask_for_float_int("Energy weight:", str(ft_config.get('energy_weight', 1.0))),
                'forces_weight': ask_for_float_int("Forces weight:", str(ft_config.get('forces_weight', 10.0))),
                'stress_weight': ask_for_float_int("Stress weight:", str(ft_config.get('stress_weight', 0.0))),
                'batch_size': ask_for_int("Batch size:", str(ft_config.get('batch_size', 10))),
                'valid_fraction': ask_for_float_int("Validation fraction:", str(ft_config.get('valid_fraction', 0.1))),
                'epochs': ask_for_int("Maximum epochs:", str(ft_config.get('epochs', 100))),
                'lr': ask_for_float_int("Learning rate:", str(ft_config.get('lr', 0.01))),
                'seed': ask_for_int("Random seed:", str(ft_config.get('seed', 123))),
            })
            
            # Catastrophic forgetting prevention
            self.config['prevent_catastrophic_forgetting'] = ask_for_yes_no(
                "Prevent catastrophic forgetting? (y/n)", 'y'
            )

        # Get XC functional
        xc_functional = self._ask_for_xc_functional()
        self.config['xc_functional_of_dataset'] = xc_functional


        if xc_functional in available_functionals():
            self.config['E0s'] = e0_wrapper(
                e0s_functionals(xc_functional), 
                train_file, 
                xc_functional
            )
        else:
            print(f"Warning: E0s for the XC functional '{xc_functional}' not available. Have to be entered manually.")
            self.config['E0s'] = input("Please provide the E0s [eV] yourself for each element in the dataset in the following format: {1:-12.4830138479, ...}: ")
    

    def _configure_ft_sevennet(self, pbc_mat: np.ndarray, project_name: str, train_file: str, base_config: dict):
        """Configure finetuning parameters for SevenNet"""
        # Load default configuration
        self.config, use_default = self._default_config_loader()

        # Basic configuration
        self.config['project_name'] = project_name
        self.config['train_file'] = train_file

        if use_default == False:

            # Get foundation model
            print("Finetuning SevenNet is only available for the SevenNet-0 Model. This will be used.")
            foundation_model = '7net-0'
            # foundation_model, modal = self._ask_for_foundation_model(base_config)
            # if modal:
            #     self.config['foundation_model'] = [foundation_model, modal]
            # else:
            #     self.config['foundation_model'] = foundation_model

            # Ask for training parameters with defaults
            ft_config = base_config.get('FINETUNE', {})
            self.config.update({
                #'device': 'cuda' if ask_for_yes_no("Use GPU (CUDA)? (y/n)", 'y') == 'y' else 'cpu',
                'force_loss_ratio': ask_for_float_int("Force-Energy-Loss Ratio:", str(ft_config.get('force_loss_ratio', 10.0))),
                'batch_size': ask_for_int("Batch size:", str(ft_config.get('batch_size', 10))),
                'epochs': ask_for_int("Maximum epochs:", str(ft_config.get('epochs', 100))),
                'lr': ask_for_float_int("Learning rate:", str(ft_config.get('lr', 0.01))),
                'seed': ask_for_int("Random seed:", str(ft_config.get('seed', 123))),
            })
    
    def _configure_ft_mattersim(self, pbc_mat: np.ndarray, project_name: str, train_file: str, base_config: dict):
        """Configure finetuning parameters for MatterSim"""
        # Load default configuration
        self.config, use_default = self._default_config_loader()

        # Basic configuration
        self.config['project_name'] = project_name
        self.config['train_file'] = train_file

        if use_default == False:

            # Get foundation model
            foundation_model, _ = self._ask_for_foundation_model(base_config)
            self.config['foundation_model'] = foundation_model

            # Ask for training parameters with defaults
            ft_config = base_config.get('FINETUNE', {})
            self.config.update({
                'device': 'cuda' if ask_for_yes_no("Use GPU (CUDA)? (y/n)", 'y') == 'y' else 'cpu',
                'force_loss_ratio': ask_for_float_int("Force-Energy-Loss Ratio:", str(ft_config.get('force_loss_ratio', 10.0))),
                'batch_size': ask_for_int("Batch size:", str(ft_config.get('batch_size', 10))),
                'epochs': ask_for_int("Maximum epochs:", str(ft_config.get('epochs', 100))),
                'early_stopping': ask_for_yes_no("Do you want to allow an early stopping? (y/n)", str(ft_config.get('early_stopping', 'n'))),
                'save_checkpoint': ask_for_yes_no("Do you want to save checkpoints? (y/n)", str(ft_config.get('save_checkpoint', 'n'))),
                'ckpt_interval': ft_config.get('ckpt_interval', 25),
                'lr': ask_for_float_int("Learning rate:", str(ft_config.get('lr', 0.01))),
                'seed': ask_for_int("Random seed:", str(ft_config.get('seed', 123))),
            })

    def _configure_ft_orb(self, pbc_mat: np.ndarray, project_name: str, train_file: str, base_config: dict):
        """Configure finetuning parameters for Orb"""
        # Load default configuration
        self.config, use_default = self._default_config_loader()

        # Basic configuration
        self.config['project_name'] = project_name
        self.config['train_file'] = train_file

        if use_default == False:

            # Get foundation model
            foundation_model = "orb_v2"
            # print("Recommended foundation model for finetuning are: orb_v2 and orb_v3_conservative_inf_omat.")
            # foundation_model, modal = self._ask_for_foundation_model(base_config)
            # if modal:
            #     self.config['foundation_model'] = [foundation_model, modal]
            # else:
            #     self.config['foundation_model'] = foundation_model

            # Ask for training parameters with defaults
            ft_config = base_config.get('FINETUNE', {})
            self.config.update({
                #'device': 'cuda' if ask_for_yes_no("Use GPU (CUDA)? (y/n)", 'y') == 'y' else 'cpu',
                #'force_loss_ratio': ask_for_float_int("Force-Energy-Loss Ratio:", str(ft_config.get('force_loss_ratio', 10.0))),
                'batch_size': ask_for_int("Batch size:", str(ft_config.get('batch_size', 10))),
                'epochs': ask_for_int("Maximum epochs:", str(ft_config.get('epochs', 100))),
                'lr': ask_for_float_int("Learning rate:", str(ft_config.get('lr', 0.01))),
                'seed': ask_for_int("Random seed:", str(ft_config.get('seed', 123))),
            })

    def _configure_ft_grace(self, pbc_mat: np.ndarray, project_name: str, train_file: str, base_config: dict):
        """Configure finetuning parameters for Grace"""
        # Load default configuration
        self.config, use_default = self._default_config_loader()

        # Basic configuration
        self.config['project_name'] = project_name
        self.config['train_file'] = train_file

        if use_default == False:

            # Get foundation model
            foundation_model, modal = self._ask_for_foundation_model(base_config)
            self.config['foundation_model'] = foundation_model

            # Ask for training parameters with defaults
            ft_config = base_config.get('FINETUNE', {})
            self.config.update({
                'force_loss_ratio': ask_for_float_int("Force-Energy-Loss Ratio:", str(ft_config.get('force_loss_ratio', 10.0))),
                'batch_size': ask_for_int("Batch size:", str(ft_config.get('batch_size', 10))),
                'epochs': ask_for_int("Maximum epochs:", str(ft_config.get('epochs', 100))),
                'lr': ask_for_float_int("Learning rate:", str(ft_config.get('lr', 0.01))),
                'seed': ask_for_int("Random seed:", str(ft_config.get('seed', 123))),
            })


    def _configure_finetune_multihead(self, coord_file: str, pbc_mat: np.ndarray, project_name: str, base_config: dict):
        """Configure MACE multihead finetuning parameters"""
        num_heads = ask_for_int("How many heads (datasets) do you want to use?", "2")
        
        train_files = []
        xc_functionals = []
        e0s = []
        
        for i in range(num_heads):
            print(f"\nConfiguring head {i+1}:")
            
            # Ask for training file
            train_file = input(f"Path to training file for head {i+1}: ")
            train_files.append(train_file)
            
            # Ask for XC functional
            xc_functional = self._ask_for_xc_functional()

            # Get E0s
            if xc_functional in available_functionals():
                e0s.append(e0_wrapper(
                    e0s_functionals(xc_functional), 
                    train_file, 
                    xc_functional
                ))
            else:
                print(f"Warning: E0s for the XC functional '{xc_functional}' on head {i+1} not available. Have to be entered manually.")
                e0s.append(input("Please provide the E0s [eV] yourself for each element in the dataset in the following format: {1:-12.4830138479, ...}: "))          
        
        # Load default configuration
        self.config, use_default = self._default_config_loader(self)

        # Basic configuration
        self.config = {
            'project_name': project_name,
            'train_file': train_files,
            'prevent_catastrophic_forgetting': 'y', # Multihead finetuning enabled
        }
        
        if use_default == False:
            # Get foundation model
            foundation_model, model_size = self._ask_for_foundation_model(base_config)
            if model_size:
                self.config['foundation_model'] = [foundation_model, model_size]
            else:
                self.config['foundation_model'] = foundation_model
                
            # Ask for training parameters
            ft_config = base_config.get('FINETUNE_MULTIHEAD', {})
            self.config.update({
                'device': 'cuda' if ask_for_yes_no("Use GPU (CUDA)? (y/n)", 'y') == 'y' else 'cpu',
                'energy_weight': ask_for_float_int("Energy weight:", str(ft_config.get('energy_weight', 1.0))),
                'forces_weight': ask_for_float_int("Forces weight:", str(ft_config.get('forces_weight', 10.0))),
                'stress_weight': ask_for_float_int("Stress weight:", str(ft_config.get('stress_weight', 1.0))),
                'batch_size': ask_for_int("Batch size:", str(ft_config.get('batch_size', 10))),
                'valid_fraction': ask_for_float_int("Validation fraction:", str(ft_config.get('valid_fraction', 0.1))),
                'epochs': ask_for_int("Maximum epochs:", str(ft_config.get('epochs', 100))),
                'lr': ask_for_float_int("Learning rate:", str(ft_config.get('lr', 0.01))),
                'seed': ask_for_int("Random seed:", str(ft_config.get('seed', 123))),
            })
        

    def _load_framework_config(self, config_name: str) -> dict:
        """Load framework-specific configuration"""
        fct_name = f"configs_{self.framework}"
        if fct_name in globals():
            return globals()[fct_name](config_name)
        else:
            raise ValueError(f"Configuration for framework '{self.framework}' not found.")
    
    def _default_config_loader(self):
        """
        Load default configuration and optionally allow modifications
        """
        # Load framework-specific default configuration
        framework_config = self._load_framework_config(self.loaded_config)
    
        # Delete usless information: force_file, simulation_environment
        try: 
            del framework_config[self.run_type]['force_file']
        except KeyError:
            pass
        try:
            del framework_config[self.run_type]['simulation_environment']
        except KeyError:
            pass

        print("Default settings for this run type: ")
        items = list(framework_config[self.run_type].items())
        
        # Calculate max key and value lengths for formatting
        max_key_len = max(len(str(k)) for k, _ in items)
        max_val_len = max(len(str(v)) for _, v in items)
        col_width = max_key_len + max_val_len + 6  # extra space for ": " and padding

        for i in range(0, len(items), 3):
            line = "|| "
            for j in range(3):
                if i + j < len(items):
                    k, v = items[i + j]
                    pair_str = f"{k}: {v}"
                    # Pad each pair to col_width
                    line += pair_str.ljust(col_width)
            print(line.strip())

        use_default_input = ask_for_yes_no(
            "Do you want to use the default input settings? (y/n)", 
            framework_config.get('use_default_input', 'y')
        )
        
        if use_default_input == 'y':
            # Use default configuration directly
            config = framework_config[self.run_type].copy()
            return config, True
        elif len(items) == 1:
            # Do not ask a useless question if there is only one setting
            config = framework_config[self.run_type].copy()
            return config, False
        else:
            small_changes = ask_for_yes_no(
                "Do you want to make small changes to the default settings? (y/n)", 
                "n"
            )
            
            if small_changes == 'y':
                # Start with default config and allow modifications
                config = framework_config[self.run_type].copy()
                
                changing = True
                while changing:
                    # List of available settings
                    settings = list(config.keys())
                    
                    # Print the available settings with current values
                    print("\nAvailable settings:")
                    setting_number = 1
                    setting_number_list = []
                    for setting in settings:
                        print(f"({setting_number}) {setting}: {config[setting]}")
                        setting_number_list.append(str(setting_number))
                        setting_number += 1
                    
                    # Ask which setting to change
                    setting_to_change = ' '
                    while setting_to_change not in setting_number_list:
                        setting_to_change = input("Which setting do you want to change? (Enter the number): ")
                        if setting_to_change not in setting_number_list:
                            print(f"Invalid input! Please enter a number between 1 and {len(setting_number_list)}.")
                    
                    # Get the setting name
                    setting_name = settings[int(setting_to_change) - 1]
                    
                    # Ask for the new value with type-appropriate input handling
                    current_value = config[setting_name]
                    new_value = self._ask_for_setting_value(setting_name, current_value)
                    config[setting_name] = new_value
                    
                    print(f"Updated {setting_name} to: {new_value}")
                    
                    # Ask if user wants to change another setting
                    dict_onoff = {'y': True, 'n': False}
                    changing = dict_onoff[ask_for_yes_no("Do you want to change another setting? (y/n)", 'n')]
                
                return config, True
            else:
                # User wants to configure everything manually
                config = framework_config[self.run_type].copy()
                return config, False

    def _ask_for_setting_value(self, setting_name: str, current_value: Any) -> Any:
        """
        Ask for a new value for a specific setting, with type-appropriate handling
        """
        # Determine the type of the current value and ask accordingly
        if isinstance(current_value, bool):
            return ask_for_yes_no(
                f"New value for {setting_name} (current: {current_value}) (y/n): ",
                'y' if current_value else 'n'
            ) == 'y'
        
        elif isinstance(current_value, int):
            return ask_for_int(
                f"New value for {setting_name} (current: {current_value}): ",
                str(current_value)
            )
        
        elif isinstance(current_value, float):
            return ask_for_float_int(
                f"New value for {setting_name} (current: {current_value}): ",
                str(current_value)
            )
        
        elif isinstance(current_value, str):
            # Handle special cases for yes/no strings
            if current_value.lower() in ['y', 'n', 'yes', 'no']:
                return ask_for_yes_no(
                    f"New value for {setting_name} (current: {current_value}) (y/n): ",
                    current_value
                )
            else:
                new_value = input(f"New value for {setting_name} (current: {current_value}): ")
                return new_value if new_value else current_value
        
        elif isinstance(current_value, list):
            print(f"Current {setting_name}: {current_value}")
            new_value = input(f"New value for {setting_name} (enter as comma-separated values): ")
            if new_value:
                # Try to parse as list
                try:
                    # Handle different list types
                    if all(isinstance(x, str) for x in current_value):
                        return [x.strip().strip("'\"") for x in new_value.split(',')]
                    elif all(isinstance(x, int) for x in current_value):
                        return [int(x.strip()) for x in new_value.split(',')]
                    elif all(isinstance(x, float) for x in current_value):
                        return [float(x.strip()) for x in new_value.split(',')]
                    else:
                        return [x.strip() for x in new_value.split(',')]
                except ValueError:
                    print("Invalid format, keeping current value")
                    return current_value
            else:
                return current_value
        
        else:
            # Fallback for other types
            new_value = input(f"New value for {setting_name} (current: {current_value}): ")
            if new_value:
                # Try to convert to the same type as current value
                try:
                    return type(current_value)(new_value)
                except (ValueError, TypeError):
                    print(f"Could not convert to {type(current_value).__name__}, keeping as string")
                    return new_value
            else:
                return current_value

    def _ask_for_foundation_model(self, base_config: dict) -> tuple:
        """Ask for foundation model and size"""
        if self.framework == 'mace':
            return self._ask_for_mace_model(base_config)
        elif self.framework == 'sevennet':
            return self._ask_for_sevennet_model(base_config)
        elif self.framework == 'mattersim':
            return self._ask_for_mattersim_model(base_config)
        elif self.framework == 'orb':
            return self._ask_for_orb_model(base_config)
        elif self.framework == 'grace':
            return self._ask_for_grace_model(base_config)
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
    
    def _ask_for_mace_model(self, base_config: dict) -> tuple:
        """Ask for MACE foundation model"""
        model_options = {
            '1': 'mace_off',
            '2': 'mace_anicc',
            '3': 'mace_mp',
            '4': 'custom'
        }
        legend = ""
        for key, value in model_options.items():
            legend += f"{key}={value}, "
        legend = legend[:-2]
        foundation_model = ''
        while foundation_model not in model_options:
            foundation_model = input(f"Foundation model ({legend}): ")
            if foundation_model not in model_options:
                print(f"Invalid input! Please enter {legend}.")
        foundation_model = model_options[foundation_model]
                
        if foundation_model == 'custom':
            try:
                # Enable tab completion for file names, append '/' for directories
                def complete(text, state):
                    matches = glob.glob(text + '*')
                    # Append '/' if match is a directory
                    matches = [
                        m + '/' if os.path.isdir(m) else m
                        for m in matches
                    ]
                    matches.append(None)
                    return matches[state]

                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind("tab: complete")
                readline.set_completer(complete)
            except ImportError:
                pass
            custom_path = input("Path to custom model: ")
            try:
                readline.set_completer(None)
            except Exception:
                pass
            return custom_path, None
        
        model_size = None
        if foundation_model in ['mace_off', 'mace_mp']:
            size_options = {
                'mace_off': {
                    '1': 'small',
                    '2': 'medium',
                    '3': 'large',
                },
                'mace_mp': {
                    '1': 'small',
                    '2': 'medium',
                    '3': 'medium-mpa-0',
                    '4': 'large'
                }
            }

            legend = ""
            for key, value in size_options[foundation_model].items():
                legend += f"{key}={value}, "
            legend = legend[:-2]

            size = None
            while size not in size_options[foundation_model]:
                size = input(f"Model size ({legend}): ")
                if size not in size_options[foundation_model]:
                    print(f"Invalid input! Please enter one of the following: {legend}.")
            model_size = size_options[foundation_model][size]

        return foundation_model, model_size

    def _ask_for_sevennet_model(self, base_config: dict) -> tuple:
        """Ask for SevenNet foundation model"""
        model_options = {
            '1': '7net-mf-ompa',
            '2': '7net-omat',
            '3': '7net-l3i5',
            '4': '7net-0',
            '5': 'custom'
        }
        legend = ""
        for key, value in model_options.items():
            legend += f"{key}={value}, "
        legend = legend[:-2]
        foundation_model = ''
        while foundation_model not in model_options:
            foundation_model = input(f"Foundation model ({legend}): ")
            if foundation_model not in model_options:
                print(f"Invalid input! Please enter {legend}.")
        foundation_model = model_options[foundation_model]
                
        if foundation_model == 'custom':
            try:
                # Enable tab completion for file names, append '/' for directories
                def complete(text, state):
                    matches = glob.glob(text + '*')
                    # Append '/' if match is a directory
                    matches = [
                        m + '/' if os.path.isdir(m) else m
                        for m in matches
                    ]
                    matches.append(None)
                    return matches[state]

                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind("tab: complete")
                readline.set_completer(complete)
            except ImportError:
                pass
            show_models()
            custom_path = input("Number of presaved model or path to custom model: ")
            if custom_path.isdigit():
                custom_path = get_model(int(custom_path))
            try:
                readline.set_completer(None)
            except Exception:
                pass
            return custom_path, None
        
        modal = None
        if foundation_model == '7net-mf-ompa':
            modal_options = {
                '1': ['PBE52 (MP)', 'mpa'],
                '2': ['PBE54 (OMAT24)', 'omat24'],
            }

            legend = ""
            for key, value in modal_options.items():
                legend += f"{key}={value[0]}, "
            legend = legend[:-2]

            modal = None
            while modal not in modal_options:
                modal = input(f"Model size ({legend}): ")
                if modal not in modal_options:
                    print(f"Invalid input! Please enter one of the following: {legend}.")

            modal = modal_options[modal][1]

        return foundation_model, modal

    def _ask_for_orb_model(self, base_config: dict) -> tuple:
        """Ask for Orb foundation model"""
        model_options = {
            '1': 'orb_v2',
            '2': 'orb_v3_conservative_inf',
            '3': 'custom'
        }
        legend = ""
        for key, value in model_options.items():
            legend += f"{key}={value}, "
        legend = legend[:-2]
        foundation_model = ''
        while foundation_model not in model_options:
            foundation_model = input(f"Foundation model ({legend}): ")
            if foundation_model not in model_options:
                print(f"Invalid input! Please enter {legend}.")
        foundation_model = model_options[foundation_model]
                
        if foundation_model == 'custom':
            try:
                # Enable tab completion for file names, append '/' for directories
                def complete(text, state):
                    matches = glob.glob(text + '*')
                    # Append '/' if match is a directory
                    matches = [
                        m + '/' if os.path.isdir(m) else m
                        for m in matches
                    ]
                    matches.append(None)
                    return matches[state]

                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind("tab: complete")
                readline.set_completer(complete)
            except ImportError:
                pass
            show_models()
            custom_path = input("Number of presaved model or path to custom model: ")
            if custom_path.isdigit():
                custom_path = get_model(int(custom_path))
            try:
                readline.set_completer(None)
            except Exception:
                pass
            return custom_path, None
        
        modal = None
        if foundation_model == 'orb_v3_conservative_inf':
            modal_options = {
                '1': ['MP and Alexandria', 'mpa'],
                '2': ['OMAT24', 'omat'],
            }

            legend = ""
            for key, value in modal_options.items():
                legend += f"{key}={value[0]}, "
            legend = legend[:-2]

            modal = None
            while modal not in modal_options:
                modal = input(f"Model size ({legend}): ")
                if modal not in modal_options:
                    print(f"Invalid input! Please enter one of the following: {legend}.")

            modal = modal_options[modal][1]

        return foundation_model, modal
    
    def _ask_for_mattersim_model(self, base_config: dict) -> tuple:
        """Ask for MatterSim foundation model"""
        model_options = {
            '1': 'small',
            '2': 'large',
            '3': 'custom'
        }
        legend = ""
        for key, value in model_options.items():
            legend += f"{key}={value}, "
        legend = legend[:-2]
        foundation_model = ''
        while foundation_model not in model_options:
            foundation_model = input(f"Foundation model ({legend}): ")
            if foundation_model not in model_options:
                print(f"Invalid input! Please enter {legend}.")
        foundation_model = model_options[foundation_model]

        if foundation_model == 'custom':
            try:
                # Enable tab completion for file names, append '/' for directories
                def complete(text, state):
                    matches = glob.glob(text + '*')
                    # Append '/' if match is a directory
                    matches = [
                        m + '/' if os.path.isdir(m) else m
                        for m in matches
                    ]
                    matches.append(None)
                    return matches[state]

                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind("tab: complete")
                readline.set_completer(complete)
            except ImportError:
                pass
            custom_path = input("Path to custom model: ")
            try:
                readline.set_completer(None)
            except Exception:
                pass
            return custom_path, None
        else:
            return foundation_model, None

    def _ask_for_grace_model(self, base_config: dict) -> tuple:
        """Ask for GRACE foundation model"""
        model_options = {
            '1': 'GRACE-1L-OMAT',
            '2': 'GRACE-2L-OMAT',
            '3': 'GRACE-1L-OAM',
            '4': 'GRACE-2L-OAM',
            '5': 'custom'
        }
        legend = ""
        for key, value in model_options.items():
            legend += f"{key}={value}, "
        legend = legend[:-2]
        foundation_model = ''
        while foundation_model not in model_options:
            foundation_model = input(f"Foundation model ({legend}): ")
            if foundation_model not in model_options:
                print(f"Invalid input! Please enter {legend}.")
        foundation_model = model_options[foundation_model]
        
        if foundation_model == 'custom':
            try:
                # Enable tab completion for file names, append '/' for directories
                def complete(text, state):
                    matches = glob.glob(text + '*')
                    # Append '/' if match is a directory
                    matches = [
                        m + '/' if os.path.isdir(m) else m
                        for m in matches
                    ]
                    matches.append(None)
                    return matches[state]

                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind("tab: complete")
                readline.set_completer(complete)
            except ImportError:
                pass
            custom_path = input("Path to custom model (main folder of model): ")
            try:
                readline.set_completer(None)
            except Exception:
                pass
            return custom_path, None
        else:
            # Warning: Download
            print(f"WARNING: If your compute nodes are not connected to the internet, you have to download the foundation model manually using this command: 'grace_models download {foundation_model}'.")

            return foundation_model, None

    def _ask_for_xc_functional(self) -> str:
        """Ask for XC functional"""
        functionals = available_functionals()
        print("Available XC functionals:")
        for i, func in enumerate(functionals, 1):
            print(f"{i}: {func}")
            
        while True:
            try:
                choice = int(input("Select XC functional (number): ")) - 1
                if 0 <= choice < len(functionals):
                    return functionals[choice]
                else:
                    print("Invalid choice! Please select a valid number.")
            except ValueError:
                print("Invalid input! Please enter a number.")
    
    def _execute_run(self):
        """Execute the run based on configuration"""        
        if self.run_type in ['FINETUNE', 'FINETUNE_MULTIHEAD']:
            self._execute_training_run()
        elif self.run_type == 'MULTI_MD':
            # Backup copy of the original config
            original_config = self.config.copy()

            self.run_type = 'MD'  # Set run type to MD for multi-model runs

            if type(self.config['foundation_model'][0]) == list:
                # Create folder structure and parse the config for the single runs
                for i, model in enumerate(self.config['foundation_model'][0]):
                    print(f"Creating the input files for model {i+1} ({model}, {self.config['foundation_model'][1][i]}) in folder multi_md_run{i+1}...")
                    run_config = original_config.copy()
                    run_config['foundation_model'] = [self.config['foundation_model'][0][i], self.config['foundation_model'][1][i]] if isinstance(self.config['foundation_model'][0], list) else self.config['foundation_model'][i]
                    run_config['project_name'] = f"{self.config['project_name']}_model_{i+1}"
                    try:
                        run_config['dispersion_via_simenv'] = self.config['dispersion_via_simenv'][i]
                    except KeyError:
                        pass
                    # Create a subdirectory for each model
                    os.makedirs(f"multi_md_run{i+1}", exist_ok=True)
                    os.chdir(f"multi_md_run{i+1}")
                    self.config = run_config
                    self._execute_simulation_run()
                    os.chdir('..')
                    self.config = original_config
            else: 
                for i, model in enumerate(self.config['foundation_model']):
                    print(f"Creating the input files for model {i+1} ({model}) in folder multi_md_run{i+1}...")
                    run_config = original_config.copy()
                    run_config['foundation_model'] = model
                    run_config['project_name'] = f"{self.config['project_name']}_model_{i+1}"
                    try:
                        run_config['dispersion_via_simenv'] = self.config['dispersion_via_simenv'][i]
                    except KeyError:
                        pass
                    # Create a subdirectory for each model
                    os.makedirs(f"multi_md_run{i+1}", exist_ok=True)
                    os.chdir(f"multi_md_run{i+1}")
                    self.config = run_config
                    self._execute_simulation_run()
                    os.chdir('..')
                    self.config = original_config

            self.run_type = 'MULTI_MD'  # Reset run type to MULTI_MD
        else:
            self._execute_simulation_run()

    def _model_logger_wrapper(self):
        """Wrapper for model logging"""
        if np.size(self.config['foundation_model']) > 1:
            f_model = self.config['foundation_model'][0]
            f_model_size = self.config['foundation_model'][1]
        else:
            f_model = self.config['foundation_model']
            f_model_size = ' ' 
        loc_of_execution = os.getcwd()
        folder_dict = {
            'mace': self.config.get('dir', '.'),
            'sevennet': '.',
            'mattersim': self.config.get('save_path','MatterSim_models'),
            'orb': '.',
            'grace': f'seed/{self.config["seed"]}/final_model',
        }
        file_end_dict = {
            'mace': f'{self.config["project_name"]}_run-1.model',
            'sevennet': 'checkpoint_best.pth',
            'mattersim': 'best_model.pth',
            'orb': f'{self.config["project_name"]}.ckpt',
            'grace': '',
        }
        model_logger(
            os.path.join(loc_of_execution, folder_dict.get(self.framework, '.'), file_end_dict.get(self.framework, '')),
            self.config['project_name'],
            f_model,
            f_model_size,
            self.config['lr'],
            no_question=self.no_questions
        )

    def _execute_training_run(self):
        """Execute training runs (FINETUNE, FINETUNE_MULTIHEAD)"""
        if self.framework == 'mace':
            FTInputGenerator(self.config, self.run_type, self.framework).mace_ft()
        elif self.framework == 'sevennet':
            FTInputGenerator(self.config, self.run_type, self.framework).sevennet_ft()
        elif self.framework == 'mattersim':
            FTInputGenerator(self.config, self.run_type, self.framework).mattersim_ft()
        elif self.framework == 'orb':
            FTInputGenerator(self.config, self.run_type, self.framework).orb_ft()
        elif self.framework == 'grace':
            FTInputGenerator(self.config, self.run_type, self.framework).grace_ft()
        else:
            raise ValueError(f"Training not supported for framework: {self.framework}")
        
        # Log the model after training
        self._model_logger_wrapper()
        
    def _execute_simulation_run(self):
        """Execute simulation runs"""
        if self.simulation_environment == 'ase':
            self._execute_ase_simulation()
        elif self.simulation_environment == 'lammps':
            self._execute_lammps_simulation()
        else:
            raise ValueError(f"Unsupported simulation environment: {self.simulation_environment}")
    
    def _execute_ase_simulation(self):
        """Execute ASE simulation"""
        try:
            generator = ASEInputGeneratorWrapper(self.run_type, self.framework, self.config)
            filename = generator.run_and_save()
            
            # Handle recalc auto-execution
            if self.run_type == 'RECALC':
                if self.no_questions == False:
                    auto_run = ask_for_yes_no("Start the recalculation now? (y/n)", 'n')
                    if auto_run == 'y':
                        print("Starting recalculation...")
                        os.system(f"python {filename}")
                    
        except Exception as e:
            print(f"Error creating ASE input: {e}")
    
    def _execute_lammps_simulation(self):
        """Execute LAMMPS simulation"""
        try:
            generator = LAMMPSInputGeneratorWrapper(self.run_type, self.framework, self.config)
            filename = generator.run_and_save()
            
        except Exception as e:
            print(f"Error creating LAMMPS input: {e}")
    
    def _validate_config(self):
        """Validate the configuration dictionary"""
        required_params = {
            'GEOOPT': ['project_name', 'coord_file', 'pbc_list', 'max_iter', 'foundation_model', 'modal', 'model_size', 'dispersion_via_simenv'],
            'CELLOPT': ['project_name', 'coord_file', 'pbc_list', 'max_iter', 'foundation_model', 'modal', 'model_size', 'dispersion_via_simenv'],
            'MD': ['project_name', 'coord_file', 'pbc_list', 'foundation_model', 'modal', 'model_size', 'dispersion_via_simenv', 'temperature', 'thermostat', 'pressure', 'nsteps', 'timestep', 'write_interval', 'log_interval', 'print_ext_traj'],
            'RECALC': ['project_name', 'coord_file', 'pbc_list', 'foundation_model', 'modal', 'model_size', 'dispersion_via_simenv'],
            'FINETUNE_mace': ['project_name', 'train_file', 'foundation_model', 'xc_functional_of_dataset', 'E0s', 'device', 'energy_weight', 'forces_weight', 'stress_weight', 'batch_size', 'valid_fraction', 'valid_batch_size', 'epochs', 'lr', 'seed', 'dir', 'prevent_catastrophic_forgetting'],
            'FINETUNE_MULTIHEAD_mace': ['project_name', 'train_file', 'foundation_model', 'xc_functional_of_dataset', 'E0s', 'device', 'energy_weight', 'forces_weight', 'stress_weight', 'batch_size', 'valid_fraction', 'valid_batch_size', 'epochs', 'lr', 'seed', 'dir'],
            'FINETUNE_sevennet': ['project_name', 'train_file', 'foundation_model', 'modal', 'batch_size', 'epochs', 'seed', 'force_loss_ratio', 'lr'],
            'FINETUNE_mattersim': ['project_name', 'train_file', 'foundation_model', 'batch_size', 'epochs', 'seed', 'force_loss_ratio', 'lr'],
        }
        explain_params = {
            'project_name': 'Name of the project/model',
            'pbc_list': 'Periodic boundary conditions as a 9x1 matrix or path to pbc file',
            'foundation_model': 'Name of foundation model or path to a fine-tuned foundation model file',
            'modal': 'Modal for the foundation model (only needed for specific models of SevenNet)',
            'model_size': 'Size of the foundation model (only needed for specific models of MACE)',
            # Simulation parameters
            'coord_file': 'Path to the coordinate file (coord.xyz)',
            'dispersion_via_simenv': 'Whether to include dispersion correction via ASE',
            'max_iter': 'Maximum number of optimization iterations',
            'temperature': 'Temperature for MD simulation in Kelvin',
            'nsteps': 'Number of MD steps to run',
            'timestep': 'Timestep for MD simulation in femtoseconds',
            'write_interval': 'Interval for writing output files during MD',
            'log_interval': 'Interval for logging during MD',
            'print_ext_traj': 'Whether to print extended (ASE) trajectory information during MD',
            'pressure': 'Pressure for NPT MD simulation in bar (only needed for NPT, in bar)',
            'thermostat': 'Thermostat type for MD simulation',
            'simulation_environment': 'Simulation environment to use (ase or lammps)',
            # FT parameters
            'train_file': 'Path to the training file (train.xyz)',
            'xc_functional_of_dataset': 'XC functional used for the dataset',
            'E0s': 'E0s for the XC functional, provided as a dictionary',
            'device': 'Device to use for training (cpu or cuda)',
            'energy_weight': 'Weight for energy loss in training',
            'forces_weight': 'Weight for forces loss in training',
            'stress_weight': 'Weight for stress loss in training',
            'force_loss_ratio': 'Ratio of force loss to energy loss in training',
            'batch_size': 'Batch size for training',
            'valid_fraction': 'Fraction of data used for validation during training',
            'valid_batch_size': 'Batch size for validation during training',
            'epochs': 'Maximum number of epochs for training',
            'lr': 'Learning rate for training',
        }
        if self.run_type == 'FINETUNE':
            rt_val = f'FINETUNE_{self.framework.lower()}'
        elif self.run_type == 'FINETUNE_MULTIHEAD':
            rt_val = f'FINETUNE_MULTIHEAD_{self.framework.lower()}'
        else:
            rt_val = self.run_type.upper()

        if rt_val in required_params:
            for param in required_params[rt_val]:
                if param not in self.config:
                    if param == 'pressure' and self.config.get('thermostat') != 'NPT':
                        continue
                    elif param == 'dispersion_via_simenv' and self.framework in ['mattersim', 'grace']:
                        continue
                    elif param == 'modal' and self.framework not in ['sevennet', 'orb']:
                        continue
                    elif param == 'modal' and self.config['foundation_model'] != '7net-mf-ompa':
                        continue # Modal is only needed for 7net-mf-ompa
                    elif param == 'model_size' and self.framework != 'mace':
                        continue
                    elif param == 'model_size' and self.framework == 'mace' and '.' in self.config.get('foundation_model', ''):
                        continue # Custom models do not have a model size
                    else: 
                        raise ValueError(f"Missing required parameter: {param} ({explain_params.get(param, 'No explanation available')})")
        if self.run_type == 'FINETUNE':
            if not os.path.isfile(self.config['train_file']):
                raise FileNotFoundError(f"Training file not found: {self.config['train_file']}")
        elif self.run_type == 'FINETUNE_MULTIHEAD':
            for train_file in self.config['train_file']:
                if not os.path.isfile(train_file):
                    raise FileNotFoundError(f"Training file not found: {train_file}")
        else:
            if not os.path.isfile(self.config['coord_file']):
                raise FileNotFoundError(f"Coordinate file not found: {self.config['coord_file']}")

    def _write_log_file(self):
        """Write log file with configuration dictionary"""
        file_name = f"{self.framework}_{self.run_type.lower()}_input.log"
        
        input_config = self.config

        if self.run_type == 'MULTI_MD':
            if type(input_config['foundation_model'][0]) == list:
                # Create single log files for all runs
                for i in range(len(input_config['foundation_model'][0])):
                    with open(f'multi_md_run{i+1}/{self.framework}_md_input.log', 'w') as output:
                        output.write("Input file created with the following configuration:\n") 
                        # Copy the dict without the key 'foundation_model' and 'model_size'
                        input_config_tmp = input_config.copy()
                        input_config_tmp['foundation_model'] = input_config['foundation_model'][0][i]
                        input_config_tmp['model_size'] = input_config['foundation_model'][1][i]
                        try:
                            input_config_tmp['dispersion_via_simenv'] = input_config['dispersion_via_simenv'][i]
                        except KeyError:
                            pass
                        input_config_tmp['pbc_list'] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
                        output.write(f'"{input_config_tmp}"')  
            else:
                for i in range(len(input_config['foundation_model'])):
                    with open(f'multi_md_run{i+1}/{self.framework}_md_input.log', 'w') as output:
                        output.write("Input file created with the following configuration:\n") 
                        # Copy the dict without the key 'foundation_model' and 'model_size'
                        input_config_tmp = input_config.copy()
                        input_config_tmp['foundation_model'] = input_config['foundation_model'][i]
                        try:
                            input_config_tmp['dispersion_via_simenv'] = input_config['dispersion_via_simenv'][i]
                        except KeyError:
                            pass
                        input_config_tmp['pbc_list'] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
                        output.write(f'"{input_config_tmp}"')

        try:
            input_config["pbc_list"] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
        except:
            pass

        if self.run_type == 'MULTI_MD': 
            if np.logical_and(type(input_config['foundation_model']) == list, type(input_config['foundation_model'][0]) == list):
                foundation_model = input_config['foundation_model'][0]
                model_size = input_config['foundation_model'][1]
                # Build a string with the list elements separated by a space
                foundation_string = ' '.join(f"'{item}'" for item in foundation_model)
                foundation_string = f"'[{foundation_string}]'"
                input_config['foundation_model'] = foundation_string
                # Build a string with the list elements separated by a space
                model_size_string = ' '.join(f"'{item}'" for item in model_size)
                model_size_string = f"'[{model_size_string}]'"
                input_config['model_size'] = model_size_string
        else: 
            if type(input_config['foundation_model']) == list:
                input_config['model_size'] = input_config['foundation_model'][1]
                input_config['foundation_model'] = input_config['foundation_model'][0]
                
        
        try:
            if type(input_config['dispersion_via_simenv']) == list:
                # Build a string with the list elements separated by a space
                dispersion_string = ' '.join(f"'{item}'" for item in input_config['dispersion_via_simenv'])
                dispersion_string = f"'[{dispersion_string}]'"
                input_config['dispersion_via_simenv'] = dispersion_string
        except:
            pass

        # Delete the key-value pair of the key 'E0s' if it exists
        try:
            del input_config['E0s']
        except:
            pass

        # Check if the key 'train_file' is in the input_config
        if 'train_file' in input_config:
            # Check if the value of the key 'train_file' is a list
            if type(input_config['train_file']) == list:
                # build a string with the list elements separated by a space
                train_string = ' '.join(f"'{item}'" for item in input_config['train_file'])
                train_string = f"'[{train_string}]'"
                input_config['train_file'] = train_string

        try:
            input_config = str(input_config).replace('"', '')
        except:
            pass
        with open(file_name, 'w') as output:
            output.write("Input file created with the following configuration:\n")
            output.write(f'"{input_config}"')



def atk_mace():
    """
    Main entry function: MACE
    """
    writer = UniversalMLIPInputWriter()
    writer.framework = 'mace'
    writer.main()

def atk_mattersim():
    """
    Main entry function: MatterSim
    """
    writer = UniversalMLIPInputWriter()
    writer.framework = 'mattersim'
    writer.main()

def atk_sevennet():
    """
    Main entry function: SevenNet
    """
    writer = UniversalMLIPInputWriter()
    writer.framework = 'sevennet'
    writer.main()

def atk_orb():
    """
    Main entry function: Orb
    """
    writer = UniversalMLIPInputWriter()
    writer.framework = 'orb'
    writer.main()

def atk_grace():
    """
    Main entry function: Grace
    """
    writer = UniversalMLIPInputWriter()
    writer.framework = 'grace'
    writer.main()
