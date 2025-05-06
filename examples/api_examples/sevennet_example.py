#!/usr/bin/env python3
"""
Example script demonstrating how to use the SevenNet API from amaceing_toolkit.
This script replicates the functionality in the sevennet_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import sevennet_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("sevennet/MD", exist_ok=True)
    os.chdir("sevennet/MD")
    
    print("----------------------------")
    print("Running MD example")
    md_config = {
        'project_name': 'system_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'foundation_model': '7net-mf-ompa',
        'modal': 'mpa',
        'dispersion_via_ase': 'n',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ase_traj': 'y'
    }
    sevennet_api(run_type='MD', config=md_config)
    
    os.chdir("../..")  # Go back to main sevennet directory
    os.makedirs("sevennet/MULTI_MD", exist_ok=True)
    os.chdir("sevennet/MULTI_MD")
    
    print("----------------------------")
    print("Running MULTI_MD example")
    multi_md_config = {
        'project_name': 'system_multimd',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'foundation_model': ['7net-0', '7net-mf-ompa'],
        'dispersion_via_ase': ['n', 'n'],
        'modal': ['', 'mpa'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ase_traj': 'y'
    }
    sevennet_api(run_type='MULTI_MD', config=multi_md_config)
    
    os.chdir("../..")  # Go back to main sevennet directory
    os.makedirs("sevennet/FINETUNE", exist_ok=True)
    os.chdir("sevennet/FINETUNE")
    
    print("----------------------------")
    print("Running FINETUNE example")
    finetune_config = {
        'project_name': 'system_finetune',
        'train_data_path': '../../../4KOH_92H2O_333K/data/train_file_7net.xyz',
        'foundation_model': '7net-0',
        'epochs': 2,
        'batch_size': 4,
        'seed': 1,
        'lr': 0.01
    }
    sevennet_api(run_type='FINETUNE', config=finetune_config)
    
    os.chdir("../..")  # Go back to main sevennet directory
    os.makedirs("sevennet/RECALC", exist_ok=True)
    os.chdir("sevennet/RECALC")
    
    print("----------------------------")
    print("Running RECALC example")
    recalc_config = {
        'project_name': 'system_recalc',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'foundation_model': '7net-mf-ompa',
        'modal': 'mpa',
        'dispersion_via_ase': 'n'
    }
    sevennet_api(run_type='RECALC', config=recalc_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("SevenNet API examples completed")

if __name__ == "__main__":
    main()