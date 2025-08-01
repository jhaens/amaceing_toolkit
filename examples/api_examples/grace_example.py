#!/usr/bin/env python3
"""
Example script demonstrating how to use the Grace API from amaceing_toolkit.
This script replicates the functionality in the grace_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import grace_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("grace/MD", exist_ok=True)
    os.chdir("grace/MD")
    
    print("----------------------------")
    print("Running MD example")
    md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'GRACE-1L-OMAT',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y',
        'simulation_environment': 'ase'
    }
    grace_api(run_type='MD', config=md_config)

    os.chdir("../..")  # Go back to main grace directory
    os.makedirs("grace/MULTI_MD", exist_ok=True)
    os.chdir("grace/MULTI_MD")
    
    print("----------------------------")
    print("Running MULTI_MD example")
    multi_md_config = {
        'project_name': '4koh_92h2o_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': ['GRACE-1L-OAM', 'GRACE-1L-OMAT'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y',
        'simulation_environment': 'ase'
    }
    grace_api(run_type='MULTI_MD', config=multi_md_config)

    os.chdir("../..")  # Go back to main grace directory
    os.makedirs("grace/FINETUNE", exist_ok=True)
    os.chdir("grace/FINETUNE")
    
    print("----------------------------")
    print("Running FINETUNE example")
    finetune_config = {
        'project_name': '4koh_92h2o_ft',
        'train_file': '../../../4KOH_92H2O_333K/data/train_file_7net.xyz',
        'foundation_model': 'GRACE-1L-OAM',
        'epochs': 2,
        'batch_size': 4,
        'seed': 1,
        'lr': 0.01,
        'force_loss_ratio': 1.0
    }
    grace_api(run_type='FINETUNE', config=finetune_config)

    os.chdir("../..")  # Go back to main grace directory
    os.makedirs("grace/RECALC", exist_ok=True)
    os.chdir("grace/RECALC")
    
    print("----------------------------")
    print("Running RECALC example")
    recalc_config = {
        'project_name': '4koh_92h2o_recalc',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'GRACE-1L-OMAT',
        'simulation_environment': 'ase'
    }
    grace_api(run_type='RECALC', config=recalc_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("Grace API examples completed")

if __name__ == "__main__":
    main()