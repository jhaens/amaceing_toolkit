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
from .utils import frame_counter
from .utils import extract_frames
from .utils import xyz_reader
from amaceing_toolkit.runs.run_logger import run_logger1
from amaceing_toolkit.default_configs import configs_uma
from amaceing_toolkit.default_configs import uma_runscript
from amaceing_toolkit.runs.model_logger import model_logger
from amaceing_toolkit.runs.model_logger import show_models
from amaceing_toolkit.runs.model_logger import get_model


def atk_uma():
    """
    Main function to write the input file for UMA
    """
    print_logo()

    # Decide if atk_mace is called with arguments or not
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Write input file for UMA runs and prepare them: (1) Via a short Q&A: NO arguments needed! (2) Directly from the command line with a dictionary: TWO arguments needed!", formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-rt", "--run_type", type=str, help="[OPTIONAL] Which type of calculation do you want to run? ('MD', 'MULTI_MD', 'RECALC')", required=False)
        parser.add_argument("-c", "--config", type=str, help=textwrap.dedent("""[OPTIONAL] Dictionary with the configuration:\n 
        \033[1m MD \033[0m: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model' : 'oc20/omat/omol/odac/omc', 'temperature': 'FLOAT', 'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT','pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ase_traj': 'y/n'}"\n
        \033[1m MULTI_MD \033[0m: "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'foundation_model' : '['oc20/omat/omol/odac/omc' ...]', 'temperature': 'FLOAT', 'thermostat': 'Langevin/NoseHooverChainNVT/Bussi/NPT','pressure': 'FLOAT/None', 'nsteps': 'INT', 'timestep': 'FLOAT', 'write_interval': 'INT', 'log_interval': 'INT', 'print_ase_traj': 'y/n'}"\n
        \033[1m RECALC \033[0m: "{'project_name': 'NAME', 'coord_file': 'FILE', 'pbc_list': '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', foundation_model' : 'oc20/omat/omol/odac/omc'}'\n" """), required=False)
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
                else:
                    input_config = string_to_dict(args.config)
                    if np.size(input_config['pbc_list']) == 3: # Keep compatibility with old input files
                        input_config['pbc_list'] = np.array([[input_config['pbc_list'][0], 0, 0], [0, input_config['pbc_list'][1], 0], [0, 0, input_config['pbc_list'][2]]])
                    else:
                        input_config['pbc_list'] = np.array(input_config['pbc_list']).reshape(3,3)
                    write_input(input_config, args.run_type)

                with open('uma_input.log', 'w') as output:
                    output.write("Input file created with the following configuration:\n") 
                    output.write(f'"{args.config}"')

                if args.run_type == 'RECALC':
                    print('Starting the recalculation...')

                    print("""################
## UMA OUTPUT ##
################""")
                    
                    # Start the recalculation with python
                    os.system(f"python recalc_uma.py")


                else:
                    write_runscript(input_config, args.run_type)

                # Log the run
                run_logger1(args.run_type,os.getcwd())

            except KeyError:
                print("The dictionary is not in the right format. Please check the help page.")
                # Print the error message
                print("Error: ", sys.exc_info()[1])

    else:
        uma_form()
    
    cite_amaceing_toolkit()

