import os
import numpy as np
import datetime
import sys
import argparse, textwrap


from .utils import print_logo  
from .utils import string_to_dict
from .utils import cite_amaceing_toolkit
from .utils import equi_to_md
from .utils import ask_for_float_int
from .utils import ask_for_int
from .utils import ask_for_yes_no
from .utils import ask_for_yes_no_pbc
from .utils import ask_for_non_cubic_pbc
from amaceing_toolkit.runs.run_logger import run_logger1
from amaceing_toolkit.default_configs import configs_cp2k
from amaceing_toolkit.default_configs import kind_data_functionals 
from amaceing_toolkit.default_configs import available_functionals
from amaceing_toolkit.default_configs import cp2k_runscript


def atk_cp2k():
    """
    Main function to build CP2K input files
    """
    print_logo()
    
    # Decide if atk_cp2k is called with arguments
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Build CP2K input files: (1) Via a short Q&A: NO arguments needed! (2) Directly from the command line with a dictionary: TWO arguments needed!', formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-rt', '--run_type', type=str, help="[OPTIONAL] Which type of calculation do you want to run? ('GEO_OPT', 'CELL_OPT', 'MD', 'REFTRAJ', 'ENERGY')")
        parser.add_argument('-c', '--config', type=str, help=textwrap.dedent("""[OPTIONAL] Dictionary with the configuration:\n 
        GEO_OPT: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'max_iter': 'INT', 'print_forces' : 'ON/OFF', 'xc_functional': 'PBE(_SR)/BLYP(_SR)', 'cp2k_newer_than_2023x' : 'y/n'}"\n
        CELL_OPT: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'max_iter': 'INT', 'keep_symmetry' : 'TREU/FALSE', 'symmetry' : 'CUBIC/TRICLINIC/NONE/MONOCLINIC/ORTHORHOMBIC/TETRAGONAL/TRIGONAL/HEXAGONAL', 'xc_functional': 'PBE(_SR)/BLYP(_SR)', 'cp2k_newer_than_2023x' : 'y/n'}"\n
        MD: "{'project_name' : 'NAME', 'coord_file' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'ensemble' : 'NVE/NVT/NPT_F/NPT_I', 'nsteps' : 'INT', 'timestep' : 'FLOAT', 'temperature' : 'FLOAT', 'print_forces' : 'ON/OFF', 'print_velocities' : 'ON/OFF', 'xc_functional' : 'PBE(_SR)/BLYP(_SR)', 'cp2k_newer_than_2023x' : 'y/n'}"\n
        REFTRAJ: "{'project_name' : 'NAME', 'ref_traj' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'nsteps' : 'INT', 'stride' : 'INT', 'print_forces' : 'ON/OFF', 'print_velocities' : 'ON/OFF', 'xc_functional' : 'PBE(_SR)/BLYP(_SR)', 'cp2k_newer_than_2023x' : 'y/n'}"\n 
        ENERGY: "{'project_name' : 'NAME', 'ref_traj' : 'FILE', 'pbc_list' = '[FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT FLOAT]', 'xc_functional' : 'PBE(_SR)/BLYP(_SR)'}" """))
        args = parser.parse_args()
        if args.config != ' ':
            try:
                input_config = string_to_dict(args.config)
                if np.size(input_config['pbc_list']) == 3: # Keep compatibility with old input files
                    input_config['pbc_list'] = np.array([[input_config['pbc_list'][0], 0, 0], [0, input_config['pbc_list'][1], 0], [0, 0, input_config['pbc_list'][2]]])
                else:
                    input_config['pbc_list'] = np.array(input_config['pbc_list']).reshape(3,3)
                write_input(input_config, args.run_type)
        
                with open('cp2k_input.log', 'w') as output:
                    output.write("Input file created with the following configuration:\n") 
                    output.write(f"{args.config}")

                if args.run_type == 'MD':
                    if input_config['equilibration_run'] == 'y':
                        write_runscript(input_config['project_name'], args.run_type, 'y') 
                        # Write python script to convert equilibration input to MD input
                        equi_to_md(input_config['project_name'], input_config['coord_file'])
                    else: 
                        write_runscript(input_config['project_name'], args.run_type)
                else:
                    write_runscript(input_config['project_name'], args.run_type)

            except KeyError:
                print("The dictionary is not in the right format. Please check the help page.")

    else:
        cp2k_form()

    cite_amaceing_toolkit()
    

