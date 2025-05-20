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
from amaceing_toolkit.default_configs import configs_mace
from amaceing_toolkit.default_configs import e0s_functionals 
from amaceing_toolkit.default_configs import mace_runscript
from amaceing_toolkit.default_configs import available_functionals
from amaceing_toolkit.runs.model_logger import model_logger
from amaceing_toolkit.runs.model_logger import show_models
from amaceing_toolkit.runs.model_logger import get_model


def atk_mace():
    """
    Main function to write the input file for MACE
    """
    print_logo()

    # Decide if atk_mace is called with arguments or not
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Write input file for MACE runs and prepare them: (1) Via a short Q&A: NO arguments needed! (2) Directly from the command line with a dictionary: TWO arguments needed!", formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-rt", "--run_type", type=str, help="[OPTIONAL] Which type of calculation do you want to run? ('GEO_OPT', 'CELL_OPT', 'MD', 'MULTI_MD', 'FINETUNE', 'FINETUNE_MULTIHEAD','RECALC')", required=False)
        parser.add_argument("-c", "--config", type=str, help=textwrap.dedent("""[OPTIONAL] Dictionary with the configuration:\n 
        \033[1m GEO_OPT \033[0m: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'max_iter': 'INT', 'foundation_model' : 'NAME/PATH', 'model_size': 'small/medium/large/none', 'dispersion_via_mace': 'y/n'}"\n
        \033[1m CELL_OPT \033[0m: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'max_iter': 'INT', 'foundation_model' : 'NAME/PATH', 'model_size': 'small/medium/large/none', 'dispersion_via_mace': 'y/n'}"\n
        \033[1m MD \033[0m: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model' : 'NAME/PATH', 'model_size': 'small/medium/large/none', 'dispersion_via_mace': 'y/n', 'temperature': 'FLOAT', 'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT','pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ase_traj': 'y/n'}"\n
        \033[1m MULTI_MD \033[0m: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model' : '['NAME/PATH' ...]', 'model_size': '['small/medium/large/none' ...]', 'dispersion_via_mace': '['y/n' ...]', 'temperature': 'FLOAT', 'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT','pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ase_traj': 'y/n'}"\n
        \033[1m FINETUNE \033[0m: "{'project_name' : 'NAME', 'train_file': 'FILE', 'device': 'cuda/cpu', 'stress_weight': 'FLOAT', 'forces_weight': 'FLOAT', 'energy_weight': 'FLOAT', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'prevent_catastrophic_forgetting': 'y/n', 'batch_size': 'INT', 'valid_fraction': 'FLOAT', 'valid_batch_size': 'INT', 'max_num_epochs': 'INT', 'seed': 'INT', 'lr': 'FLOAT', 'xc_functional_of_dataset' : 'BLYP/PBE', 'dir': 'PATH'}"\n
        \033[1m FINETUNE_MULTIHEAD \033[0m: "{'project_name' : 'NAME', 'train_file': '['FILE' ...]', 'device': 'cuda/cpu', 'stress_weight': 'FLOAT', 'forces_weight': 'FLOAT', 'energy_weight': 'FLOAT', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'batch_size': 'INT', 'valid_fraction': 'FLOAT', 'valid_batch_size': 'INT', 'max_num_epochs': 'INT', 'seed': 'INT', 'lr': 'FLOAT', 'xc_functional_of_dataset' : '[BLYP(_SR)/PBE(_SR) ...]', 'dir': 'PATH'}"\n
        \033[1m RECALC \033[0m: "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model': 'NAME/PATH', 'model_size': 'small/medium/large/none', 'dispersion_via_mace': 'y/n'}'\n" """), required=False)
        args = parser.parse_args()
        if args.config != ' ':
            try:
                if args.run_type == 'MULTI_MD':
                    input_config = string_to_dict_multi(args.config)
                    if np.size(input_config['pbc_list']) == 3: # Keep compatibility with old input files
                        input_config['pbc_list'] = np.array([[input_config['pbc_list'][0], 0, 0], [0, input_config['pbc_list'][1], 0], [0, 0, input_config['pbc_list'][2]]])
                    else:
                        input_config['pbc_list'] = np.array(input_config['pbc_list']).reshape(3,3)
                elif args.run_type == 'FINETUNE':
                    input_config = string_to_dict(args.config)
                    input_config['E0s'] = e0_wrapper(e0s_functionals(input_config['xc_functional_of_dataset']), input_config['train_file'], input_config['xc_functional_of_dataset'])
                elif args.run_type == 'FINETUNE_MULTIHEAD':
                    input_config = string_to_dict_multi2(args.config)
                    input_config['E0s'] = {}
                    for head in range(len(input_config['train_file'])):
                        print("Head no.", head)
                        input_config['E0s'][head] = e0_wrapper(e0s_functionals(input_config['xc_functional_of_dataset'][head]), input_config['train_file'][head], input_config['xc_functional_of_dataset'][head])
                else:
                    input_config = string_to_dict(args.config)
                    if np.size(input_config['pbc_list']) == 3: # Keep compatibility with old input files
                        input_config['pbc_list'] = np.array([[input_config['pbc_list'][0], 0, 0], [0, input_config['pbc_list'][1], 0], [0, 0, input_config['pbc_list'][2]]])
                    else:
                        input_config['pbc_list'] = np.array(input_config['pbc_list']).reshape(3,3)

                write_input(input_config, args.run_type)
            
                with open('mace_input.log', 'w') as output:
                    output.write("Input file created with the following configuration:\n") 
                    output.write(f'"{args.config}"')

                if args.run_type == 'RECALC':
                    print('Starting the recalculation...')

                    print("""#################
## MACE OUTPUT ##
#################""")
                    
                    # Start the recalculation with python
                    os.system(f"python recalc_mace.py")
                
                else:
                    write_runscript(input_config, args.run_type)

                # Log the run
                run_logger1(args.run_type,os.getcwd())

                # Log the model
                if args.run_type == 'FINETUNE' or args.run_type == 'FINETUNE_MULTIHEAD':
                    
                    name_of_model = f"{input_config['project_name']}_run-1.model"
                    location = os.path.join(os.getcwd(), input_config['dir'], name_of_model)

                    model_logger(location, input_config['project_name'], input_config['foundation_model'], input_config['model_size'], input_config['lr'], True)

                # Citations of MACE (outsource to the util function)
                #try: 
                #    mace_citations(input_config['foundation_model'])
                #except KeyError:
                #    mace_citations()

            except KeyError:
                print("The dictionary is not in the right format. Please check the help page.")
    else:
        mace_form()
    
    cite_amaceing_toolkit()