def uma_form():
    """
    Function to ask the user for the input file for UMA
    """

    print("\n")
    print("Welcome to the UMA input file writer!")
    print("This tool will help you build input files for UMA calculations.")
    print("Please answer the following questions to build the input file.")
    print("#####################################################################################################")
    print("## Defaults are set in the config file: /src/amaceing_toolkit/default_configs/uma_configs.py       ##")
    print("## For more advanced options, please edit the resulting input file.                                ##")
    loaded_config = 'default'
    uma_config = configs_uma(loaded_config)
    print(f"## Loading config: " + loaded_config + "                                                                         ##")
    print("#####################################################################################################")
    print("\n")

    # Ask user for input data
    coord_file = input("What is the name of the coordinate file (or reference trajecory)? " +"[" + uma_config['coord_file'] + "]: ")
    if coord_file == '':
        coord_file = uma_config['coord_file']
    assert os.path.isfile(coord_file), "Coordinate file does not exist!"
    
    box_cubic = ask_for_yes_no_pbc("Is the box cubic? (y/n/pbc)", uma_config['box_cubic'])

    if box_cubic == 'y':
        box_xyz = ask_for_float_int("What is the length of the box in Å?", str(10.0))
        pbc_mat = np.array([[box_xyz, 0.0, 0.0],[0.0, box_xyz, 0.0],[0.0, 0.0, box_xyz]])
    elif box_cubic == 'n':
        pbc_mat = ask_for_non_cubic_pbc()
    else:
        pbc_mat = np.loadtxt(box_cubic)


    # Ask the user for the run type
    run_type_dict = {'1': 'MD', '2': 'MULTI_MD', '3': 'RECALC'}
    run_type = ' '
    while run_type not in ['1', '2', '3','']:
        run_type = input("Which type of calculation do you want to run? (1=MD, 2=MULTI_MD, 3=RECALC): " + "[" + uma_config['run_type'] + "]: ")
        if run_type not in ['1', '2', '3','']:
            print("Invalid input! Please enter '1', '2' or '3'.")
    if run_type == '':
        run_type = uma_config['run_type']
    else:
        run_type = run_type_dict[run_type]

    project_name = input("What is the name of the project?: ")
    if project_name == '':
        project_name = f'{run_type}_{datetime.datetime.now().strftime("%Y%m%d")}'


    print("Default settings for this run type: " + str(uma_config[run_type]))

    use_default_input = ask_for_yes_no("Do you want to use the default input settings? (y/n)", uma_config['use_default_input'])
    if use_default_input == 'y':
        input_config = config_wrapper(True, run_type, uma_config, coord_file, pbc_mat, project_name)
    else:
        small_changes = ask_for_yes_no("Do you want to make small changes to the default settings? (y/n)", "n")
        if small_changes == 'y':

            changing = True
            while changing:
                # List of uma_config[run_type] keys:
                settings = list(uma_config[run_type].keys())

                # Print the available settings with the default value
                print("Available settings:")
                setting_number = 1
                setting_number_list = []
                for setting in settings:
                    print(f"({setting_number}) {setting}: {uma_config[run_type][setting]}")
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
                uma_config[run_type][settings[int(setting_to_change) - 1]] = new_value

                # Change another setting?
                dict_onoff = {'y': True, 'n': False}
                changing = dict_onoff[ask_for_yes_no("Do you want to change another setting? (y/n)", 'n')]
            
            input_config = config_wrapper(True, run_type, uma_config, coord_file, pbc_mat, project_name)

        else: 
            input_config = config_wrapper(False, run_type, uma_config, coord_file, pbc_mat, project_name)

    if run_type == 'RECALC':
        
        write_input(input_config, run_type)
        
        print('Starting the recalculation...')

        print("""################
## UMA OUTPUT ##
################""")
        
        # Start the recalculation with python
        os.system(f"python recalc_uma.py")

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

            
    # Citations WIP