def cp2k_form():
    """
    Questions to build CP2K input files
    """
   
    print("\n")
    print("Welcome to the CP2K input file builder!")
    print("This tool will help you build input files for CP2K calculations.")
    print("Please answer the following questions to build the input file.")
    print("################################################################################################")
    print("## Defaults are set in the config file: /src/amaceing_toolkit/default_configs/cp2k_configs.py ##")
    print("## For more advanced options, please edit the resulting input file.                           ##")
    loaded_config = 'default'
    cp2k_config = configs_cp2k(loaded_config)
    print(f"## Loading config: " + loaded_config + "                                                                    ##")
    if cp2k_config['cp2k_newer_than_2023x'] == 'y': print("## The resulting input file is suited for only for versions of cp2k newer than v2023.x!       ##")
    print("################################################################################################")
    print("\n")

    # Ask user for input data
    coord_file = input("What is the name of the coordinate file (or reference trajecory)? " +"[" + cp2k_config['coord_file'] + "]: ")
    if coord_file == '':
        coord_file = cp2k_config['coord_file']
    assert os.path.isfile(coord_file), "Coordinate file does not exist!"
    
    box_cubic = ask_for_yes_no_pbc("Is the box cubic? (y/n/pbc)", cp2k_config['box_cubic'])

    if box_cubic == 'y':
        box_xyz = ask_for_float_int("What is the length of the box in Å?", str(10.0))
        pbc_mat = np.array([[box_xyz, 0.0, 0.0],[0.0, box_xyz, 0.0],[0.0, 0.0, box_xyz]])
    elif box_cubic == 'n':
        pbc_mat = ask_for_non_cubic_pbc()
    else:
        pbc_mat = np.loadtxt(box_cubic)
    
    # Configure GLOBAL and template usage
    run_type_dict = {'1': 'GEO_OPT', '2': 'CELL_OPT', '3': 'MD', '4': 'REFTRAJ', '5': 'ENERGY'}
    run_type = ' '
    while run_type != '1' and run_type != '2' and run_type != '3' and run_type != '4' and run_type !='5' and run_type != '':
        run_type = input("What type of calculation do you want to run? (1=GEO_OPT, 2=CELL_OPT, 3=MD, 4=REFTRAJ, 5=ENERGY) " + "[" + cp2k_config['run_type'] + "]: ")
        if run_type != '1' and run_type != '2' and run_type != '3' and run_type != '4' and run_type != '5' and run_type != '':
            print("Invalid input. Please enter '1', '2', '3', '4' or '5'.")
    if run_type == '':
        run_type = cp2k_config['run_type']
    else:
        run_type = run_type_dict[run_type]


    project_name = input("What is the name of the project?: ")
    if project_name == '':
        project_name = f'{run_type}_{datetime.datetime.now().strftime("%Y%m%d")}'

    print("Default settings for this run type: " + str(cp2k_config[run_type]))

    use_default_input = ask_for_yes_no("Do you want to use the default input settings? (y/n)", cp2k_config['use_default_input'])
    if use_default_input == 'y':
        input_config = config_wrapper(True, run_type, cp2k_config, coord_file, pbc_mat, project_name)
    else:
        small_changes = ask_for_yes_no("Do you want to make small changes to the default settings? (y/n)", "n")
        if small_changes == 'y':

            changing = True
            while changing:
                # List of mace_config[run_type] keys:
                settings = list(cp2k_config[run_type].keys())

                # Print the available settings with the default value
                print("Available settings:")
                setting_number = 1
                setting_number_list = []
                for setting in settings:
                    print(f"({setting_number}) {setting}: {cp2k_config[run_type][setting]}")
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
                cp2k_config[run_type][settings[int(setting_to_change) - 1]] = new_value

                # Change another setting?
                dict_onoff = {'y': True, 'n': False}
                changing = dict_onoff[ask_for_yes_no("Do you want to change another setting? (y/n)", 'n')]
            
            input_config = config_wrapper(True, run_type, cp2k_config, coord_file, pbc_mat, project_name)


        else: 
            input_config = config_wrapper(False, run_type, cp2k_config, coord_file, pbc_mat, project_name)

    
    # Write the input file
    write_input(input_config, run_type)

    # Write the runscript
    if run_type == 'MD':
        if input_config['equilibration_run'] == 'y':
            write_runscript(input_config['project_name'], run_type, 'y') 
            # Write python script to convert equilibration input to MD input
            equi_to_md(project_name, coord_file)
        else: 
            write_runscript(input_config['project_name'], run_type)
    else:
        write_runscript(input_config['project_name'], run_type)

    # Write the configuration to a log file
    write_log(input_config)

    # Log the run
    run_logger1(run_type,os.getcwd())


