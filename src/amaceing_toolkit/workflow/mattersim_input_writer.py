import os
import numpy as np
import datetime
import sys
import argparse, textwrap


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
from amaceing_toolkit.runs.run_logger import run_logger1
from amaceing_toolkit.default_configs import configs_mattersim
from amaceing_toolkit.default_configs import mattersim_runscript 
from amaceing_toolkit.runs.model_logger import model_logger
from amaceing_toolkit.runs.model_logger import show_models
from amaceing_toolkit.runs.model_logger import get_model


def atk_mattersim():
    """
    Main function to write the input file for MatterSim
    """
    print_logo()

    # Decide if atk_mace is called with arguments or not
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Write input file for MatterSim runs and prepare them: (1) Via a short Q&A: NO arguments needed! (2) Directly from the command line with a dictionary: TWO arguments needed!", formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-rt", "--run_type", type=str, help="[OPTIONAL] Which type of calculation do you want to run? ('MD', 'MULTI_MD', 'FINETUNE', 'RECALC')", required=False)
        parser.add_argument("-c", "--config", type=str, help=textwrap.dedent("""[OPTIONAL] Dictionary with the configuration:\n 
        \033[1m MD \033[0m: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model' : 'small/large/PATH', 'dispersion_via_ase': 'y/n', 'temperature': 'FLOAT', 'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT','pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ase_traj': 'y/n'}"\n
        \033[1m MULTI_MD \033[0m: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model' : '['small/large/PATH' ...]', 'dispersion_via_ase': '['y/n' ...]', 'temperature': 'FLOAT', 'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT','pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ase_traj': 'y/n'}"\n
        \033[1m FINETUNE \033[0m: "{'project_name' : 'NAME', 'train_data_path': 'FILE', 'device': 'cuda/cpu', 'force_loss_ratio': 'FLOAT', 'load_model_path': 'small/large/PATH', 'y/n', 'batch_size': 'INT', 'epochs': 'INT', 'seed': 'INT', 'lr': 'FLOAT', 'save_checkpoint' : 'y', 'ckpt_interval': '25', 'save_path': 'PATH', 'early_stopping': 'n'}"\n
        \033[1m RECALC \033[0m: "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model': 'small/large/PATH', 'dispersion_via_ase': 'y/n'}'\n" """), required=False)
        args = parser.parse_args()
        if args.config != ' ':
            try:
                if args.run_type == 'MULTI_MD':
                    input_config = string_to_dict_multi(args.config)
                    if np.size(input_config['pbc_list']) == 3: # Keep compatibility with old input files
                        input_config['pbc_list'] = np.array([[input_config['pbc_list'][0], 0, 0], [0, input_config['pbc_list'][1], 0], [0, 0, input_config['pbc_list'][2]]])
                    else:
                        input_config['pbc_list'] = np.array(input_config['pbc_list']).reshape(3,3)
                    write_input(input_config, args.run_type)
                elif args.run_type == 'FINETUNE':
                    input_config = string_to_dict(args.config)
                    finetune_config = crt_config(input_config)
                else:
                    input_config = string_to_dict(args.config)
                    if np.size(input_config['pbc_list']) == 3: # Keep compatibility with old input files
                        input_config['pbc_list'] = np.array([[input_config['pbc_list'][0], 0, 0], [0, input_config['pbc_list'][1], 0], [0, 0, input_config['pbc_list'][2]]])
                    else:
                        input_config['pbc_list'] = np.array(input_config['pbc_list']).reshape(3,3)
                    write_input(input_config, args.run_type)


                with open('mattersim_input.log', 'w') as output:
                    output.write("Input file created with the following configuration:\n") 
                    output.write(f'"{args.config}"')

                if args.run_type == 'RECALC':
                    print('Starting the recalculation...')

                    print("""######################
## MATTERSIM OUTPUT ##
######################""")
                    
                    # Start the recalculation with python
                    os.system(f"python recalc_mattersim.py")
                
                elif args.run_type == 'FINETUNE':
                    write_runscript(input_config, args.run_type, finetune_config)

                else:
                    write_runscript(input_config, args.run_type)

                # Log the run
                run_logger1(args.run_type,os.getcwd())

                # Log the model
                if args.run_type == 'FINETUNE':
                    
                    name_of_model = f"{input_config['project_name']}.model"
                    location = os.path.join(os.getcwd(), input_config['save_path'], name_of_model)

                    model_logger(location, input_config['project_name'], input_config['load_model_path'], '', input_config['lr'], True)

            except KeyError:
                print("The dictionary is not in the right format. Please check the help page.")
    else:
        mattersim_form()
    
    cite_amaceing_toolkit()

