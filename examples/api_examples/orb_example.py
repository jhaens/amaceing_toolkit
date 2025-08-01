#!/usr/bin/env python3
"""
Example script demonstrating how to use the ORB API from amaceing_toolkit.
This script replicates the functionality in the orb_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import orb_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("orb/MD", exist_ok=True)
    os.chdir("orb/MD")

    print("----------------------------")
    print("Running MD example")
    md_config = {
        'project_name': 'system_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
        'dispersion_via_simenv': 'n',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y'
    }
    orb_api(run_type='MD', config=md_config)

    os.chdir("../..")  # Go back to main orb directory
    os.makedirs("orb/MULTI_MD", exist_ok=True)
    os.chdir("orb/MULTI_MD")

    print("----------------------------")
    print("Running MULTI_MD example")
    multi_md_config = {
        'project_name': 'system_multimd',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': ['orb_v2', 'orb_v3_conservative_inf'],
        'dispersion_via_simenv': ['n', 'n'],
        'modal': ['', 'omat'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y'
    }
    orb_api(run_type='MULTI_MD', config=multi_md_config)

    os.chdir("../..")  # Go back to main orb directory
    os.makedirs("orb/FINETUNE", exist_ok=True)
    os.chdir("orb/FINETUNE")

    print("----------------------------")
    print("Running FINETUNE example")
    finetune_config = {
        'project_name': 'system_finetune',
        'train_file': '../../../4KOH_92H2O_333K/data/train_file_7net.xyz',
        'foundation_model': 'orb_v2',
        'epochs': 2,
        'batch_size': 4,
        'seed': 1,
        'lr': 0.01,
    }
    orb_api(run_type='FINETUNE', config=finetune_config)

    os.chdir("../..")  # Go back to main orb directory
    os.makedirs("orb/RECALC", exist_ok=True)
    os.chdir("orb/RECALC")

    print("----------------------------")
    print("Running RECALC example")
    recalc_config = {
        'project_name': 'system_recalc',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
        'dispersion_via_simenv': 'n'
    }
    orb_api(run_type='RECALC', config=recalc_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("ORB API examples completed")

if __name__ == "__main__":
    main()