def config_wrapper(default, run_type, cp2k_config, coord_file, pbc_mat, project_name):
    """
    Create dictionary for create_input
    """
    # Tranlsate dictionaries
    onoff_dict = {'y': 'ON', 'n': 'OFF'}
    truefalse_dict = {'y': 'TRUE', 'n': 'FALSE'}

    # Use default input data
    if default == True:
        if run_type == 'GEO_OPT':
            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'max_iter': cp2k_config['GEO_OPT']['max_iter'],
                            'print_forces': onoff_dict[cp2k_config['GEO_OPT']['print_forces']], 
                            'xc_functional': cp2k_config['GEO_OPT']['xc_functional'],
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
        elif run_type == 'CELL_OPT':
            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'max_iter': cp2k_config['CELL_OPT']['max_iter'],
                            'keep_symmetry': onoff_dict[cp2k_config['CELL_OPT']['keep_symmetry']],
                            'symmetry': cp2k_config['CELL_OPT']['symmetry'],
                            'xc_functional': cp2k_config['CELL_OPT']['xc_functional'],
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
        elif run_type == 'MD':
            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'ensemble': cp2k_config['MD']['ensemble'],
                            'nsteps': cp2k_config['MD']['nsteps'],
                            'timestep': cp2k_config['MD']['timestep'],
                            'temperature': cp2k_config['MD']['temperature'],
                            'print_forces': onoff_dict[cp2k_config['MD']['print_forces']],
                            'print_velocities': onoff_dict[cp2k_config['MD']['print_velocities']],
                            'xc_functional': cp2k_config['MD']['xc_functional'],
                            'equilibration_steps' : cp2k_config['MD']['equilibration_steps'],
                            'equilibration_run': cp2k_config['MD']['equilibration_run'],
                            'pressure_b': cp2k_config['MD']['pressure_b'],
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
        elif run_type == 'REFTRAJ':
            input_config = {'project_name': project_name,
                            'ref_traj': coord_file,
                            'pbc_list': pbc_mat,
                            'nsteps': cp2k_config['REFTRAJ']['nsteps'],
                            'stride': cp2k_config['REFTRAJ']['stride'],
                            'print_forces': onoff_dict[cp2k_config['REFTRAJ']['print_forces']],
                            'print_velocities': onoff_dict[cp2k_config['REFTRAJ']['print_velocities']],
                            'xc_functional': cp2k_config['REFTRAJ']['xc_functional'],
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
        elif run_type == 'ENERGY':
            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'xc_functional': cp2k_config['ENERGY']['xc_functional'],
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
            
    # Ask user for input data
    else:
        if run_type == 'GEO_OPT':
            max_iter = ask_for_int("What is the maximum number of iterations?", cp2k_config['GEO_OPT']['max_iter'])

            print_forces = ask_for_yes_no("Do you want to print the forces? (y/n)", cp2k_config['GEO_OPT']['print_forces'])
            print_forces = onoff_dict[print_forces]
            
            print(f"Available exchange-correlation functionals: {available_functionals()}")
            xc_functional = input("What is the exchange-correlation functional? " + "[" + cp2k_config['GEO_OPT']['xc_functional'] + "]: ")
            if xc_functional == '':
                xc_functional = cp2k_config['GEO_OPT']['xc_functional']

            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'max_iter': max_iter,
                            'print_forces': print_forces, 
                            'xc_functional': xc_functional,
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
            
        elif run_type == 'CELL_OPT':
            max_iter = ask_for_int("What is the maximum number of iterations?", cp2k_config['CELL_OPT']['max_iter'])

            keep_symmetry = ask_for_yes_no("Do you want to keep the symmetry? (y/n)", cp2k_config['CELL_OPT']['keep_symmetry'])
            keep_symmetry = truefalse_dict[keep_symmetry]

            # to do: include the right symmetry options
            symmetry = ' '
            while symmetry != 'CUBIC' and symmetry != 'TRICLINIC' and symmetry != 'NONE' and symmetry != 'MONOCLINIC' and symmetry != 'ORTHORHOMBIC' and symmetry != 'TETRAGONAL' and symmetry != 'TRIGONAL' and symmetry != 'HEXAGONAL':
                symmetry = input("What is the symmetry? " + "[" + cp2k_config['CELL_OPT']['symmetry'] + "]: ")
                if symmetry == '':
                    symmetry = cp2k_config['CELL_OPT']['symmetry']
                elif symmetry != 'CUBIC' and symmetry != 'TRICLINIC' and symmetry != 'NONE' and symmetry != 'MONOCLINIC' and symmetry != 'ORTHORHOMBIC' and symmetry != 'TETRAGONAL' and symmetry != 'TRIGONAL' and symmetry != 'HEXAGONAL':
                    print("Invalid input. Please enter a valid symmetry: CUBIC, NONE, TRICLINIC, TETRAGONAL, MONOCLINIC, TRIGONAL, HEXAGONAL, ORTHOROMBIC.")
            
            print(f"Available exchange-correlation functionals: {available_functionals()}")
            xc_functional = input("What is the exchange-correlation functional? " + "[" + cp2k_config['CELL_OPT']['xc_functional'] + "]: ")
            if xc_functional == '':
                xc_functional = cp2k_config['CELL_OPT']['xc_functional']
            
            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'max_iter': max_iter,
                            'keep_symmetry': keep_symmetry,
                            'symmetry': symmetry,
                            'xc_functional': xc_functional,
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}

        elif run_type == 'MD':
            ensemble = ' '
            while ensemble != 'NVT' and ensemble != 'NPT_F' and ensemble != 'NPT_I':
                ensemble = input("What is the ensemble? " + "[" + cp2k_config['MD']['ensemble'] + "]: ")
                if ensemble == '':
                    ensemble = cp2k_config['MD']['ensemble']
                elif ensemble != 'NVT' and ensemble != 'NPT_F' and ensemble != 'NPT_I':
                    print("Invalid input. Please enter a valid ensemble: NVT, NPT_F, NPT_I.")
            
            pressure_b = '' # placeholder
            if ensemble == 'NPT_F' or ensemble == 'NPT_I':
                input_config['pressure_b'] = ask_for_float_int("What is the pressure in bar?", cp2k_config['MD']['pressure_b'])
            
            nsteps = ask_for_int("What is the number of steps?", cp2k_config['MD']['nsteps'])
            
            timestep = ask_for_float_int("What is the timestep in fs?", cp2k_config['MD']['timestep'])

            temperature = ask_for_float_int("What is the temperature in K?", cp2k_config['MD']['temperature'])
                
            print_forces = ask_for_yes_no("Do you want to print the forces? (y/n)", cp2k_config['MD']['print_forces'])
            print_forces = onoff_dict[print_forces]

            print_velocities = ask_for_yes_no("Do you want to print the velocities? (y/n)", cp2k_config['MD']['print_velocities'])
            print_velocities = onoff_dict[print_velocities]

            print(f"Available exchange-correlation functionals: {available_functionals()}")
            xc_functional = input("What is the exchange-correlation functional? " + "[" + cp2k_config['MD']['xc_functional'] + "]: ")
            if xc_functional == '':
                xc_functional = cp2k_config['MD']['xc_functional']

            equi_prod = ask_for_yes_no("Do you want to run an extra equilibration run input file? (y/n)", cp2k_config['MD']['equilibration_run'])

            if equi_prod == 'y':
                equi_nsteps = ask_for_int("What is the number of steps for the equilibration run?", cp2k_config['MD']['equilibration_steps'])
            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'ensemble': ensemble,
                            'nsteps': nsteps,
                            'timestep': timestep,
                            'temperature': temperature,
                            'print_forces': print_forces,
                            'print_velocities': print_velocities,
                            'xc_functional': xc_functional,
                            'equilibration_run': equi_prod,
                            'equilibration_steps': equi_nsteps,
                            'pressure_b': pressure_b,
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
            
        elif run_type == 'REFTRAJ':
            
            nsteps = ask_for_int("What is the number of steps?", cp2k_config['REFTRAJ']['nsteps'])
            
            stride = ask_for_float_int("What is the stride in steps?", cp2k_config['REFTRAJ']['stride'])

            print_forces = ask_for_yes_no("Do you want to print the forces? (y/n)", cp2k_config['REFTRAJ']['print_forces'])
            print_forces = onoff_dict[print_forces]

            print_velocities = ask_for_yes_no("Do you want to print the velocities? (y/n)", cp2k_config['REFTRAJ']['print_velocities'])
            print_velocities = onoff_dict[print_velocities]

            print(f"Available exchange-correlation functionals: {available_functionals()}")
            xc_functional = input("What is the exchange-correlation functional? " + "[" + cp2k_config['REFTRAJ']['xc_functional'] + "]: ")
            if xc_functional == '':
                xc_functional = cp2k_config['MD']['xc_functional']

            input_config = {'project_name': project_name,
                            'ref_traj': coord_file,
                            'pbc_list': pbc_mat,
                            'nsteps': nsteps,
                            'stride': stride,
                            'print_forces': print_forces,
                            'print_velocities': print_velocities,
                            'xc_functional': xc_functional,
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
            
        elif run_type == 'ENERGY':

            print(f"Available exchange-correlation functionals: {available_functionals()}")
            xc_functional = input("What is the exchange-correlation functional? " + "[" + cp2k_config['ENERGY']['xc_functional'] + "]: ")
            if xc_functional == '':
                xc_functional = cp2k_config['ENERGY']['xc_functional']

            input_config = {'project_name': project_name,
                            'coord_file': coord_file,
                            'pbc_list': pbc_mat,
                            'xc_functional': xc_functional,
                            'cp2k_newer_than_2023x': cp2k_config['cp2k_newer_than_2023x']}
    return input_config



def create_input(input_config, run_type, equi_prod=''):
    """
    Create input file for CP2K calculation: GEO_OPT, CELL_OPT, MD or REFTRAJ
    """

    # Check if CP2K version is newer than 2023x, if so, add IGNORE_CONVERGENCE_FAILURE
    if input_config["cp2k_newer_than_2023x"] == "y":
        ignore_convergence_failure = "IGNORE_CONVERGENCE_FAILURE T"
    else:
        ignore_convergence_failure = ""

    # Obtain the description of the kind of the atoms in the system
    kind_data = kind_data_functionals(input_config['xc_functional'])

    if run_type == 'GEO_OPT':
        return f"""
&GLOBAL
    PROJECT {input_config['project_name']}
    RUN_TYPE GEO_OPT
&END GLOBAL

&MOTION
    &GEO_OPT
        OPTIMIZER BFGS
        MAX_ITER {input_config['max_iter']}
    &END GEO_OPT
    &PRINT
        &FORCES {input_config['print_forces']}
            FILENAME force.xyz
        &END FORCES
    &END PRINT
&END MOTION

&FORCE_EVAL
    METHOD QUICKSTEP
    &DFT
        BASIS_SET_FILE_NAME BASIS_MOLOPT
        POTENTIAL_FILE_NAME POTENTIAL
        &MGRID
            CUTOFF 320
            NGRIDS 4
            REL_CUTOFF 40
        &END MGRID
        &QS
            EPS_DEFAULT 1.0E-10
            EPS_GVG 1.0E-5
            EPS_PGF_ORB 1.0E-5
            EXTRAPOLATION ASPC
            EXTRAPOLATION_ORDER 3
            METHOD GPW
        &END QS
        &XC 
            &XC_GRID
                XC_SMOOTH_RHO NN10
                XC_DERIV NN10_SMOOTH
            &END XC_GRID
            &XC_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
            &END XC_FUNCTIONAL
            &VDW_POTENTIAL
                POTENTIAL_TYPE PAIR_POTENTIAL
                &PAIR_POTENTIAL
                    TYPE DFTD3
                    PARAMETER_FILE_NAME dftd3.dat
                    REFERENCE_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
                &END PAIR_POTENTIAL
            &END VDW_POTENTIAL
        &END XC
        &SCF
            EPS_SCF 1.0E-6
            MAX_SCF 100
            {ignore_convergence_failure}
            &OT
                MINIMIZER DIIS
                PRECONDITIONER FULL_SINGLE_INVERSE
            &END OT
            &PRINT
                &RESTART
                    ADD_LAST NUMERIC
                    &EACH
                        MD 0
                    &END EACH
                &END RESTART
            &END PRINT
        &END SCF
    &END DFT
    &SUBSYS
        &CELL
            A {input_config['pbc_list'][0,0]} {input_config['pbc_list'][0,1]} {input_config['pbc_list'][0,2]}
            B {input_config['pbc_list'][1,0]} {input_config['pbc_list'][1,1]} {input_config['pbc_list'][1,2]}
            C {input_config['pbc_list'][2,0]} {input_config['pbc_list'][2,1]} {input_config['pbc_list'][2,2]}
            PERIODIC XYZ
        &END CELL
        &TOPOLOGY
            COORD_FILE_NAME {input_config['coord_file']}
            COORD_FILE_FORMAT {input_config['coord_file'].split('.')[-1]}
        &END TOPOLOGY

    {kind_data}

    &END SUBSYS

&END FORCE_EVAL
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

    elif run_type == 'CELL_OPT':
        return f"""
&GLOBAL
    PROJECT {input_config['project_name']}
    RUN_TYPE CELL_OPT
&END GLOBAL

&MOTION
    &CELL_OPT
        MAX_ITER {input_config['max_iter']}
        KEEP_SYMMETRY {input_config['keep_symmetry']}
    &END CELL_OPT
&END MOTION

&FORCE_EVAL
    METHOD QUICKSTEP
    STRESS_TENSOR Analytical
    &DFT
        BASIS_SET_FILE_NAME BASIS_MOLOPT
        POTENTIAL_FILE_NAME POTENTIAL
        &MGRID
            CUTOFF 320
            NGRIDS 4
            REL_CUTOFF 40
        &END MGRID
        &QS
            EPS_DEFAULT 1.0E-10
            EPS_GVG 1.0E-5
            EPS_PGF_ORB 1.0E-5
            EXTRAPOLATION ASPC
            EXTRAPOLATION_ORDER 3
            METHOD GPW
        &END QS
        &XC 
            &XC_GRID
                XC_SMOOTH_RHO NN10
                XC_DERIV NN10_SMOOTH
            &END XC_GRID
            &XC_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
            &END XC_FUNCTIONAL
            &VDW_POTENTIAL
                POTENTIAL_TYPE PAIR_POTENTIAL
                &PAIR_POTENTIAL
                    TYPE DFTD3
                    PARAMETER_FILE_NAME dftd3.dat
                    REFERENCE_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
                &END PAIR_POTENTIAL
            &END VDW_POTENTIAL
        &END XC
        &SCF
            EPS_SCF 1.0E-6
            MAX_SCF 100
            {ignore_convergence_failure}
            &OT
                MINIMIZER DIIS
                PRECONDITIONER FULL_SINGLE_INVERSE
            &END OT
            &PRINT
                &RESTART
                    ADD_LAST NUMERIC
                    &EACH
                        MD 0
                    &END EACH
                &END RESTART
            &END PRINT
        &END SCF
    &END DFT
    &SUBSYS
        &CELL
            A {input_config['pbc_list'][0,0]} {input_config['pbc_list'][0,1]} {input_config['pbc_list'][0,2]}
            B {input_config['pbc_list'][1,0]} {input_config['pbc_list'][1,1]} {input_config['pbc_list'][1,2]}
            C {input_config['pbc_list'][2,0]} {input_config['pbc_list'][2,1]} {input_config['pbc_list'][2,2]}
            PERIODIC XYZ
            SYMMETRY {input_config['symmetry']}
        &END CELL
        &TOPOLOGY
            COORD_FILE_NAME {input_config['coord_file']}
            COORD_FILE_FORMAT {input_config['coord_file'].split('.')[-1]}
        &END TOPOLOGY
    
    {kind_data}

    &END SUBSYS

&END FORCE_EVAL
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

    elif run_type == 'REFTRAJ':
        # Create frame0 file and return the name (only works with xyz files)
        coord_frame0_name = create_frame0(input_config['ref_traj'], input_config['project_name'])

        return f"""
&GLOBAL
    PROJECT {input_config['project_name']}
    RUN_TYPE MD
    PRINT_LEVEL LOW
&END GLOBAL

&MOTION
    &MD
        ENSEMBLE REFTRAJ
        STEPS {input_config['nsteps']}
        &REFTRAJ
            TRAJ_FILE_NAME {input_config['ref_traj']}
            STRIDE {input_config['stride']}
            FIRST_SNAPSHOT 1
            EVAL_ENERGY_FORCES  
            EVAL_FORCES
        &END REFTRAJ
    &END MD
    &PRINT
        &FORCES {input_config['print_forces']}
            FILENAME force.xyz
        &END FORCES
        &VELOCITIES {input_config['print_velocities']}
            FILENAME velocities.xyz
        &END VELOCITIES
        &RESTART
            ADD_LAST NUMERIC
            &EACH
                MD 1
            &END EACH
        &END RESTART
    &END PRINT
&END MOTION

&FORCE_EVAL
    METHOD QUICKSTEP
    &DFT
        BASIS_SET_FILE_NAME BASIS_MOLOPT
        POTENTIAL_FILE_NAME POTENTIAL
        &MGRID
            CUTOFF 320
            NGRIDS 4
            REL_CUTOFF 40
        &END MGRID
        &QS
            EPS_DEFAULT 1.0E-10
            EPS_GVG 1.0E-5
            EPS_PGF_ORB 1.0E-5
            EXTRAPOLATION ASPC
            EXTRAPOLATION_ORDER 3
            METHOD GPW
        &END QS
        &XC 
            &XC_GRID
                XC_SMOOTH_RHO NN10
                XC_DERIV NN10_SMOOTH
            &END XC_GRID
            &XC_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
            &END XC_FUNCTIONAL
            &VDW_POTENTIAL
                POTENTIAL_TYPE PAIR_POTENTIAL
                &PAIR_POTENTIAL
                    TYPE DFTD3
                    PARAMETER_FILE_NAME dftd3.dat
                    REFERENCE_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
                &END PAIR_POTENTIAL
            &END VDW_POTENTIAL
        &END XC
        &SCF
            EPS_SCF 1.0E-6
            MAX_SCF 100
            {ignore_convergence_failure}
            &OT
                MINIMIZER DIIS
                PRECONDITIONER FULL_SINGLE_INVERSE
            &END OT
            &PRINT
                &RESTART
                    ADD_LAST NUMERIC
                    &EACH
                        MD 0
                    &END EACH
                &END RESTART
            &END PRINT
        &END SCF
    &END DFT
    &SUBSYS
        &CELL
            A {input_config['pbc_list'][0,0]} {input_config['pbc_list'][0,1]} {input_config['pbc_list'][0,2]}
            B {input_config['pbc_list'][1,0]} {input_config['pbc_list'][1,1]} {input_config['pbc_list'][1,2]}
            C {input_config['pbc_list'][2,0]} {input_config['pbc_list'][2,1]} {input_config['pbc_list'][2,2]}
            PERIODIC XYZ
        &END CELL
        &TOPOLOGY
            COORD_FILE_NAME {coord_frame0_name}
            COORD_FILE_FORMAT {coord_frame0_name.split('.')[-1]}
        &END TOPOLOGY
    
    {kind_data}

    &END SUBSYS

&END FORCE_EVAL
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
    
    elif run_type == 'MD':
        thermstat_setup = {'equilibration': ['MASSIVE', 10.0, input_config["equilibration_steps"], str(input_config['project_name']+'_equi') ], 'production': ['GLOBAL', 100.0, input_config['nsteps'], input_config['project_name']]}
        return f"""
&GLOBAL
    PROJECT {thermstat_setup[equi_prod][3]}
    RUN_TYPE MD
    PRINT_LEVEL LOW
&END GLOBAL

&MOTION
    &MD
        ENSEMBLE {input_config['ensemble']}
        STEPS {thermstat_setup[equi_prod][2]}
        TIMESTEP {input_config['timestep']}
        TEMPERATURE {input_config['temperature']}
        &THERMOSTAT
            REGION {thermstat_setup[equi_prod][0]}
            &NOSE
                LENGTH 3
                YOSHIDA 3
                TIMECON {thermstat_setup[equi_prod][1]}
                MTS 2
            &END NOSE
        &END THERMOSTAT {barostat_setup(input_config)}    
    &END MD
    &PRINT
        &FORCES {input_config['print_forces']}
            FILENAME force.xyz
        &END FORCES
        &VELOCITIES {input_config['print_velocities']}
            FILENAME velocities.xyz
        &END VELOCITIES
        &RESTART
            ADD_LAST NUMERIC
            &EACH
                MD 1
            &END EACH
        &END RESTART
    &END PRINT
&END MOTION

&FORCE_EVAL
    METHOD QUICKSTEP
    &DFT
        BASIS_SET_FILE_NAME BASIS_MOLOPT
        POTENTIAL_FILE_NAME POTENTIAL
        &MGRID
            CUTOFF 320
            NGRIDS 4
            REL_CUTOFF 40
        &END MGRID
        &QS
            EPS_DEFAULT 1.0E-10
            EPS_GVG 1.0E-5
            EPS_PGF_ORB 1.0E-5
            EXTRAPOLATION ASPC
            EXTRAPOLATION_ORDER 3
            METHOD GPW
        &END QS
        &XC 
            &XC_GRID
                XC_SMOOTH_RHO NN10
                XC_DERIV NN10_SMOOTH
            &END XC_GRID
            &XC_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
            &END XC_FUNCTIONAL
            &VDW_POTENTIAL
                POTENTIAL_TYPE PAIR_POTENTIAL
                &PAIR_POTENTIAL
                    TYPE DFTD3
                    PARAMETER_FILE_NAME dftd3.dat
                    REFERENCE_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
                &END PAIR_POTENTIAL
            &END VDW_POTENTIAL
        &END XC
        &SCF
            EPS_SCF 1.0E-6
            MAX_SCF 100
            {ignore_convergence_failure}
            &OT
                MINIMIZER DIIS
                PRECONDITIONER FULL_SINGLE_INVERSE
            &END OT
            &PRINT
                &RESTART
                    ADD_LAST NUMERIC
                    &EACH
                        MD 0
                    &END EACH
                &END RESTART
            &END PRINT
        &END SCF
    &END DFT
    &SUBSYS
        &CELL
            A {input_config['pbc_list'][0,0]} {input_config['pbc_list'][0,1]} {input_config['pbc_list'][0,2]}
            B {input_config['pbc_list'][1,0]} {input_config['pbc_list'][1,1]} {input_config['pbc_list'][1,2]}
            C {input_config['pbc_list'][2,0]} {input_config['pbc_list'][2,1]} {input_config['pbc_list'][2,2]}
            PERIODIC XYZ
        &END CELL
        &TOPOLOGY
            COORD_FILE_NAME {input_config['coord_file']}
            COORD_FILE_FORMAT {input_config['coord_file'].split('.')[-1]}
        &END TOPOLOGY

    {kind_data}

    &END SUBSYS


&END FORCE_EVAL
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
    elif run_type == 'ENERGY':
        return f"""
&GLOBAL
    PROJECT {input_config['project_name']}
    RUN_TYPE ENERGY
    PRINT_LEVEL LOW
&END GLOBAL


&FORCE_EVAL
    METHOD QUICKSTEP
    &DFT
        UKS
        BASIS_SET_FILE_NAME BASIS_MOLOPT
        POTENTIAL_FILE_NAME POTENTIAL
        &MGRID
            CUTOFF 320
            NGRIDS 5
            REL_CUTOFF 40
        &END MGRID
        &QS
            EPS_DEFAULT 1.0E-10
            EPS_GVG 1.0E-5
            EPS_PGF_ORB 1.0E-5
            EXTRAPOLATION ASPC
            EXTRAPOLATION_ORDER 3
            METHOD GPW
        &END QS
        &XC 
            &XC_GRID
                XC_SMOOTH_RHO NN10
                XC_DERIV NN10_SMOOTH
            &END XC_GRID
            &XC_FUNCTIONAL {input_config['xc_functional'].split('_SR')[0]}
            &END XC_FUNCTIONAL
        &END XC
        &SCF
            EPS_SCF 1.0E-6
            MAX_SCF 1000
            {ignore_convergence_failure}
            &OT
                MINIMIZER DIIS
                PRECONDITIONER FULL_SINGLE_INVERSE
            &END OT
            &PRINT
                &RESTART SILENT
                    ADD_LAST NUMERIC
                    &EACH
                        MD 0
                    &END EACH
                &END RESTART
            &END PRINT
        &END SCF
    &END DFT
    &SUBSYS
        &CELL
            A {input_config['pbc_list'][0,0]} {input_config['pbc_list'][0,1]} {input_config['pbc_list'][0,2]}
            B {input_config['pbc_list'][1,0]} {input_config['pbc_list'][1,1]} {input_config['pbc_list'][1,2]}
            C {input_config['pbc_list'][2,0]} {input_config['pbc_list'][2,1]} {input_config['pbc_list'][2,2]}
            PERIODIC XYZ
            MULTIPLE_UNIT_CELL  1 1 1
        &END CELL
        &TOPOLOGY
            COORD_FILE_NAME {input_config['coord_file']}
            COORD_FILE_FORMAT {input_config['coord_file'].split('.')[-1]}
        &END TOPOLOGY

    {kind_data}

    &END SUBSYS

&END FORCE_EVAL
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

def barostat_setup(input_config):
    if input_config['ensemble'] == 'NPT_F' or input_config['ensemble'] == 'NPT_I':
        if input_config['pressure_b'] == '':
            input_config['pressure_b'] = '1.0'
        return f"""
&BAROSTAT
    PRESSURE {input_config['pressure_b']}
    TIMECON 1000
&END BAROSTAT"""
    else:
        return ""

# Write functions
def write_input(input_config, run_type):
    """
    Create CP2K input file
    """

    if run_type == 'GEO_OPT':
        input_text = create_input(input_config, run_type)
        file_name = 'geoopt_cp2k.inp'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

    elif run_type == 'CELL_OPT':
        input_text = create_input(input_config, run_type)
        file_name = 'cellopt_cp2k.inp'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

    elif run_type == 'MD':
        if input_config['equilibration_run'] == 'y':
            input_text = create_input(input_config, run_type, 'equilibration')
            file_name = 'md_equilibration_cp2k.inp'
            with open(file_name, 'w') as output:
                output.write(input_text)
            print(f"Input file {file_name} created.")
        
        input_text = create_input(input_config, run_type, 'production')
        file_name = 'md_cp2k.inp'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")
    
    elif run_type == 'REFTRAJ':
        input_text = create_input(input_config, run_type)
        file_name = 'reftraj_cp2k.inp'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")

    elif run_type == 'ENERGY':
        input_text = create_input(input_config, run_type)
        file_name = 'energy_cp2k.inp'
        with open(file_name, 'w') as output:
            output.write(input_text)
        print(f"Input file {file_name} created.")


def write_log(input_config):
    """
    Write configuration to log file with the right format to be read by direct input
    """
    with open('cp2k_input.log', 'w') as output:
        output.write("Input file created with the following configuration:\n") 
        input_config["pbc_list"] = f'[{input_config["pbc_list"][0,0]} {input_config["pbc_list"][0,1]} {input_config["pbc_list"][0,2]} {input_config["pbc_list"][1,0]} {input_config["pbc_list"][1,1]} {input_config["pbc_list"][1,2]} {input_config["pbc_list"][2,0]} {input_config["pbc_list"][2,1]} {input_config["pbc_list"][2,2]}]'
        #input_config = str(input_config).replace("'", '')
        output.write(f"{input_config}")

def write_runscript(project_name,run_type,equi_run=''):
    """
    Write runscript for CP2K calculations: default runscript for cp2k is in the default_configs/runscript_templates.py
    """
    run_type_inp_names = {'GEO_OPT': 'geoopt_cp2k.inp', 'CELL_OPT': 'cellopt_cp2k.inp', 'MD': ['md_cp2k.inp', 'md_equilibration_cp2k.inp'], 'REFTRAJ': 'reftraj_cp2k.inp', 'ENERGY': 'energy_cp2k.inp'}
    

    if run_type == 'MD':
        with open('runscript.sh', 'w') as output:
            output.write(cp2k_runscript(project_name, run_type_inp_names[run_type][0])[0])
        os.system('chmod +x runscript.sh')
        print("Runscript for the production run created: " + cp2k_runscript(project_name, run_type_inp_names[run_type][0])[1])
        if equi_run == 'y':
            with open('runscript_equilibration.sh', 'w') as output2:
                output2.write(cp2k_runscript(project_name, run_type_inp_names[run_type][1])[0])
            print("Runscript for the equilibration run created: " + cp2k_runscript(project_name, run_type_inp_names[run_type][1])[1])
            os.system('chmod +x runscript_equilibration.sh')

    else: 
        with open('runscript.sh', 'w') as output:
            output.write(cp2k_runscript(project_name, run_type_inp_names[run_type])[0])
        print("Runscript created: " + cp2k_runscript(project_name, run_type_inp_names[run_type])[1])
        os.system('chmod +x runscript.sh')

def create_frame0(ref_traj, project_name):
    coord_file_name = project_name.split('.')[0] + "_frame0.xyz"

    number_of_atoms = 0 

    with open(ref_traj, 'r') as input:
        for i, line in enumerate(input):
            if i == 0:
                number_of_atoms = int(line)
                break
    
    # Write the first frame to a new file
    with open(ref_traj, 'r') as input, open(coord_file_name, 'w') as output:
        for i, line in enumerate(input):
            if i < number_of_atoms + 2:
                output.write(line)
            else:
                break
    return coord_file_name