def mattersim_form():
    """
    Function to ask the user for the input file for MatterSim
    """

    print("\n")
    print("Welcome to the MatterSim input file writer!")
    print("This tool will help you build input files for MatterSim calculations.")
    print("Please answer the following questions to build the input file.")
    print("#####################################################################################################")
    print("## Defaults are set in the config file: /src/amaceing_toolkit/default_configs/mattersim_configs.py ##")
    print("## For more advanced options, please edit the resulting input file.                                ##")
    loaded_config = 'default'
    mattersim_config = configs_mattersim(loaded_config)
    print(f"## Loading config: " + loaded_config + "                                                                         ##")
    print("#####################################################################################################")
    print("\n")

    # Ask user for input data
    coord_file = input("What is the name of the coordinate file (or reference trajecory/training file)? " +"[" + mattersim_config['coord_file'] + "]: ")
    if coord_file == '':
        coord_file = mattersim_config['coord_file']
    assert os.path.isfile(coord_file), "Coordinate file does not exist!"
    
    box_cubic = ask_for_yes_no_pbc("Is the box cubic? (y/n/pbc)", mattersim_config['box_cubic'])

    if box_cubic == 'y':
        box_xyz = ask_for_float_int("What is the length of the box in Å?", str(10.0))
        pbc_mat = np.array([[box_xyz, 0.0, 0.0],[0.0, box_xyz, 0.0],[0.0, 0.0, box_xyz]])
    elif box_cubic == 'n':
        pbc_mat = ask_for_non_cubic_pbc()
    else:
        pbc_mat = np.loadtxt(box_cubic)


    # Ask the user for the run type
    run_type_dict = {'1': 'MD', '2': 'MULTI_MD', '3': 'FINETUNE', '4': 'RECALC'}
    run_type = ' '
    while run_type not in ['1', '2', '3', '4','']:
        run_type = input("Which type of calculation do you want to run? (1=MD, 2=MULTI_MD, 3=FINETUNE, 4=RECALC): " + "[" + mattersim_config['run_type'] + "]: ")
        if run_type not in ['1', '2', '3', '4','']:
            print("Invalid input! Please enter '1', '2', '3' or '4'.")
    if run_type == '':
        run_type = mattersim_config['run_type']
    else:
        run_type = run_type_dict[run_type]

    if run_type == 'FINETUNE':
        project_name = input("What is the name of the final model?: ")
    else:
        project_name = input("What is the name of the project?: ")
    if project_name == '':
        project_name = f'{run_type}_{datetime.datetime.now().strftime("%Y%m%d")}'

    # Ask for the fine-tune settings 
    if run_type == 'FINETUNE':
        dataset_needed = ask_for_yes_no("Do you want to create a training dataset from a force & a position file (y) or did you define it already (n)?", 'y')
        if dataset_needed == 'y':
            print("Creating the training dataset...")
            path_to_training_file = dataset_creator(coord_file, pbc_mat, run_type, mattersim_config)      
            
        else: 
            # The given file is the training file
            path_to_training_file = coord_file

        # Use only a fraction of the dataset
        smaller_dataset = ask_for_yes_no("Do you want to use only a fraction of the dataset (e.g. for testing purposes)? (y/n)", 'n')
        if smaller_dataset == 'y':
            dataset_fraction = ask_for_int("Which n-th frame do you want to use? (e.g. 10 means every 10th frame)", 10)
            path_to_training_file = extract_frames(path_to_training_file, dataset_fraction)


    print("Default settings for this run type: " + str(mattersim_config[run_type]))

    use_default_input = ask_for_yes_no("Do you want to use the default input settings? (y/n)", mattersim_config['use_default_input'])
    if use_default_input == 'y':
        if run_type == 'FINETUNE':
            input_config = config_wrapper(True, run_type, mattersim_config, coord_file, pbc_mat, project_name, path_to_training_file)
        else:
            input_config = config_wrapper(True, run_type, mattersim_config, coord_file, pbc_mat, project_name)
    else:
        small_changes = ask_for_yes_no("Do you want to make small changes to the default settings? (y/n)", "n")
        if small_changes == 'y':

            changing = True
            while changing:
                # List of mattersim_config[run_type] keys:
                settings = list(mattersim_config[run_type].keys())

                # Print the available settings with the default value
                print("Available settings:")
                setting_number = 1
                setting_number_list = []
                for setting in settings:
                    print(f"({setting_number}) {setting}: {mattersim_config[run_type][setting]}")
                    setting_number_list.append(str(setting_number))
                    setting_number += 1
                
                # Ask which settings the user wants to change
                setting_to_change = ' '
                while setting_to_change not in setting_number_list:
                    setting_to_change = input("Which setting do you want to change? (Enter the number): ")
                    if setting_to_change not in setting_number_list:
                        print("Invalid input! Please enter a number between 1 and " + str(len(setting_number_list)) + ".")
                    
                # Ask for the new value of the setting
                new_value = input(f"What is the new value for {settings[int(setting_to_change) - 1]}? ")
                mattersim_config[run_type][settings[int(setting_to_change) - 1]] = new_value

                # Change another setting?
                dict_onoff = {'y': True, 'n': False}
                changing = dict_onoff[ask_for_yes_no("Do you want to change another setting? (y/n)", 'n')]
            
            if run_type == 'FINETUNE':
                input_config = config_wrapper(True, run_type, mattersim_config, coord_file, pbc_mat, project_name, path_to_training_file)
            else:
                input_config = config_wrapper(True, run_type, mattersim_config, coord_file, pbc_mat, project_name)

        else: 
            if run_type == 'FINETUNE':
                input_config = config_wrapper(False, run_type, mattersim_config, coord_file, pbc_mat, project_name, path_to_training_file)
            else:
                input_config = config_wrapper(False, run_type, mattersim_config, coord_file, pbc_mat, project_name)

    if run_type == 'FINETUNE':
        input_config['train_data_path'] = review_training_file(input_config['train_data_path'])

        finetune_config = crt_config(input_config)
        
        write_runscript(input_config, run_type, finetune_config)

        write_log(input_config)

        run_logger1(run_type,os.getcwd())

        # Log the model
        loc_of_execution = os.getcwd()
        loc_of_model = input_config['save_path']
        name_of_model = f"{input_config['project_name']}.model"
        location = os.path.join(loc_of_execution, loc_of_model, name_of_model)

        model_logger(location, input_config['project_name'], input_config['load_model_path'], '', input_config['lr'])
    
    elif run_type == 'RECALC':
        
        write_input(input_config, run_type)
        
        print('Starting the recalculation...')

        print("""######################
## MATTERSIM OUTPUT ##
######################""")
        
        # Start the recalculation with python
        os.system(f"python recalc_mattersim.py")

        # Write the configuration to a log file
        write_log(input_config)

        # Log the run
        run_logger1(run_type,os.getcwd())
    
    else:
        # Write the input file
        write_input(input_config, run_type)

        # Write the runscript
        write_runscript(input_config, run_type) 

        # Write the configuration to a log file
        write_log(input_config)

        # Log the run
        run_logger1(run_type,os.getcwd())

            
    # Citations of MatterSim (until now not necessary)
    # mattersim_citations()

