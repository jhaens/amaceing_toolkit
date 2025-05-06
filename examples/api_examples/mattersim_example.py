#!/usr/bin/env python3
"""
Example script demonstrating how to use the MatterSim API from amaceing_toolkit.
This script replicates the functionality in the mattersim_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import mattersim_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("mattersim/MD", exist_ok=True)
    os.chdir("mattersim/MD")
    
    print("----------------------------")
    print("Running MD example")
    md_config = {
        'project_name': 'system_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'foundation_model': 'large',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ase_traj': 'y'
    }
    mattersim_api(run_type='MD', config=md_config)
    
    os.chdir("../..")  # Go back to main mattersim directory
    os.makedirs("mattersim/MULTI_MD", exist_ok=True)
    os.chdir("mattersim/MULTI_MD")
    
    print("----------------------------")
    print("Running MULTI_MD example")
    multi_md_config = {
        'project_name': 'system_multimd',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'foundation_model': ['small', 'large'],  # Pass as Python list
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ase_traj': 'y'
    }
    mattersim_api(run_type='MULTI_MD', config=multi_md_config)
    
    os.chdir("../..")  # Go back to main mattersim directory
    os.makedirs("mattersim/FINETUNE", exist_ok=True)
    os.chdir("mattersim/FINETUNE")
    
    print("----------------------------")
    print("Running FINETUNE example")
    finetune_config = {
        'project_name': 'system_ft',
        'train_data_path': '../../../4KOH_92H2O_333K/data/train_file_ms.xyz',
        'device': 'cuda',
        'force_loss_ratio': 100.0,
        'load_model_path': 'small',
        'batch_size': 5,
        'save_checkpoint': 'y',
        'ckpt_interval': 25,
        'epochs': 2,
        'seed': 1,
        'lr': 0.01,
        'save_path': 'MatterSim_models',
        'early_stopping': 'n'
    }
    mattersim_api(run_type='FINETUNE', config=finetune_config)
    
    os.chdir("../..")  # Go back to main mattersim directory
    os.makedirs("mattersim/RECALC", exist_ok=True)
    os.chdir("mattersim/RECALC")
    
    print("----------------------------")
    print("Running RECALC example")
    recalc_config = {
        'project_name': 'system_recalc',
        'coord_file': '../../../4KOH_92H2O_333K/data/dft_energies.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'foundation_model': 'large'
    }
    mattersim_api(run_type='RECALC', config=recalc_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("MatterSim API examples completed")

if __name__ == "__main__":
    main()