def mace_form():
    """
    Function to ask the user for the input file for MACE
    """

    print("\n")
    print("Welcome to the MACE input file writer!")
    print("This tool will help you build input files for MACE calculations.")
    print("Please answer the following questions to build the input file.")
    print("################################################################################################")
    print("## Defaults are set in the config file: /src/amaceing_toolkit/default_configs/mace_configs.py ##")
    print("## For more advanced options, please edit the resulting input file.                           ##")
    loaded_config = 'default'
    mace_config = configs_mace(loaded_config)
    print(f"## Loading config: " + loaded_config + "                                                                    ##")
    print("################################################################################################")
    print("\n")

    # Ask user for input data
    coord_file = input("What is the name of the coordinate file (or reference trajecory/training file)? " +"[" + mace_config['coord_file'] + "]: ")
    if coord_file == '':
        coord_file = mace_config['coord_file']
    assert os.path.isfile(coord_file), "Coordinate file does not exist!"
    
    box_cubic = ask_for_yes_no_pbc("Is the box cubic? (y/n/pbc)", mace_config['box_cubic'])

    if box_cubic == 'y':
        box_xyz = ask_for_float_int("What is the length of the box in Å?", str(10.0))
        pbc_mat = np.array([[box_xyz, 0.0, 0.0],[0.0, box_xyz, 0.0],[0.0, 0.0, box_xyz]])
    elif box_cubic == 'n':
        pbc_mat = ask_for_non_cubic_pbc()
    else:
        pbc_mat = np.loadtxt(box_cubic)


    # Ask the user for the run type
    run_type_dict = {'1': 'GEO_OPT', '2': 'CELL_OPT', '3': 'MD', '4': 'MULTI_MD', '5': 'FINETUNE', '6': 'FINETUNE_MULTIHEAD', '7': 'RECALC'}
    run_type = ' '
    while run_type not in ['1', '2', '3', '4', '5', '6', '7','']:
        run_type = input("Which type of calculation do you want to run? (1=GEO_OPT, 2=CELL_OPT, 3=MD, 4=MULTI_MD, 5=FINETUNE, 6=FINETUNE_MULTIHEAD, 7=RECALC): " + "[" + mace_config['run_type'] + "]: ")
        if run_type not in ['1', '2', '3', '4', '5', '6', '7','']:
            print("Invalid input! Please enter '1', '2', '3', '4', '5', '6' or '7'.")
    if run_type == '':
        run_type = mace_config['run_type']
    else:
        run_type = run_type_dict[run_type]

    if run_type == 'FINETUNE' or run_type == 'FINETUNE_MULTIHEAD':
        project_name = input("What is the name of the model?: ")
    else:
        project_name = input("What is the name of the project?: ")
    if project_name == '':
        project_name = f'{run_type}_{datetime.datetime.now().strftime("%Y%m%d")}'

    # Ask for the fine-tune settings 
    if run_type == 'FINETUNE':
        dataset_needed = ask_for_yes_no("Do you want to create a training dataset from a force & a position file (y) or did you define it already (n)?", 'y')
        if dataset_needed == 'y':
            print("Creating the training dataset...")
            path_to_training_file = dataset_creator(coord_file, pbc_mat, run_type, mace_config)      
            
        else: 
            # The given file is the training file
            path_to_training_file = coord_file

        # Use only a fraction of the dataset
        smaller_dataset = ask_for_yes_no("Do you want to use only a fraction of the dataset (e.g. for testing purposes)? (y/n)", 'n')
        if smaller_dataset == 'y':
            dataset_fraction = ask_for_int("Which n-th frame do you want to use? (e.g. 10 means every 10th frame)", 10)
            path_to_training_file = extract_frames(path_to_training_file, dataset_fraction)

        print("Collecting E0s for the training dataset...")
        xc_functional = ' '
        while xc_functional not in available_functionals():
            xc_functional = input(f"What is the exchange-correlation functional used in the production of the training dataset? {available_functionals()}: ")
            if xc_functional not in available_functionals():
                print(f"Invalid input! Please enter {available_functionals()}.")
        
        if xc_functional in available_functionals():
            e0_dict = e0_wrapper(e0s_functionals(xc_functional), coord_file, xc_functional)
        else:
            e0_dict = input("Please provide the E0s yourself for each element in the dataset in the following format: {1:-12.4830138479, ...}: ")

        
    elif run_type == 'FINETUNE_MULTIHEAD':
        no_heads = ask_for_int("How many heads do you want to train on?", 2)
        path_to_training_file = []
        e0_heads = {}
        for head in range(int(no_heads)):
            print(f"Head {head}")

            if head == 0:
                dataset_needed = ask_for_yes_no(f"Do you want to create a training dataset for head no. {head} from a force & a position file (y) or did you define it already (n)?", 'y')
            else: 
                dataset_needed = ask_for_yes_no(f"Do you want to create a training dataset for head no. {head} from a force & a position file (y) or did you prepare the file already (n)? ", 'y')
            
            if dataset_needed == 'y':
                print("Creating the training dataset...")
                if head == 0:
                    path_to_training_file_head = dataset_creator(coord_file, pbc_mat, run_type, mace_config)     
                else: 
                    coord_file = input("What is the name of the xyz file which includes positions and energies? " +"[" + mace_config['coord_file'] + "]: ")
                    if coord_file == '':
                        coord_file = mace_config['coord_file']
                    assert os.path.isfile(coord_file), "Coordinate file does not exist!"
                    path_to_training_file_head = dataset_creator(coord_file, pbc_mat, run_type, mace_config) 
            
            else: 
                if head == 0:
                    # The given file is the training file
                    path_to_training_file_head = coord_file
                else: 
                    # The given file is the training file
                    path_to_training_file_head = input("What is the name of the training file? " +"[" + mace_config['coord_file'] + "]: ")
                    if path_to_training_file_head == '':
                        path_to_training_file_head = mace_config['coord_file']
                    assert os.path.isfile(path_to_training_file_head), "Coordinate file does not exist!"

            path_to_training_file.append(path_to_training_file_head)

            # E0s        
            print(f"Collecting E0s for the training dataset...  (for head no. {head})")

            xc_functional = ' '
            while xc_functional not in available_functionals():
                xc_functional = input(f"What is the exchange-correlation functional used in the production of the training dataset? {available_functionals()}: ")
                if xc_functional not in available_functionals():
                    print(f"Invalid input! Please enter {available_functionals()}.")
            
            if xc_functional in available_functionals():
                e0_dict = e0_wrapper(e0s_functionals(xc_functional), path_to_training_file_head, xc_functional)
            else:
                e0_dict = input("Please provide the E0s yourself for each element in the dataset in the following format: {1:-12.4830138479, ...}: ")        
            
            e0_heads[head] = e0_dict
        
        e0_dict = e0_heads
        

    print("Default settings for this run type: " + str(mace_config[run_type]))

    use_default_input = ask_for_yes_no("Do you want to use the default input settings? (y/n)", mace_config['use_default_input'])
    if use_default_input == 'y':
        if run_type == 'FINETUNE' or run_type == 'FINETUNE_MULTIHEAD':
            input_config = config_wrapper(True, run_type, mace_config, coord_file, pbc_mat, project_name, path_to_training_file, e0_dict)
        else:
            input_config = config_wrapper(True, run_type, mace_config, coord_file, pbc_mat, project_name)
    else:
        small_changes = ask_for_yes_no("Do you want to make small changes to the default settings? (y/n)", "n")
        if small_changes == 'y':

            changing = True
            while changing:
                # List of mace_config[run_type] keys:
                settings = list(mace_config[run_type].keys())

                # Print the available settings with the default value
                print("Available settings:")
                setting_number = 1
                setting_number_list = []
                for setting in settings:
                    print(f"({setting_number}) {setting}: {mace_config[run_type][setting]}")
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
                mace_config[run_type][settings[int(setting_to_change) - 1]] = new_value

                # Change another setting?
                dict_onoff = {'y': True, 'n': False}
                changing = dict_onoff[ask_for_yes_no("Do you want to change another setting? (y/n)", 'n')]
            
            if run_type == 'FINETUNE' or run_type == 'FINETUNE_MULTIHEAD':
                input_config = config_wrapper(True, run_type, mace_config, coord_file, pbc_mat, project_name, path_to_training_file, e0_dict)
            else:
                input_config = config_wrapper(True, run_type, mace_config, coord_file, pbc_mat, project_name)

        else: 
            if run_type == 'FINETUNE' or run_type == 'FINETUNE_MULTIHEAD':
                input_config = config_wrapper(False, run_type, mace_config, coord_file, pbc_mat, project_name, path_to_training_file, e0_dict)
            else:
                input_config = config_wrapper(False, run_type, mace_config, coord_file, pbc_mat, project_name)

    if run_type == 'RECALC':
        
        write_input(input_config, run_type)
        
        print('Starting the recalculation...')

        print("""#################
## MACE OUTPUT ##
#################""")
        
        # Start the recalculation with python
        os.system(f"python recalc_mace.py")

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

        if run_type == 'FINETUNE' or run_type == 'FINETUNE_MULTIHEAD':
            # Log the model
            loc_of_execution = os.getcwd()
            loc_of_model = input_config['dir']
            name_of_model = f"{input_config['project_name']}_run-1.model"
            location = os.path.join(loc_of_execution, loc_of_model, name_of_model)

            model_logger(location, input_config['project_name'], input_config['foundation_model'], input_config['model_size'], input_config['lr'])

    # Citations of MACE (outsourced to the util function)
    #try: 
    #    mace_citations(input_config['foundation_model'])
    #except KeyError:
    #    mace_citations()