def config_wrapper(default, run_type, mattersim_config, coord_file, pbc_mat, project_name, path_to_training_file="", e0_dict={}):

    """
    Wrapper function to create the input file
    """

    # Use default input data
    if default == True:
        if run_type == 'MD': 
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': mattersim_config[run_type]['foundation_model'],
                            #'dispersion_via_ase': mattersim_config[run_type]['dispersion_via_ase'],
                            'temperature': mattersim_config[run_type]['temperature'],
                            'pressure': mattersim_config[run_type]['pressure'],
                            'thermostat': mattersim_config[run_type]['thermostat'],
                            'nsteps': mattersim_config[run_type]['nsteps'],
                            'write_interval': mattersim_config[run_type]['write_interval'],
                            'timestep': mattersim_config[run_type]['timestep'],
                            'log_interval': mattersim_config[run_type]['log_interval'],
                            'print_ase_traj': mattersim_config[run_type]['print_ase_traj']}
        elif run_type == 'MULTI_MD': 
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': mattersim_config[run_type]['foundation_model'], # List
                            #'dispersion_via_ase': mattersim_config[run_type]['dispersion_via_ase'], # List
                            'temperature': mattersim_config[run_type]['temperature'],
                            'pressure': mattersim_config[run_type]['pressure'],
                            'thermostat': mattersim_config[run_type]['thermostat'],
                            'nsteps': mattersim_config[run_type]['nsteps'],
                            'write_interval': mattersim_config[run_type]['write_interval'],
                            'timestep': mattersim_config[run_type]['timestep'],
                            'log_interval': mattersim_config[run_type]['log_interval'],
                            'print_ase_traj': mattersim_config[run_type]['print_ase_traj']}
        elif run_type == 'FINETUNE':
            input_config = {'project_name': project_name,
                            'train_data_path': path_to_training_file, 
                            'device': mattersim_config[run_type]['device'],
                            'force_loss_ratio': mattersim_config[run_type]['force_loss_ratio'],
                            'load_model_path': mattersim_config[run_type]['load_model_path'],
                            'batch_size': mattersim_config[run_type]['batch_size'],
                            'save_checkpoint': mattersim_config[run_type]['save_checkpoint'],
                            'ckpt_interval': mattersim_config[run_type]['ckpt_interval'],
                            'epochs': mattersim_config[run_type]['epochs'],
                            'seed': mattersim_config[run_type]['seed'],
                            'lr': mattersim_config[run_type]['lr'], 
                            'save_path': mattersim_config[run_type]['save_path'],
                            'early_stopping': mattersim_config[run_type]['early_stopping']}
        elif run_type == 'RECALC':
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': mattersim_config[run_type]['foundation_model']}
                            #'dispersion_via_ase': mattersim_config[run_type]['dispersion_via_ase']}
            
    # Ask user for input data
    else:
        if run_type == 'MD': 
            
            foundation_model = ask_for_foundational_model(mattersim_config, run_type)
            #dispersion_via_ase = ask_for_yes_no("Do you want to include dispersion via ASE? (y/n)", mattersim_config[run_type]['dispersion_via_ase'])
            thermostat = ask_for_int("What thermostat do you want to use (or NPT run)? (1: Langevin, 2: NoseHooverChainNVT, 3: Bussi, 4: NPT): ", mattersim_config[run_type]['thermostat'])
            thermo_dict = {'1': 'Langevin', '2': 'NoseHooverChainNVT', '3': 'Bussi', '4': 'NPT'}
            thermostat = thermo_dict[thermostat]
            temperature = ask_for_float_int("What is the temperature in Kelvin?", mattersim_config[run_type]['temperature'])
            if thermostat == 'NPT':
                pressure = ask_for_float_int("What is the pressure in bar?", mattersim_config[run_type]['pressure'])
            else: 
                pressure = ' '
            nsteps = ask_for_int("How many steps do you want to run?", mattersim_config[run_type]['nsteps'])
            write_interval = ask_for_int("How often do you want to write the trajectory?", mattersim_config[run_type]['write_interval'])
            timestep = ask_for_float_int("What is the timestep in fs?", mattersim_config[run_type]['timestep'])
            log_interval = ask_for_int("How often do you want to write the log file?", mattersim_config[run_type]['log_interval'])
            print_ase_traj = ask_for_yes_no("Do you want to print the ASE trajectory? (y/n)", mattersim_config[run_type]['print_ase_traj'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model,
                            #'dispersion_via_ase': dispersion_via_ase,
                            'temperature': temperature,
                            'pressure': pressure,
                            'thermostat': thermostat,
                            'nsteps': nsteps,
                            'write_interval': write_interval,
                            'timestep': timestep,
                            'log_interval': log_interval,
                            'print_ase_traj': print_ase_traj}

            
        elif run_type == 'MULTI_MD': 
            
            no_runs = ask_for_int("How many MD runs do you want to perform?")
            foundation_model = []
            #dispersion_via_ase = []
            for i in range(no_runs):
                foundation_model_tmp = ask_for_foundational_model(mattersim_config, run_type)
                #dispersion_via_ase_tmp = ask_for_yes_no("Do you want to include dispersion via ASE? (y/n)", mattersim_config[run_type]['dispersion_via_ase'])
                foundation_model.append(foundation_model_tmp)
                #dispersion_via_ase.append(dispersion_via_ase_tmp)
            thermostat = ask_for_int("What thermostat do you want to use (or NPT run)? (1: Langevin, 2: NoseHooverChainNVT, 3: Bussi, 4: NPT): ", mattersim_config[run_type]['thermostat'])
            thermo_dict = {'1': 'Langevin', '2': 'NoseHooverChainNVT', '3': 'Bussi', '4': 'NPT'}
            thermostat = thermo_dict[thermostat]
            temperature = ask_for_float_int("What is the temperature in Kelvin?", mattersim_config[run_type]['temperature'])
            if thermostat == 'NPT':
                pressure = ask_for_float_int("What is the pressure in bar?", mattersim_config[run_type]['pressure'])
            else: 
                pressure = ' '
            nsteps = ask_for_int("How many steps do you want to run?", mattersim_config[run_type]['nsteps'])
            write_interval = ask_for_int("How often do you want to write the trajectory?", mattersim_config[run_type]['write_interval'])
            timestep = ask_for_float_int("What is the timestep in fs?", mattersim_config[run_type]['timestep'])
            log_interval = ask_for_int("How often do you want to write the log file?", mattersim_config[run_type]['log_interval'])
            print_ase_traj = ask_for_yes_no("Do you want to print the ASE trajectory? (y/n)", mattersim_config[run_type]['print_ase_traj'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model, # List
                            'temperature': temperature,
                            'pressure': pressure,
                            'thermostat': thermostat,
                            'nsteps': nsteps,
                            'write_interval': write_interval,
                            'timestep': timestep,
                            'log_interval': log_interval,
                            'print_ase_traj': print_ase_traj}


        elif run_type == 'FINETUNE':
            
            foundation_model = ask_for_foundational_model(mattersim_config, run_type)
            batch_size = ask_for_int("What is the batch size?", mattersim_config[run_type]['batch_size'])
            device = ''
            while device not in ['cuda', 'cpu']:
                device = input("What is the device? (cuda/cpu) [" + mattersim_config[run_type]['device'] + "]: ")
                if device == '':
                    device = mattersim_config[run_type]['device']
            epochs = ask_for_int("What is the maximum number of epochs?", mattersim_config[run_type]['epochs'])
            seed = ask_for_int("What is the seed?", mattersim_config[run_type]['seed'])
            lr = ask_for_float_int("What is the learning rate?", mattersim_config[run_type]['lr'])
            save_path = ''
            save_path = input("What is the directory for the model? [" + mattersim_config[run_type]['save_path'] + "]: ")
            if save_path == '':
                save_path = mattersim_config[run_type]['save_path']
            early_stopping = ask_for_yes_no("Do you want to allow early stopping? (y/n)", mattersim_config[run_type]['early_stopping'])


            input_config = {'project_name': project_name,
                            'train_data_path': path_to_training_file, 
                            'device': device,
                            'force_loss_ratio': mattersim_config[run_type]['force_loss_ratio'],
                            'load_model_path': foundation_model,
                            'batch_size': batch_size,
                            'save_checkpoint': mattersim_config[run_type]['save_checkpoint'],
                            'ckpt_interval': mattersim_config[run_type]['ckpt_interval'],
                            'epochs': epochs,
                            'seed': seed,
                            'lr': lr, 
                            'save_path': save_path,
                            'early_stopping': early_stopping}

            
        elif run_type == 'RECALC':
            
            foundation_model = ask_for_foundational_model(mattersim_config, run_type)
            #dispersion_via_ase = ask_for_yes_no("Do you want to include dispersion via ASE? (y/n)", mattersim_config[run_type]['dispersion_via_ase'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model}
                            #'dispersion_via_ase': dispersion_via_ase}
    return input_config


def create_input(input_config, run_type):
    """
    Function to create the input file
    """

    if run_type == 'MD':
        return f"""
import time
import numpy as np
import os
import torch
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import write
from ase.io import read
from ase.md import MDLogger
from mattersim.forcefield import MatterSimCalculator
{thermostat_code(input_config)[0]}

# Set the device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the foundation model
mattersim_calc = MatterSimCalculator({foundation_model_path(input_config['foundation_model'])}, device=device)
print("Loading of MatterSim model completed: {input_config['foundation_model']} model")

# Load the coordinates (take care if it is the first start or a restart)
if os.path.isfile('{input_config['project_name']}.traj'):
    atoms = read('{input_config['project_name']}.traj')
    #atoms = read('{input_config['project_name']}_restart.traj')
else:
    atoms = read('{input_config['coord_file']}')			

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({cell_matrix(input_config['pbc_list'])})

atoms.calc = mattersim_calc

# Set the temperature in Kelvin and initialize the velocities (only if it is the first start)
temperature_K = {int(input_config['temperature'])}
if os.path.isfile('{input_config['project_name']}.traj') == False:
    MaxwellBoltzmannDistribution(atoms, temperature_K = temperature_K) 


# Thermostat and/or barostat
{thermostat_code(input_config)[1]}
dyn.fixcm = True

{write_log_file(input_config)}

{write_traj_file(input_config)}

# Write the xyz trajectory
def write_xyz():
    write('{input_config['project_name']}_pos.xyz', atoms, format='xyz', append=True)
dyn.attach(write_xyz, interval={int(input_config['write_interval'])})

start_time = time.time()
dyn.run({int(input_config['nsteps'])})
end_time = time.time()

# Calculate the runtime
runtime = end_time - start_time
print("Function runtime: "+ str(runtime) + " seconds")
np.savetxt("md_runtime.txt", [runtime])

# Write the final coordinates
write('{input_config['project_name']}_restart.traj', atoms)

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    elif run_type == 'RECALC':
        return f"""
from mattersim.forcefield import MatterSimCalculator
import torch
import time
import numpy as np
from ase import build
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import write
from ase.io import read

# Set the device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the foundation model
mattersim_calc = MatterSimCalculator({foundation_model_path(input_config['foundation_model'])}, device=device)
print("Loading of MatterSim model completed: {input_config['foundation_model']} model")

# Load the reference trajectory
trajectory = read('{input_config['coord_file']}', index=':')

# Initialize a list to store forces for each frame
all_forces = []
all_energies = []
frame_counter = 0

# Loop over each frame and calculate forces
for atoms in trajectory:
    if frame_counter % 25 == 0:
        print(frame_counter)
    frame_counter += 1
    atoms.pbc = (True, True, True)
    atoms.set_cell({cell_matrix(input_config['pbc_list'])})
    atoms.calc = mattersim_calc
    forces = atoms.get_forces()
    all_forces.append(forces)
    energies = atoms.get_total_energy()
    all_energies.append(energies)

# Saving the energies and forces to files
all_forces = np.array(all_forces)
np.savetxt("energies_recalc_with_mattersim_model_{input_config['project_name']}", all_energies)
atom = trajectory[0].get_chemical_symbols()
atom = np.array(atom)
with open('forces_recalc_with_mattersim_model_{input_config['project_name']}.xyz', 'w') as f: """+r"""
    for i in range(0, all_forces.shape[0]):
        f.write(f"{len(atom)} \n")
        f.write(f"# Frame {i}\n")
        for j in range(0, len(atom)):
            f.write('%s %f %f %f \n' % (atom[j], all_forces[i][j][0], all_forces[i][j][1], all_forces[i][j][2]))
"""+f"""
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""


def thermostat_code(input_config):
    """
    Function to return the thermostat code
    """
    thermostat = input_config['thermostat']
    if thermostat == 'Langevin':
        return "from ase.md import Langevin", f"""
dyn = Langevin(atoms, {float(input_config['timestep'])} * units.fs, temperature_K = temperature_K, friction = 0.01 / units.fs)
"""
    elif thermostat == 'NoseHooverChainNVT':
        return "from ase.md.nose_hoover_chain import NoseHooverChainNVT", f"dyn = NoseHooverChainNVT(atoms, {float(input_config['timestep'])} * units.fs, temperature_K = temperature_K, tdamp = 50 * units.fs)"
    elif thermostat == 'Bussi':
        return "from ase.md.bussi import Bussi", f"dyn = Bussi(atoms, {float(input_config['timestep'])} * units.fs, temperature_K = temperature_K, taut = 100 * units.fs)"
    elif thermostat == 'NPT':
        return "from ase.md.npt import NPT", f"""
pressure_b = {float(input_config['pressure'])} 
ttime   = 20.0
pfactor = 2e6
num_interval = 100

dyn = NPT(atoms, {float(input_config['timestep'])}*units.fs, temperature_K = temperature_K, externalstress = pressure_b*units.bar, ttime = ttime*units.fs, pfactor = pfactor*units.GPa*(units.fs**2))
"""

def foundation_model_path(foundation_model):
    """
    Function to return the path to the foundation model
    """
    if foundation_model in ['small', 'large']:
        if foundation_model == 'small':
            model_code = 'MatterSim-v1.0.0-1M.pth'
        elif foundation_model == 'large':
            model_code = 'MatterSim-v1.0.0-5M.pth'
    else:
        # Custom model
        model_code = foundation_model
    #return f"""load_path="{model_code}", {dispersion_corr(dispersion_via_ase)}"""
    return f"""load_path="{model_code}" """

def foundation_model_code(foundation_model):
    """
    Function to return the name of the foundation model
    """
    if foundation_model in ['small', 'large']:
        if foundation_model == 'small':
            model_code = 'MatterSim-v1.0.0-1M.pth'
        elif foundation_model == 'large':
            model_code = 'MatterSim-v1.0.0-5M.pth'
    else:
        # Custom model
        model_code = foundation_model
    return model_code


def dispersion_corr(dispersion_via_ase):
    """
    Function to return the dispersion correction
    """
    if dispersion_via_ase == 'y':
        return " dispersion=True"
    else:
        return " dispersion=False"

def cell_matrix(pbc_mat):
    """
    Function to return the box matrix from the pbc_mat
    """
    return f"""np.array([[{float(pbc_mat[0,0])}, {float(pbc_mat[0,1])}, {float(pbc_mat[0,2])}], [{float(pbc_mat[1,0])}, {float(pbc_mat[1,1])}, {float(pbc_mat[1,2])}], [{float(pbc_mat[2,0])}, {float(pbc_mat[2,1])}, {float(pbc_mat[2,2])}]])"""

def write_traj_file(input_config):
    """
    Function to write the trajectory file
    """
    if input_config['print_ase_traj'] == 'y':
        return f"""# Trajectory ASE format: including positions, forces and velocities
traj = Trajectory('{input_config['project_name']}.traj', 'a', atoms)
dyn.attach(traj.write, interval={int(input_config['write_interval'])})
"""
    else:
        return " "


def ask_for_foundational_model(mattersim_config, run_type):
    """
    Function to ask the user for the foundational model and its size
    """
    foundation_model = ' '
    while foundation_model not in ['small', 'large', 'custom', '']:
        foundation_model = input("What is the foundational model? ('small', 'large', 'custom'): ")
        if foundation_model not in ['small', 'large', 'custom', '']:
            print("Invalid input! Please enter 'small', 'large' or 'custom'.")
    if foundation_model == 'custom':
        # Print the previous models
        show_models()
        foundation_model = input("What is the number/path to the custom model? ")
        # Check if input is int
        if foundation_model.isdigit():
            foundation_model = get_model(int(foundation_model))
    elif foundation_model == '':
        foundation_model = mattersim_config[run_type]['foundation_model']
    return foundation_model

def write_log_file(input_config):
    """
    Function to write the log file
    """
    if input_config['thermostat'] == 'NPT':
        return f"""# Log file
dyn.attach(MDLogger(dyn, atoms, 'md.log', header=True, stress=True, peratom=False, mode="a"), interval=100)
"""
    else:
        return f"""# Log file
dyn.attach(MDLogger(dyn, atoms, 'md.log', header=True, stress=False, peratom=False, mode="a"), interval={int(input_config['log_interval'])})"""

# Dataset creator
def dataset_creator(coord_file, pbc_mat, run_type, mattersim_config):
    """
    Function to create the dataset
    """
    force_file = input("What is the name of the force file? " +"[" + mattersim_config[run_type]['force_file'] + "]: ")
    if force_file == '':
        force_file = mattersim_config[run_type]['force_file']
    assert os.path.isfile(force_file), "Force file does not exist!"

    # Create the training dataset
    path_to_training_file = create_dataset(coord_file, force_file, pbc_mat)
    return path_to_training_file

def crt_config(input_config):
    """
    Function to create the config file for the finetuning
    """
    truefalse_dict = {'y': '--save_checkpoint', 'n': ''}
    early_stopping_dict = {'y': '', 'n': '--early_stop_patience 1000'}
    # Create the config file
    config = f""" --load_model_path {foundation_model_code(input_config['load_model_path'])} --train_data_path {input_config['train_data_path']} --device {input_config['device']} --force_loss_ratio {input_config['force_loss_ratio']} --batch_size {input_config['batch_size']} {truefalse_dict[input_config['save_checkpoint']]} --ckpt_interval {input_config['ckpt_interval']} --epochs {input_config['epochs']} {early_stopping_dict[input_config['early_stopping']]} --seed {input_config['seed']} --lr {input_config['lr']} --save_path {input_config['save_path']}"""
    return config


def review_training_file(path_to_training_file):
    """
    Function to keep the right Keywords for Forces and Energy in the training file
    """
    with open(path_to_training_file, 'r') as file:
        filedata = file.read()
    # Replace the target string
    try:
        filedata = filedata.replace('REF_Force', 'forces')
        filedata = filedata.replace('REF_TotEnergy', 'energy')
        path_to_training_file = path_to_training_file.replace('.xyz', '_trainset.xyz')
    except:
        try:
            filedata = filedata.replace('force', 'forces')
            filedata = filedata.replace('TotEnergy', 'energy')
            path_to_training_file = path_to_training_file.replace('.xyz', '_trainset.xyz')
        except:
            print("Please check the force and energy keywords yourself ('forces', 'energy').")
    
    # Write the file out again
    with open(path_to_training_file, 'w') as file:
        file.write(filedata)
    return path_to_training_file



# Write functions 
def write_input(input_config, run_type):
    """
    Create MatterSim input file
    """

    if run_type == 'MD':
        input_text = create_input(input_config, run_type)
        file_name = 'md_mattersim.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

    elif run_type == 'MULTI_MD':
        print(input_config['foundation_model'])
        no_runs = len(input_config['foundation_model'])
        print(f"Creating {no_runs} input files for the multi MD run.")

        # Explain the run
        with open('overview_multi_md.txt', 'w') as output:
            # Give the folder name + the model + model size
            for i in range(no_runs):
                output.write(f"multi_md_run{i}: {input_config['foundation_model'][i]} model\n")
        print("Overview file created: multi_md_overview.txt")

        for i in range(no_runs):
            input_config_tmp = input_config.copy()
            # Change the path of the coord file to ../coord_file (because each run is a folder)
            input_config_tmp['coord_file'] = f"../{input_config['coord_file']}"
            input_config_tmp['foundation_model'] = input_config['foundation_model'][i]
            #input_config_tmp['dispersion_via_ase'] = input_config['dispersion_via_ase'][i]

            input_text = create_input(input_config_tmp, 'MD')
            file_name = f'md_mattersim.py'
            
            # Make a new directory and save the input file there
            if not os.path.exists(f'multi_md_run{i}'):
                os.makedirs(f'multi_md_run{i}')
            with open(f'multi_md_run{i}/{file_name}', 'w') as output:
                output.write(input_text)
            print(f"Input file {file_name} created in multi_md_run{i}.")
    
    elif run_type == 'FINETUNE':
        print("No input file needed for the finetuning.")
        

    elif run_type == 'RECALC':
        input_text = create_input(input_config, run_type)
        file_name = 'recalc_mattersim.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

def write_runscript(input_config,run_type, finetune_config=""):
    """
    Write runscript for MatterSim calculations: default runscript for MatterSim is in the default_configs/runscript_templates.py
    """
    run_type_inp_names = {'MD': 'md_mattersim.py', 'MULTI_MD': 'md_mattersim.py', 'FINETUNE': '', 'RECALC': 'recalc_mattersim.py'}
    if run_type == 'FINETUNE':
        if input_config['device'] == 'cuda':
            with open('gpu_script.job', 'w') as output:
                output.write(mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type, finetune_config)[0])
            print("Runscript created: " + mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type, finetune_config)[1])
            # Change the runscript to be executable
            os.system('chmod +x gpu_script.job')
        elif input_config['device'] == 'cpu':
            with open('runscript.sh', 'w') as output:
                output.write(mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type, finetune_config)[2])
            print("Runscript created: " + mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type, finetune_config)[3])
            # Change the runscript to be executable
            os.system('chmod +x runscript.sh')
    elif run_type == 'MULTI_MD':
        for i in range(len(input_config['foundation_model'])):
            with open(f'multi_md_run{i}/gpu_script.job', 'w') as output:
                output.write(mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[0])
            print("Runscript created: " + mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[1])
            # Change the runscript to be executable
            os.system(f'chmod +x multi_md_run{i}/gpu_script.job')
            with open(f'multi_md_run{i}/runscript.sh', 'w') as output:
                output.write(mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[2])
            print("Runscript created: " + mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[3])
            # Change the runscript to be executable
            os.system(f'chmod +x multi_md_run{i}/runscript.sh')
    else: 
        with open('gpu_script.job', 'w') as output:
            output.write(mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[0])
        print("Runscript created: " + mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[1])
        # Change the runscript to be executable
        os.system('chmod +x gpu_script.job')
        with open('runscript.sh', 'w') as output:
            output.write(mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[2])
        print("Runscript created: " + mattersim_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[3])
        # Change the runscript to be executable
        os.system('chmod +x runscript.sh')