def config_wrapper(default, run_type, uma_config, coord_file, pbc_mat, project_name, path_to_training_file="", e0_dict={}):

    """
    Wrapper function to create the input file
    """

    # Use default input data
    if default == True:
        if run_type == 'MD': 
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': uma_config[run_type]['foundation_model'],
                            'temperature': uma_config[run_type]['temperature'],
                            'pressure': uma_config[run_type]['pressure'],
                            'thermostat': uma_config[run_type]['thermostat'],
                            'nsteps': uma_config[run_type]['nsteps'],
                            'write_interval': uma_config[run_type]['write_interval'],
                            'timestep': uma_config[run_type]['timestep'],
                            'log_interval': uma_config[run_type]['log_interval'],
                            'print_ase_traj': uma_config[run_type]['print_ase_traj']}
        elif run_type == 'MULTI_MD': 
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': uma_config[run_type]['foundation_model'], # List
                            'temperature': uma_config[run_type]['temperature'],
                            'pressure': uma_config[run_type]['pressure'],
                            'thermostat': uma_config[run_type]['thermostat'],
                            'nsteps': uma_config[run_type]['nsteps'],
                            'write_interval': uma_config[run_type]['write_interval'],
                            'timestep': uma_config[run_type]['timestep'],
                            'log_interval': uma_config[run_type]['log_interval'],
                            'print_ase_traj': uma_config[run_type]['print_ase_traj']}
        elif run_type == 'RECALC':
            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': uma_config[run_type]['foundation_model']}
            
    # Ask user for input data
    else:
        if run_type == 'MD': 
            
            foundation_model = ask_for_foundational_model(uma_config, run_type)
            reversed_thermo_dict = {'Langevin': '1', 'NoseHooverChainNVT': '2', 'Bussi': '3', 'NPT': '4'}
            thermostat = ask_for_int("What thermostat do you want to use (or NPT run)? (1: Langevin, 2: NoseHooverChainNVT, 3: Bussi, 4: NPT): ", reversed_thermo_dict[uma_config[run_type]['thermostat']])
            thermo_dict = {'1': 'Langevin', '2': 'NoseHooverChainNVT', '3': 'Bussi', '4': 'NPT'}
            thermostat = thermo_dict[thermostat]
            temperature = ask_for_float_int("What is the temperature in Kelvin?", uma_config[run_type]['temperature'])
            if thermostat == 'NPT':
                pressure = ask_for_float_int("What is the pressure in bar?", uma_config[run_type]['pressure'])
            else: 
                pressure = ' '
            nsteps = ask_for_int("How many steps do you want to run?", uma_config[run_type]['nsteps'])
            write_interval = ask_for_int("How often do you want to write the trajectory?", uma_config[run_type]['write_interval'])
            timestep = ask_for_float_int("What is the timestep in fs?", uma_config[run_type]['timestep'])
            log_interval = ask_for_int("How often do you want to write the log file?", uma_config[run_type]['log_interval'])
            print_ase_traj = ask_for_yes_no("Do you want to print the ASE trajectory? (y/n)", uma_config[run_type]['print_ase_traj'])

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model,
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
            for i in range(int(no_runs)):
                foundation_model_tmp = ask_for_foundational_model(uma_config, run_type)
                foundation_model.append(foundation_model_tmp)
            reversed_thermo_dict = {'Langevin': '1', 'NoseHooverChainNVT': '2', 'Bussi': '3', 'NPT': '4'}
            thermostat = ask_for_int("What thermostat do you want to use (or NPT run)? (1: Langevin, 2: NoseHooverChainNVT, 3: Bussi, 4: NPT): ", reversed_thermo_dict[uma_config[run_type]['thermostat']])
            thermo_dict = {'1': 'Langevin', '2': 'NoseHooverChainNVT', '3': 'Bussi', '4': 'NPT'}
            thermostat = thermo_dict[thermostat]
            temperature = ask_for_float_int("What is the temperature in Kelvin?", uma_config[run_type]['temperature'])
            if thermostat == 'NPT':
                pressure = ask_for_float_int("What is the pressure in bar?", uma_config[run_type]['pressure'])
            else: 
                pressure = ' '
            nsteps = ask_for_int("How many steps do you want to run?", uma_config[run_type]['nsteps'])
            write_interval = ask_for_int("How often do you want to write the trajectory?", uma_config[run_type]['write_interval'])
            timestep = ask_for_float_int("What is the timestep in fs?", uma_config[run_type]['timestep'])
            log_interval = ask_for_int("How often do you want to write the log file?", uma_config[run_type]['log_interval'])
            print_ase_traj = ask_for_yes_no("Do you want to print the ASE trajectory? (y/n)", uma_config[run_type]['print_ase_traj'])

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

            
        elif run_type == 'RECALC':
            
            foundation_model = ask_for_foundational_model(uma_config, run_type)

            input_config = {'project_name': project_name, 
                            'coord_file': coord_file, 
                            'pbc_list': pbc_mat,
                            'foundation_model': foundation_model}
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
from fairchem.core import FAIRChemCalculator
from fairchem.core import pretrained_mlip
{thermostat_code(input_config)[0]}

# Set the device
device1 = "cuda" if torch.cuda.is_available() else "cpu"

# Load the foundation model
predictor = pretrained_mlip.get_predict_unit("uma-s-1", device=device1)
uma_calc = FAIRChemCalculator(predictor, task_name="{input_config['foundation_model']}")
print("Loading of UMA completed: {input_config['foundation_model']} model")

# Load the coordinates (take care if it is the first start or a restart)
if os.path.isfile('{input_config['project_name']}.traj'):
    atoms = read('{input_config['project_name']}.traj')
    #atoms = read('{input_config['project_name']}_restart.traj')
else:
    atoms = read('{input_config['coord_file']}')			

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({cell_matrix(input_config['pbc_list'])})

atoms.calc = uma_calc

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
import torch
import time
import numpy as np
from ase import build
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import write
from ase.io import read
from fairchem.core import FAIRChemCalculator
from fairchem.core import pretrained_mlip

# Set the device
device1 = "cuda" if torch.cuda.is_available() else "cpu"

# Load the foundation model
predictor = pretrained_mlip.get_predict_unit("uma-s-1", device=device1)
uma_calc = FAIRChemCalculator(predictor, task_name="{input_config['foundation_model']}")
print("Loading of UMA completed: {input_config['foundation_model']} model")

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
    atoms.calc = uma_calc
    forces = atoms.get_forces()
    all_forces.append(forces)
    energies = atoms.get_total_energy()
    all_energies.append(energies)