def config_wrapper(default, run_type, mace_config, coord_file, pbc_mat, project_name, path_to_training_file="", e0_dict={}):

    """
    Wrapper function to create the input file
    """

    # Use default input data
    if default == True:
        if run_type == 'GEO_OPT':
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat, 
                            'foundation_model': mace_config[run_type]['foundation_model'],
                            'model_size': mace_config[run_type]['model_size'],
                            'dispersion_via_mace': mace_config[run_type]['dispersion_via_mace'],
                            'max_iter': mace_config[run_type]['max_iter']}
        elif run_type == 'CELL_OPT':  
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat, 
                            'foundation_model': mace_config[run_type]['foundation_model'],
                            'model_size': mace_config[run_type]['model_size'],
                            'dispersion_via_mace': mace_config[run_type]['dispersion_via_mace'],
                            'max_iter': mace_config[run_type]['max_iter']}
        elif run_type == 'MD': 
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': mace_config[run_type]['foundation_model'],
                            'model_size': mace_config[run_type]['model_size'],
                            'dispersion_via_mace': mace_config[run_type]['dispersion_via_mace'],
                            'temperature': mace_config[run_type]['temperature'],
                            'pressure': mace_config[run_type]['pressure'],
                            'thermostat': mace_config[run_type]['thermostat'],
                            'nsteps': mace_config[run_type]['nsteps'],
                            'write_interval': mace_config[run_type]['write_interval'],
                            'timestep': mace_config[run_type]['timestep'],
                            'log_interval': mace_config[run_type]['log_interval'],
                            'print_ase_traj': mace_config[run_type]['print_ase_traj']}
        elif run_type == 'MULTI_MD': 
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': mace_config[run_type]['foundation_model'], # List
                            'model_size': mace_config[run_type]['model_size'], # List
                            'dispersion_via_mace': mace_config[run_type]['dispersion_via_mace'], # List
                            'temperature': mace_config[run_type]['temperature'],
                            'pressure': mace_config[run_type]['pressure'],
                            'thermostat': mace_config[run_type]['thermostat'],
                            'nsteps': mace_config[run_type]['nsteps'],
                            'write_interval': mace_config[run_type]['write_interval'],
                            'timestep': mace_config[run_type]['timestep'],
                            'log_interval': mace_config[run_type]['log_interval'],
                            'print_ase_traj': mace_config[run_type]['print_ase_traj']}
        elif run_type == 'FINETUNE':
            input_config = {'project_name': project_name,
                            'train_file': path_to_training_file, 
                            'E0s': e0_dict,
                            'device': mace_config[run_type]['device'],
                            'stress_weight': mace_config[run_type]['stress_weight'],
                            'forces_weight': mace_config[run_type]['forces_weight'],
                            'energy_weight': mace_config[run_type]['energy_weight'],
                            'foundation_model': mace_config[run_type]['foundation_model'],
                            'model_size': mace_config[run_type]['model_size'],
                            'batch_size': mace_config[run_type]['batch_size'],
                            'prevent_catastrophic_forgetting': mace_config[run_type]['prevent_catastrophic_forgetting'],
                            'valid_fraction': mace_config[run_type]['valid_fraction'],
                            'valid_batch_size': mace_config[run_type]['valid_batch_size'],
                            'max_num_epochs': mace_config[run_type]['max_num_epochs'],
                            'seed': mace_config[run_type]['seed'],
                            'lr': mace_config[run_type]['lr'], 
                            'dir': mace_config[run_type]['dir']}
        elif run_type == 'FINETUNE_MULTIHEAD':
            input_config = {'project_name': project_name,
                            'train_file': path_to_training_file, # List
                            'E0s': e0_dict,
                            'device': mace_config[run_type]['device'],
                            'stress_weight': mace_config[run_type]['stress_weight'],
                            'forces_weight': mace_config[run_type]['forces_weight'],
                            'energy_weight': mace_config[run_type]['energy_weight'],
                            'foundation_model': mace_config[run_type]['foundation_model'],
                            'model_size': mace_config[run_type]['model_size'],
                            'batch_size': mace_config[run_type]['batch_size'],
                            'valid_fraction': mace_config[run_type]['valid_fraction'],
                            'valid_batch_size': mace_config[run_type]['valid_batch_size'],
                            'max_num_epochs': mace_config[run_type]['max_num_epochs'],
                            'seed': mace_config[run_type]['seed'],
                            'lr': mace_config[run_type]['lr'], 
                            'dir': mace_config[run_type]['dir']}
        elif run_type == 'RECALC':
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': mace_config[run_type]['foundation_model'],
                            'model_size': mace_config[run_type]['model_size'],
                            'dispersion_via_mace': mace_config[run_type]['dispersion_via_mace']}
            
    # Ask user for input data
    else:
        if run_type == 'GEO_OPT':
            
            foundation_model, model_size = ask_for_foundational_model(mace_config, run_type)
            dispersion_via_mace = ask_for_yes_no("Do you want to include dispersion via MACE? (y/n)", mace_config[run_type]['dispersion_via_mace'])
            max_iter = ask_for_int("What is the maximum number of iterations?", mace_config['GEO_OPT']['max_iter'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat, 
                            'foundation_model': foundation_model,
                            'model_size': model_size,
                            'dispersion_via_mace': dispersion_via_mace,
                            'max_iter': max_iter}

        elif run_type == 'CELL_OPT':  
            
            foundation_model, model_size = ask_for_foundational_model(mace_config, run_type)
            dispersion_via_mace = ask_for_yes_no("Do you want to include dispersion via MACE? (y/n)", mace_config[run_type]['dispersion_via_mace'])
            max_iter = ask_for_int("What is the maximum number of iterations?", mace_config['GEO_OPT']['max_iter'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat, 
                            'foundation_model': foundation_model,
                            'model_size': model_size,
                            'dispersion_via_mace': dispersion_via_mace,
                            'max_iter': max_iter}
            
        elif run_type == 'MD': 
            
            foundation_model, model_size = ask_for_foundational_model(mace_config, run_type)
            dispersion_via_mace = ask_for_yes_no("Do you want to include dispersion via MACE? (y/n)", mace_config[run_type]['dispersion_via_mace'])
            thermostat = ask_for_int("What thermostat do you want to use (or NPT run)? (1: Langevin, 2: NoseHooverChainNVT, 3: Bussi, 4: NPT): ", mace_config[run_type]['thermostat'])
            thermo_dict = {'1': 'Langevin', '2': 'NoseHooverChainNVT', '3': 'Bussi', '4': 'NPT'}
            thermostat = thermo_dict[thermostat]
            temperature = ask_for_float_int("What is the temperature in Kelvin?", mace_config[run_type]['temperature'])
            if thermostat == 'NPT':
                pressure = ask_for_float_int("What is the pressure in bar?", mace_config[run_type]['pressure'])
            else: 
                pressure = ' '
            nsteps = ask_for_int("How many steps do you want to run?", mace_config[run_type]['nsteps'])
            write_interval = ask_for_int("How often do you want to write the trajectory?", mace_config[run_type]['write_interval'])
            timestep = ask_for_float_int("What is the timestep in fs?", mace_config[run_type]['timestep'])
            log_interval = ask_for_int("How often do you want to write the log file?", mace_config[run_type]['log_interval'])
            print_ase_traj = ask_for_yes_no("Do you want to print the ASE trajectory? (y/n)", mace_config[run_type]['print_ase_traj'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model,
                            'model_size': model_size,
                            'dispersion_via_mace': dispersion_via_mace,
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
            model_size = []
            dispersion_via_mace = []
            for i in range(no_runs):
                foundation_model_tmp, model_size_tmp = ask_for_foundational_model(mace_config, run_type)
                dispersion_via_mace_tmp = ask_for_yes_no("Do you want to include dispersion via MACE? (y/n)", mace_config[run_type]['dispersion_via_mace'])
                foundation_model.append(foundation_model_tmp)
                model_size.append(model_size_tmp)
                dispersion_via_mace.append(dispersion_via_mace_tmp)
            thermostat = ask_for_int("What thermostat do you want to use (or NPT run)? (1: Langevin, 2: NoseHooverChainNVT, 3: Bussi, 4: NPT): ", mace_config[run_type]['thermostat'])
            thermo_dict = {'1': 'Langevin', '2': 'NoseHooverChainNVT', '3': 'Bussi', '4': 'NPT'}
            thermostat = thermo_dict[thermostat]
            temperature = ask_for_float_int("What is the temperature in Kelvin?", mace_config[run_type]['temperature'])
            if thermostat == 'NPT':
                pressure = ask_for_float_int("What is the pressure in bar?", mace_config[run_type]['pressure'])
            else: 
                pressure = ' '
            nsteps = ask_for_int("How many steps do you want to run?", mace_config[run_type]['nsteps'])
            write_interval = ask_for_int("How often do you want to write the trajectory?", mace_config[run_type]['write_interval'])
            timestep = ask_for_float_int("What is the timestep in fs?", mace_config[run_type]['timestep'])
            log_interval = ask_for_int("How often do you want to write the log file?", mace_config[run_type]['log_interval'])
            print_ase_traj = ask_for_yes_no("Do you want to print the ASE trajectory? (y/n)", mace_config[run_type]['print_ase_traj'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model, # List
                            'model_size': model_size, # List
                            'dispersion_via_mace': dispersion_via_mace, # List
                            'temperature': temperature,
                            'pressure': pressure,
                            'thermostat': thermostat,
                            'nsteps': nsteps,
                            'write_interval': write_interval,
                            'timestep': timestep,
                            'log_interval': log_interval,
                            'print_ase_traj': print_ase_traj}


        elif run_type == 'FINETUNE':
            
            foundation_model, model_size = ask_for_foundational_model(mace_config, run_type)
            prevent_catastrophic_forgetting = ask_for_yes_no("Do you want to prevent catastrophic forgetting of the foundation model (multihead_finetune)? (y/n)", mace_config[run_type]['prevent_catastrophic_forgetting'])
            batch_size = ask_for_int("What is the batch size?", mace_config[run_type]['batch_size'])
            valid_batch_size = ask_for_int("What is the validation batch size?", mace_config[run_type]['valid_batch_size'])
            valid_fraction = ask_for_float_int("What is the validation fraction?", mace_config[run_type]['valid_fraction'])
            max_num_epochs = ask_for_int("What is the maximum number of epochs?", mace_config[run_type]['max_num_epochs'])
            seed = ask_for_int("What is the seed?", mace_config[run_type]['seed'])
            lr = ask_for_float_int("What is the learning rate?", mace_config[run_type]['lr'])
            dir = input("What is the directory for the model? [" + mace_config[run_type]['dir'] + "]: ")
            if dir == '':
                dir = mace_config[run_type]['dir']


            input_config = {'project_name': project_name,
                            'train_file': path_to_training_file,
                            'E0s': e0_dict,
                            'device': mace_config[run_type]['device'],
                            'stress_weight': mace_config[run_type]['stress_weight'],
                            'forces_weight': mace_config[run_type]['forces_weight'],
                            'energy_weight': mace_config[run_type]['energy_weight'],
                            'foundation_model': foundation_model,
                            'model_size': model_size,
                            'prevent_catastrophic_forgetting': prevent_catastrophic_forgetting,
                            'batch_size': batch_size,
                            'valid_fraction': valid_fraction,
                            'valid_batch_size': valid_batch_size,
                            'max_num_epochs': max_num_epochs,
                            'seed': seed,
                            'lr': lr, 
                            'dir': dir}

            
        elif run_type == 'FINETUNE_MULTIHEAD':

            foundation_model, model_size = ask_for_foundational_model(mace_config, run_type)
            batch_size = ask_for_int("What is the batch size?", mace_config[run_type]['batch_size'])
            valid_batch_size = ask_for_int("What is the validation batch size?", mace_config[run_type]['valid_batch_size'])
            valid_fraction = ask_for_float_int("What is the validation fraction?", mace_config[run_type]['valid_fraction'])
            max_num_epochs = ask_for_int("What is the maximum number of epochs?", mace_config[run_type]['max_num_epochs'])
            seed = ask_for_int("What is the seed?", mace_config[run_type]['seed'])
            lr = ask_for_float_int("What is the learning rate?", mace_config[run_type]['lr'])
            dir = input("What is the directory for the model? [" + mace_config[run_type]['dir'] + "]: ")
            if dir == '':
                dir = mace_config[run_type]['dir']


            input_config = {'project_name': project_name,
                            'train_file': path_to_training_file, # List
                            'E0s': e0_dict, # List
                            'device': mace_config[run_type]['device'],
                            'stress_weight': mace_config[run_type]['stress_weight'],
                            'forces_weight': mace_config[run_type]['forces_weight'],
                            'energy_weight': mace_config[run_type]['energy_weight'],
                            'foundation_model': foundation_model,
                            'model_size': model_size,
                            'batch_size': batch_size,
                            'valid_fraction': valid_fraction,
                            'valid_batch_size': valid_batch_size,
                            'max_num_epochs': max_num_epochs,
                            'seed': seed,
                            'lr': lr, 
                            'dir': dir}
            
        elif run_type == 'RECALC':
            
            foundation_model, model_size = ask_for_foundational_model(mace_config, run_type)
            dispersion_via_mace = ask_for_yes_no("Do you want to include dispersion via MACE? (y/n)", mace_config[run_type]['dispersion_via_mace'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model,
                            'model_size': model_size,
                            'dispersion_via_mace': dispersion_via_mace}
    return input_config


def create_input(input_config, run_type):
    """
    Function to create the input file
    """

    if run_type == 'GEO_OPT':
        return f""" 
{foundation_model_code(input_config['foundation_model'])}
import time
import numpy as np
from ase import build
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import write
from ase.optimize import BFGS
from ase.io import read

# Load the foundation model
mace_calc = {foundation_model_path(input_config['foundation_model'], input_config['dispersion_via_mace'], input_config['model_size'])} 
print("Loading of MACE model completed: {input_config['foundation_model']} model {input_config['model_size']}")

# Load the coordinates
atoms = read('{input_config['coord_file']}')			

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({cell_matrix(input_config['pbc_list'])})

atoms.calc = mace_calc

# Write the xyz trajectory
xyz_file = 'geoopt_output.xyz'
def save_positions(atoms):
    write(xyz_file, atoms, append=True)

# Set up the optimizer
optimizer = BFGS(atoms, trajectory='geoopt_output.traj', logfile='geoopt_output.log')
optimizer.attach(save_positions, interval=10, atoms=atoms)

# Run the optimizer
optimizer.run(fmax=0.01, steps={int(input_config['max_iter'])}) 

# Write the final coordinates
print("Final positions:", atoms.get_positions())
print("Total energy:", atoms.get_potential_energy())

write("{input_config['project_name']}_geoopt_final.xyz", atoms)

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    elif run_type == 'CELL_OPT':
        return f"""
{foundation_model_code(input_config['foundation_model'])}
import time
import numpy as np
from ase import build
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import write
from ase.optimize import BFGS, LBFGS
from ase.io import read
from ase.constraints import ExpCellFilter, StrainFilter

# Load the foundation model
mace_calc = {foundation_model_path(input_config['foundation_model'], input_config['dispersion_via_mace'], input_config['model_size'])} 
print("Loading of MACE model completed: {input_config['foundation_model']} model {input_config['model_size']}")

# Load the coordinates
atoms = read('{input_config['coord_file']}')			

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({cell_matrix(input_config['pbc_list'])})

atoms.calc = mace_calc

""" + r"""
# Set up logging
def print_dyn():
    imd = optimizer.get_number_of_steps()
    cell = atoms.get_cell()
    print(f" {imd: >3}   ", cell)
""" + f"""
print("Cell size before: ", atoms.cell)
atoms = ExpCellFilter(atoms, hydrostatic_strain=True)
optimizer = LBFGS(atoms, trajectory="cellopt.traj", logfile='cellopt.log')

# Write the xyz trajectory
xyz_file = 'cellopt_output.xyz'
def save_positions(atoms):
    write(xyz_file, atoms, append=True)

optimizer.attach(print_dyn, interval=10)

# Run the optimizer
optimizer.run(fmax=0.01, steps={int(input_config['max_iter'])})

# Print the final cell size
print("Cell size after optimization: ", atoms.atoms.cell)

# Write the final coordinates
print("Final positions:", atoms.get_positions())
print("Total energy:", atoms.get_potential_energy())

write("{input_config['project_name']}_cellopt_final.xyz", atoms)

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    elif run_type == 'MD':
        return f"""
{foundation_model_code(input_config['foundation_model'])}
import time
import numpy as np
import os
from ase import build
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import write
from ase.optimize import BFGS
from ase.io import read
from ase.md import MDLogger
{thermostat_code(input_config)[0]}

# Load the foundation model
mace_calc = {foundation_model_path(input_config['foundation_model'], input_config['dispersion_via_mace'], input_config['model_size'])}
print("Loading of MACE model completed: {input_config['foundation_model']} model {input_config['model_size']}")

# Load the coordinates (take care if it is the first start or a restart)
if os.path.isfile('{input_config['project_name']}.traj'):
    atoms = read('{input_config['project_name']}.traj')
    #atoms = read('{input_config['project_name']}_restart.traj')
else:
    atoms = read('{input_config['coord_file']}')			

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({cell_matrix(input_config['pbc_list'])})

atoms.calc = mace_calc

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
    
    elif run_type == 'FINETUNE':
        return f"""
import warnings

warnings.filterwarnings("ignore")
from mace.cli.run_train import main as mace_run_train_main
import sys
import logging


def train_mace(config_file_path):
    logging.getLogger().handlers.clear()
    sys.argv = ["program", "--config", config_file_path]
    mace_run_train_main()


train_mace("config_{input_config['project_name']}.yml")
""", f"""model: "MACE"
stress_weight: {input_config['stress_weight']}
forces_weight: {input_config['forces_weight']}
energy_weight: {input_config['energy_weight']}
foundation_model: {foundation_model_finetune_config(input_config['foundation_model'], input_config['model_size'])}
name: "{input_config['project_name']}"
model_dir: {input_config['dir']}
log_dir: {input_config['dir']}
checkpoints_dir: {input_config['dir']}
results_dir: {input_config['dir']}
train_file: "{input_config['train_file']}" 
valid_fraction: {input_config['valid_fraction']}
energy_key: "REF_TotEnergy"
forces_key: "REF_Force"
device: {input_config['device']}
{is_cuequivariance_installed_FT()}
{multihead_or_naive_ft(input_config['prevent_catastrophic_forgetting'])}
batch_size: {input_config['batch_size']}
valid_batch_size: {input_config['valid_batch_size']}
max_num_epochs: {input_config['max_num_epochs']}
seed: {input_config['seed']}
lr: {input_config['lr']}
E0s: "{input_config['E0s']}"
default_dtype: float32

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    elif run_type == 'FINETUNE_MULTIHEAD':
        heads_text = write_heads(input_config['train_file'], input_config['E0s'])
        return f"""
import warnings

warnings.filterwarnings("ignore")
from mace.cli.run_train import main as mace_run_train_main
import sys
import logging


def train_mace(config_file_path):
    logging.getLogger().handlers.clear()
    sys.argv = ["program", "--config", config_file_path]
    mace_run_train_main()


train_mace("config_{input_config['project_name']}.yml")
""", f"""model: "MACE"
stress_weight: {input_config['stress_weight']}
forces_weight: {input_config['forces_weight']}
energy_weight: {input_config['energy_weight']}
foundation_model: {foundation_model_finetune_config(input_config['foundation_model'], input_config['model_size'])}
name: "{input_config['project_name']}"
model_dir: {input_config['dir']}
log_dir: {input_config['dir']}
checkpoints_dir: {input_config['dir']}
results_dir: {input_config['dir']}
{heads_text}
valid_fraction: {input_config['valid_fraction']}
energy_key: "REF_TotEnergy"
forces_key: "REF_Force"
device: {input_config['device']}
{is_cuequivariance_installed_FT()}
batch_size: {input_config['batch_size']}
valid_batch_size: {input_config['valid_batch_size']}
max_num_epochs: {input_config['max_num_epochs']}
seed: {input_config['seed']}
lr: {input_config['lr']}
default_dtype: float32

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    elif run_type == 'RECALC': # to do: write the recalculation input code
        return f"""

{foundation_model_code(input_config['foundation_model'])}
import time
import numpy as np
from ase import build
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import write
from ase.io import read

# Load the foundation model
mace_calc = {foundation_model_path(input_config['foundation_model'], input_config['dispersion_via_mace'], input_config['model_size'])}
print("Loading of MACE model completed: {input_config['foundation_model']} model {input_config['model_size']}")

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
    atoms.calc = mace_calc
    forces = atoms.get_forces()
    all_forces.append(forces)
    energies = atoms.get_total_energy()
    all_energies.append(energies)

# Saving the energies and forces to files
all_forces = np.array(all_forces)
np.savetxt("energies_recalc_with_mace_model_{input_config['project_name']}", all_energies)
atom = trajectory[0].get_chemical_symbols()
atom = np.array(atom)
with open('forces_recalc_with_mace_model_{input_config['project_name']}.xyz', 'w') as f: """+r"""
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


def foundation_model_code(foundation_model):
    """
    Function to return the foundation model import code
    """
    if foundation_model == 'mace_off':
        return "from mace.calculators import mace_off"
    elif foundation_model == 'mace_anicc':
        return "from mace.calculators import mace_anicc"
    elif foundation_model == 'mace_mp':
        return "from mace.calculators import mace_mp"
    else:
        return "from mace.calculators import mace_mp" # to do check if right?

def foundation_model_path(foundation_model, dispersion_via_mace, model_size = ""):
    """
    Function to return the path to the foundation model
    """
    if foundation_model == 'mace_off':
        if model_size == "" or model_size not in ['small', 'medium', 'large']:
            model_size = 'small'
        return f"mace_off(model='{model_size}' {dispersion_corr(dispersion_via_mace)} {is_cuequivariance_installed()})"
    elif foundation_model == 'mace_anicc':
        return f"mace_anicc( {dispersion_corr(dispersion_via_mace)} {is_cuequivariance_installed()})"
    elif foundation_model == 'mace_mp':
        if model_size == "" or model_size not in ['small', 'medium', 'large']:
            model_size = 'small'
        return f"mace_mp(model='{model_size}' {dispersion_corr(dispersion_via_mace)} {is_cuequivariance_installed()})" 
    else:
        # Check if the foundation_model is a file path
        if np.logical_and(os.path.isfile(foundation_model),foundation_model.endswith('.model')):
            return f"mace_mp(model='{foundation_model}' {dispersion_corr(dispersion_via_mace)})"
        else: 
            print("Here are the available models (previously logged models):")
            show_models()
            path_to_custom_model = get_model(ask_for_int("What is the number of the model you want to use? ", 1))
            return f"mace_mp(model='{path_to_custom_model}' {dispersion_corr(dispersion_via_mace)})"

def foundation_model_finetune_config(foundation_model, model_size = ""):
    """
    Function to return the code for the foundation model to include in the finetuning config file 
    """
    if foundation_model == 'mace_off':
        if model_size == "" or model_size not in ['small', 'medium', 'large']:
            model_size = 'small'
        return f"{model_size}_off"
    elif foundation_model == 'mace_anicc':
        return "anicc"
    elif foundation_model == 'mace_mp':
        if model_size == "" or model_size not in ['small', 'medium', 'large']:
            model_size = 'small'
        return f"{model_size}"
    else:
        # Custom model
        return foundation_model


def dispersion_corr(dispersion_via_mace):
    """
    Function to return the dispersion correction
    """
    if dispersion_via_mace == 'y':
        return ", dispersion = True"
    else:
        return ", dispersion = False"

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

# (Hopefully) faster Mace with cuequivariance
def is_cuequivariance_installed():
    if cuequivariance_import() == False:
        return ", enable_cueq = False"
    else:
        return ", enable_cueq = True"

def is_cuequivariance_installed_FT(): # for finetuning config file
    if cuequivariance_import() == False:
        return "enable_cueq: False"
    else:
        return "enable_cueq: True"

def cuequivariance_import():
    try:
        import cuequivariance
        return True
    except ImportError:
        return False
    
def multihead_or_naive_ft(prevent_catastrophic_forgetting):
    if prevent_catastrophic_forgetting == 'y':
        return "multiheads_finetuning: True"
    else:
        return "multiheads_finetuning: False"
    

def ask_for_foundational_model(mace_config, run_type):
    """
    Function to ask the user for the foundational model and its size
    """
    foundation_model = ' '
    model_size= ' '
    while foundation_model not in ['mace_off', 'mace_anicc', 'mace_mp', 'custom', '']:
        foundation_model = input("What is the foundational model? ('mace_off', 'mace_anicc', 'mace_mp', 'custom'): ")
        if foundation_model not in ['mace_off', 'mace_anicc', 'mace_mp', 'custom', '']:
            print("Invalid input! Please enter 'mace_off', 'mace_anicc', 'mace_mp', or 'custom'.")
    if foundation_model == 'custom':
        # Print the previous models
        show_models()
        foundation_model = input("What is the number/path to the custom model? ")
        # Check if input is int
        if foundation_model.isdigit():
            foundation_model = get_model(int(foundation_model))
    elif foundation_model == '':
        foundation_model = mace_config[run_type]['foundation_model']

    if foundation_model in ['mace_off', 'mace_mp']:
        while model_size not in ['small', 'medium', 'large', '']:
            model_size = input("What is the model size? ('small', 'medium', 'large'): ")
            if model_size not in ['small', 'medium', 'large', '']:
                print("Invalid input! Please enter 'small', 'medium', or 'large'.")
        if model_size == '':
            model_size = mace_config[run_type]['model_size']
    
    return foundation_model, model_size

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
def dataset_creator(coord_file, pbc_list, run_type, mace_config):
    """
    Function to create the dataset
    """
    force_file = input("What is the name of the force file? " +"[" + mace_config[run_type]['force_file'] + "]: ")
    if force_file == '':
        force_file = mace_config[run_type]['force_file']
    assert os.path.isfile(force_file), "Force file does not exist!"

    # Create the training dataset
    path_to_training_file = create_dataset(coord_file, force_file, pbc_list)
    return path_to_training_file


# Write functions 
def write_input(input_config, run_type):
    """
    Create MACE input file
    """

    if run_type == 'GEO_OPT':
        input_text = create_input(input_config, run_type)
        file_name = 'geoopt_mace.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

    elif run_type == 'CELL_OPT':
        input_text = create_input(input_config, run_type)
        file_name = 'cellopt_mace.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

    elif run_type == 'MD':
        input_text = create_input(input_config, run_type)
        file_name = 'md_mace.py'
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
                output.write(f"multi_md_run{i}: {input_config['foundation_model'][i]} model {input_config['model_size'][i]}\n")
        print("Overview file created: multi_md_overview.txt")

        for i in range(no_runs):
            input_config_tmp = input_config.copy()
            # Change the path of the coord file to ../coord_file (because each run is a folder)
            input_config_tmp['coord_file'] = f"../{input_config['coord_file']}"
            input_config_tmp['foundation_model'] = input_config['foundation_model'][i]
            input_config_tmp['model_size'] = input_config['model_size'][i]
            input_config_tmp['dispersion_via_mace'] = input_config['dispersion_via_mace'][i]

            input_text = create_input(input_config_tmp, 'MD')
            file_name = f'md_mace.py'
            
            # Make a new directory and save the input file there
            if not os.path.exists(f'multi_md_run{i}'):
                os.makedirs(f'multi_md_run{i}')
            with open(f'multi_md_run{i}/{file_name}', 'w') as output:
                output.write(input_text)
            print(f"Input file {file_name} created in multi_md_run{i}.")
    
    elif run_type == 'FINETUNE':
        input_text, config_text = create_input(input_config, run_type)
        file_name = 'finetune_mace.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")
        config_file = f"config_{input_config['project_name']}.yml"
        with open(config_file, 'w') as output:
            output.write(config_text)
        print(f"Config file {config_file} created.")
    
    elif run_type == 'FINETUNE_MULTIHEAD':
        input_text, config_text = create_input(input_config, run_type)
        file_name = 'finetune_mace.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")
        config_file = f"config_{input_config['project_name']}.yml"
        with open(config_file, 'w') as output:
            output.write(config_text)
        print(f"Config file {config_file} created.")

    elif run_type == 'RECALC':
        input_text = create_input(input_config, run_type)
        file_name = 'recalc_mace.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

def write_runscript(input_config,run_type):
    """
    Write runscript for MACE calculations: default runscript for mace is in the default_configs/runscript_templates.py
    """
    run_type_inp_names = {'GEO_OPT': 'geoopt_mace.py', 'CELL_OPT': 'cellopt_mace.py', 'MD': 'md_mace.py', 'MULTI_MD': 'md_mace.py', 'FINETUNE': 'finetune_mace.py', 'FINETUNE_MULTIHEAD': 'finetune_multihead_mace.py', 'RECALC': 'recalc_mace.py'}
    if run_type == 'FINETUNE' or run_type == 'FINETUNE_MULTIHEAD':
        if input_config['device'] == 'cuda':
            with open('gpu_script.job', 'w') as output:
                output.write(mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[0])
            print("Runscript created: " + mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[1])
            # Change the runscript to be executable
            os.system('chmod +x gpu_script.job')
        elif input_config['device'] == 'cpu':
            with open('runscript.sh', 'w') as output:
                output.write(mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[2])
            print("Runscript created: " + mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[3])
            # Change the runscript to be executable
            os.system('chmod +x runscript.sh')
    elif run_type == 'MULTI_MD':
        for i in range(len(input_config['foundation_model'])):
            with open(f'multi_md_run{i}/gpu_script.job', 'w') as output:
                output.write(mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[0])
            print("Runscript created: " + mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[1])
            # Change the runscript to be executable
            os.system(f'chmod +x multi_md_run{i}/gpu_script.job')
            with open(f'multi_md_run{i}/runscript.sh', 'w') as output:
                output.write(mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[2])
            print("Runscript created: " + mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[3])
            # Change the runscript to be executable
            os.system(f'chmod +x multi_md_run{i}/runscript.sh')
    else: 
        with open('gpu_script.job', 'w') as output:
            output.write(mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[0])
        print("Runscript created: " + mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[1])
        # Change the runscript to be executable
        os.system('chmod +x gpu_script.job')
        with open('runscript.sh', 'w') as output:
            output.write(mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[2])
        print("Runscript created: " + mace_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[3])
        # Change the runscript to be executable
        os.system('chmod +x runscript.sh')

def write_log(input_config):
    """
    Write configuration to log file with the right format to be read by direct input
    """
    # Check if foundation_model value is a list
    if type(input_config['foundation_model']) == list:
        # Write the multiple log files for the MULTI_MD run
        for i in range(len(input_config['foundation_model'])):
            with open(f'multi_md_run{i}/mace_input.log', 'w') as output:
                output.write("Input file created with the following configuration:\n") 
                # Copy the dict without the key 'foundation_model' and 'model_size'
                input_config_tmp = input_config.copy()
                input_config_tmp['foundation_model'] = input_config['foundation_model'][i]
                input_config_tmp['model_size'] = input_config['model_size'][i]
                input_config_tmp['dispersion_via_mace'] = input_config['dispersion_via_mace'][i]
                input_config_tmp['pbc_list'] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
                output.write(f'"{input_config_tmp}"')  
    
    with open('mace_input.log', 'w') as output:
        output.write("Input file created with the following configuration:\n")
        try:  
            input_config["pbc_list"] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
        except:
            pass
        if type(input_config['foundation_model']) == list:
            # build a string with the list elements separated by a space
            foundation_string = ' '.join(f"'{item}'" for item in input_config['foundation_model'])
            foundation_string = f"'[{foundation_string}]'"
            input_config['foundation_model'] = foundation_string
        print(input_config['model_size'])    
        if type(input_config['model_size']) == list:
            # build a string with the list elements separated by a space
            model_size_string = ' '.join(f"'{item}'" for item in input_config['model_size'])
            model_size_string = f"'[{model_size_string}]'"
            input_config['model_size'] = model_size_string
        try:
            if type(input_config['dispersion_via_mace']) == list:
                # build a string with the list elements separated by a space
                dispersion_string = ' '.join(f"'{item}'" for item in input_config['dispersion_via_mace'])
                dispersion_string = f"'[{dispersion_string}]'"
                input_config['dispersion_via_mace'] = dispersion_string
        except:
            pass


        # delete the key-value pair of the key 'E0s' if it exists
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

        #input_config = str(input_config).replace("'", '')
        output.write(f'"{input_config}"')


def write_heads(train_files, e0_dict):
    """
    Write the heads for the multihead finetune
    """
    head_text = f"""multiheads_finetuning: True
heads: """ 
    for i in range(len(train_files)):
        head_text += f"""
  head_{i}:
    train_file: "{train_files[i]}"  
    E0s: "{e0_dict[i]}" """
    return head_text


def mace_citations(foundation_model = ""):
    """
    Function to print the citations for MACE
    """
    print("")
    print("Citations for MACE:")
    print(r""" 1. Ilyes Batatia, David Peter Kovacs, Gregor N. C. Simm, Christoph Ortner, Gábor Csányi, MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields, Advances in Neural Information Processing Systems, 2022, https://openreview.net/forum?id=YPpSngE-ZU
@inproceedings{Batatia2022mace,
  title={{MACE}: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields},
  author={Ilyes Batatia and David Peter Kovacs and Gregor N. C. Simm and Christoph Ortner and Gábor Csányi},
  booktitle={Advances in Neural Information Processing Systems},
  editor={Alice H. Oh and Alekh Agarwal and Danielle Belgrave and Kyunghyun Cho},
  year={2022},
  url={https://openreview.net/forum?id=YPpSngE-ZU}
}""")
    print("")
    print(r""" 2. Ilyes Batatia, Simon Batzner, David Peter Kovacs, Albert Musaelian, Gregor N. C. Simm, Ralf Drautz, Christoph Ortner, Boris Kozinsky, Gábor Csányi, The Design Space of E(3)-Equivariant Atom-Centered Interatomic Potentials, arXiv:2205.06643, 2022, https://arxiv.org/abs/2205.06643
@misc{Batatia2022Design,
  title = {The Design Space of E(3)-Equivariant Atom-Centered Interatomic Potentials},
  author = {Batatia, Ilyes and Batzner, Simon and Kov{\'a}cs, D{\'a}vid P{\'e}ter and Musaelian, Albert and Simm, Gregor N. C. and Drautz, Ralf and Ortner, Christoph and Kozinsky, Boris and Cs{\'a}nyi, G{\'a}bor},
  year = {2022},
  number = {arXiv:2205.06643},
  eprint = {2205.06643},
  eprinttype = {arxiv},
  doi = {10.48550/arXiv.2205.06643},
  archiveprefix = {arXiv}
 }""")
    if foundation_model == 'mace_mp':
        print("")
        print(r""" 3. Ilyes Batatia, Philipp Benner, Yuan Chiang, Alin M. Elena, Dávid P. Kovács, Janosh Riebesell, Xavier R. Advincula, Mark Asta, William J. Baldwin, Noam Bernstein, Arghya Bhowmik, Samuel M. Blau, Vlad Cărare, James P. Darby, Sandip De, Flaviano Della Pia, Volker L. Deringer, Rokas Elijošius, Zakariya El-Machachi, Edvin Fako, Andrea C. Ferrari, Annalena Genreith-Schriever, Janine George, Rhys E. A. Goodall, Clare P. Grey, Shuang Han, Will Handley, Hendrik H. Heenen, Kersti Hermansson, Christian Holm, Jad Jaafar, Stephan Hofmann, Konstantin S. Jakob, Hyunwook Jung, Venkat Kapil, Aaron D. Kaplan, Nima Karimitari, Namu Kroupa, Jolla Kullgren, Matthew C. Kuner, Domantas Kuryla, Guoda Liepuoniute, Johannes T. Margraf, Ioan-Bogdan Magdău, Angelos Michaelides, J. Harry Moore, Aakash A. Naik, Samuel P. Niblett, Sam Walton Norwood, Niamh O'Neill, Christoph Ortner, Kristin A. Persson, Karsten Reuter, Andrew S. Rosen, Lars L. Schaaf, Christoph Schran, Eric Sivonxay, Tamás K. Stenczel, Viktor Svahn, Christopher Sutton, Cas van der Oord, Eszter Varga-Umbrich, Tejs Vegge, Martin Vondrák, Yangshuai Wang, William C. Witt, Fabian Zills, Gábor Csányi, A foundation model for atomistic materials chemistry, arXiv:2401.00096, 2023, https://arxiv.org/abs/2401.00096
@article{batatia2023foundation,
  title={A foundation model for atomistic materials chemistry},
  author={Ilyes Batatia and Philipp Benner and Yuan Chiang and Alin M. Elena and Dávid P. Kovács and Janosh Riebesell and Xavier R. Advincula and Mark Asta and William J. Baldwin and Noam Bernstein and Arghya Bhowmik and Samuel M. Blau and Vlad Cărare and James P. Darby and Sandip De and Flaviano Della Pia and Volker L. Deringer and Rokas Elijošius and Zakariya El-Machachi and Edvin Fako and Andrea C. Ferrari and Annalena Genreith-Schriever and Janine George and Rhys E. A. Goodall and Clare P. Grey and Shuang Han and Will Handley and Hendrik H. Heenen and Kersti Hermansson and Christian Holm and Jad Jaafar and Stephan Hofmann and Konstantin S. Jakob and Hyunwook Jung and Venkat Kapil and Aaron D. Kaplan and Nima Karimitari and Namu Kroupa and Jolla Kullgren and Matthew C. Kuner and Domantas Kuryla and Guoda Liepuoniute and Johannes T. Margraf and Ioan-Bogdan Magdău and Angelos Michaelides and J. Harry Moore and Aakash A. Naik and Samuel P. Niblett and Sam Walton Norwood and Niamh O'Neill and Christoph Ortner and Kristin A. Persson and Karsten Reuter and Andrew S. Rosen and Lars L. Schaaf and Christoph Schran and Eric Sivonxay and Tamás K. Stenczel and Viktor Svahn and Christopher Sutton and Cas van der Oord and Eszter Varga-Umbrich and Tejs Vegge and Martin Vondrák and Yangshuai Wang and William C. Witt and Fabian Zills and Gábor Csányi},
  year={2023},
  eprint={2401.00096},
  archivePrefix={arXiv},
  primaryClass={physics.chem-ph}
}""")
        print("")
        print(r""" 4. Bowen Deng, Peichen Zhong, KyuJung Jun, Janosh Riebesell, Kevin Han, Christopher J. Bartel, Gerbrand Ceder, CHGNet: Pretrained universal neural network potential for charge-informed atomistic modeling, arXiv:2302.14231, 2023, https://arxiv.org/abs/2302.14231
@article{deng2023chgnet,
  title={CHGNet: Pretrained universal neural network potential for charge-informed atomistic modeling},
  author={Bowen Deng and Peichen Zhong and KyuJung Jun and Janosh Riebesell and Kevin Han and Christopher J. Bartel and Gerbrand Ceder},
  year={2023},
  eprint={2302.14231},
  archivePrefix={arXiv},
  primaryClass={cond-mat.mtrl-sci}
}
""")
    elif foundation_model == 'mace_off':
        print("")
        print(r""" 3. Dávid Péter Kovács, J. Harry Moore, Nicholas J. Browning, Ilyes Batatia, Joshua T. Horton, Venkat Kapil, William C. Witt, Ioan-Bogdan Magdău, Daniel J. Cole, Gábor Csányi, MACE-OFF23: Transferable Machine Learning Force Fields for Organic Molecules, arXiv:2312.15211, 2023, https://arxiv.org/abs/2312.15211
@misc{kovacs2023maceoff23,
  title={MACE-OFF23: Transferable Machine Learning Force Fields for Organic Molecules}, 
  author={Dávid Péter Kovács and J. Harry Moore and Nicholas J. Browning and Ilyes Batatia and Joshua T. Horton and Venkat Kapil and William C. Witt and Ioan-Bogdan Magdău and Daniel J. Cole and Gábor Csányi},
  year={2023},
  eprint={2312.15211},
  archivePrefix={arXiv},
}        
""")