def write_log(input_config):
    """
    Write configuration to log file with the right format to be read by direct input
    """
    # Check if foundation_model value is a list
    if 'foundation_model' in input_config:
        if type(input_config['foundation_model']) == list:
            # Write the multiple log files for the MULTI_MD run
            for i in range(len(input_config['foundation_model'])):
                with open(f'multi_md_run{i}/mattersim_input.log', 'w') as output:
                    output.write("Input file created with the following configuration:\n") 
                    # Copy the dict without the key 'foundation_model'
                    input_config_tmp = input_config.copy()
                    input_config_tmp['foundation_model'] = input_config['foundation_model'][i]
                    #input_config_tmp['dispersion_via_ase'] = input_config['dispersion_via_ase'][i]
                    input_config_tmp['pbc_list'] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
                    output.write(f'"{input_config_tmp}"')  
    
    with open('mattersim_input.log', 'w') as output:
        output.write("Input file created with the following configuration:\n")
        try:  
            input_config["pbc_list"] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
        except:
            pass   
        # Check if foundation_model is in the input_config
        if np.logical_and('foundation_model' in input_config, 'dispersion_via_ase' in input_config):
            if type(input_config['foundation_model']) == list:
                # build a string with the list elements separated by a space
                foundation_string = ' '.join(f"'{item}'" for item in input_config['foundation_model'])
                foundation_string = f"'[{foundation_string}]'"
                input_config['foundation_model'] = foundation_string

            if type(input_config['dispersion_via_ase']) == list:
                # build a string with the list elements separated by a space
                dispersion_string = ' '.join(f"'{item}'" for item in input_config['dispersion_via_ase'])
                dispersion_string = f"'[{dispersion_string}]'"
                input_config['dispersion_via_ase'] = dispersion_string

        try:
            input_config = str(input_config).replace('"', '')
        except:
            pass 

        output.write(f'"{input_config}"')
    
      