# Saving the energies and forces to files
all_forces = np.array(all_forces)
np.savetxt("energies_recalc_with_uma_model_{input_config['project_name']}", all_energies)
atom = trajectory[0].get_chemical_symbols()
atom = np.array(atom)
with open('forces_recalc_with_uma_model_{input_config['project_name']}.xyz', 'w') as f: """+r"""
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


def ask_for_foundational_model(uma_config, run_type):
    """
    Function to ask the user for the foundational model and its size
    """
    foundation_model = ' '
    print("fairchem offeres serveral foundation models, so called pretrained UMA (Universal Models for Atoms) models for different classes of materials. These models are available from huggingface.co and will be downloaded automatically if you are logged to huggingface.co with your account. You need to have access to the UMA model repository.")
    print("""The available models are:
    (1) oc20: catalysis related tasks,
    (2) omat: inorganic materials,
    (3) omol: organic molecules,
    (4) odac: Metal-Organic Frameworks (MOFs),
    (5) omc: molecular crystals.""")
    foundation_model_dict = {1: 'oc20', 2: 'omat', 3: 'omol', 4: 'odac', 5: 'omc'}
    while foundation_model not in ['1', '2', '3', '4', '5', '']:
        foundation_model = input("Which foundational model do you want to use? [1-5]: ")
        if foundation_model not in ['1', '2', '3', '4', '5', '']:
            print("Invalid input! Please enter '1', '2', '3', '4' or '5'.")
    if foundation_model == '':
        foundation_model = uma_config[run_type]['foundation_model']
    else:
        foundation_model = foundation_model_dict[int(foundation_model)]

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


# Write functions 
def write_input(input_config, run_type):
    """
    Create UMA input file
    """

    if run_type == 'MD':
        input_text = create_input(input_config, run_type)
        file_name = 'md_uma.py'
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

            input_text = create_input(input_config_tmp, 'MD')
            file_name = f'md_uma.py'
            
            # Make a new directory and save the input file there
            if not os.path.exists(f'multi_md_run{i}'):
                os.makedirs(f'multi_md_run{i}')
            with open(f'multi_md_run{i}/{file_name}', 'w') as output:
                output.write(input_text)
            print(f"Input file {file_name} created in multi_md_run{i}.")


    elif run_type == 'RECALC':
        input_text = create_input(input_config, run_type)
        file_name = 'recalc_uma.py'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

def write_runscript(input_config,run_type, finetune_config=""):
    """
    Write runscript for UMA calculations: default runscript for UMA is in the default_configs/runscript_templates.py
    """
    run_type_inp_names = {'MD': 'md_uma.py', 'MULTI_MD': 'md_uma.py', 'RECALC': 'recalc_uma.py'}
    if run_type == 'MULTI_MD':
        for i in range(len(input_config['foundation_model'])):
            with open(f'multi_md_run{i}/gpu_script.job', 'w') as output:
                output.write(uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[0])
            print("Runscript created: " + uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[1])
            # Change the runscript to be executable
            os.system(f'chmod +x multi_md_run{i}/gpu_script.job')
            with open(f'multi_md_run{i}/runscript.sh', 'w') as output:
                output.write(uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[2])
            print("Runscript created: " + uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[3])
            # Change the runscript to be executable
            os.system(f'chmod +x multi_md_run{i}/runscript.sh')
    else: 
        with open('gpu_script.job', 'w') as output:
            output.write(uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[0])
        print("Runscript created: " + uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[1])
        # Change the runscript to be executable
        os.system('chmod +x gpu_script.job')
        with open('runscript.sh', 'w') as output:
            output.write(uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[2])
        print("Runscript created: " + uma_runscript(input_config['project_name'], run_type_inp_names[run_type], run_type)[3])
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
                with open(f'multi_md_run{i}/uma_input.log', 'w') as output:
                    output.write("Input file created with the following configuration:\n") 
                    # Copy the dict without the key 'foundation_model'
                    input_config_tmp = input_config.copy()
                    input_config_tmp['foundation_model'] = input_config['foundation_model'][i]
                    input_config_tmp['pbc_list'] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
                    output.write(f'"{input_config_tmp}"')  
    
    with open('uma_input.log', 'w') as output:
        output.write("Input file created with the following configuration:\n")
        try:  
            input_config["pbc_list"] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
        except:
            pass   
        # Check if foundation_model is in the input_config
        if type(input_config['foundation_model']) == list:
            # build a string with the list elements separated by a space
            foundation_string = ' '.join(f"'{item}'" for item in input_config['foundation_model'])
            foundation_string = f"'[{foundation_string}]'"
            input_config['foundation_model'] = foundation_string
        try:
            input_config = str(input_config).replace('"', '')
        except:
            pass 

        output.write(f'"{input_config}"')
    
      