def mattersim_citations(foundation_model = ""):
    """
    Function to print the citations for MatterSim
    """
    print("")
    print("Citations for MatterSim:")
    print(r"""1. Han Yang, Chenxi Hu, Yichi Zhou, Xixian Liu, Yu Shi, Jielan Li, Guanzhi Li, Zekun Chen, Shuizhou Chen, Claudio Zeni, Matthew Horton, Robert Pinsler, Andrew Fowler, Daniel Zügner, Tian Xie, Jake Smith, Lixin Sun, Qian Wang, Lingyu Kong, Chang Liu, Hongxia Hao, Ziheng Lu, MatterSim: A Deep Learning Atomistic Model Across Elements, Temperatures and Pressures, arXiv:2405.04967, 2024, https://arxiv.org/abs/2405.04967
@article{yang2024mattersim,
      title={MatterSim: A Deep Learning Atomistic Model Across Elements, Temperatures and Pressures},
      author={Han Yang and Chenxi Hu and Yichi Zhou and Xixian Liu and Yu Shi and Jielan Li and Guanzhi Li and Zekun Chen and Shuizhou Chen and Claudio Zeni and Matthew Horton and Robert Pinsler and Andrew Fowler and Daniel Zügner and Tian Xie and Jake Smith and Lixin Sun and Qian Wang and Lingyu Kong and Chang Liu and Hongxia Hao and Ziheng Lu},
      year={2024},
      eprint={2405.04967},
      archivePrefix={arXiv},
      primaryClass={cond-mat.mtrl-sci},
      url={https://arxiv.org/abs/2405.04967},
      journal={arXiv preprint arXiv:2405.04967}
}""")      
    print("")


