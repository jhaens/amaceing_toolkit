#!/usr/bin/env python3
"""
Example script demonstrating how to use the MACE API from amaceing_toolkit.
This script replicates the functionality in the mace_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import mace_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("mace/GEO_OPT", exist_ok=True)
    os.chdir("mace/GEO_OPT")
    
    print("----------------------------")
    print("Running GEO_OPT example")
    # Use Python dictionaries instead of string representation
    geo_opt_config = {
        'project_name': 'system_geoopt',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],  # List directly, API handles formatting
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n',
        'max_iter': 10,
        'simulation_environment': 'ase'
    }
    mace_api(run_type='GEO_OPT', config=geo_opt_config)
    
    os.chdir("../..")  # Go back to main mace directory
    os.makedirs("mace/CELL_OPT", exist_ok=True)
    os.chdir("mace/CELL_OPT")
    
    print("----------------------------")
    print("Running CELL_OPT example")
    cell_opt_config = {
        'project_name': 'system_cellopt',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n',
        'max_iter': 10,
        'simulation_environment': 'ase'
    }
    mace_api(run_type='CELL_OPT', config=cell_opt_config)
    
    os.chdir("../..")  # Go back to main mace directory
    os.makedirs("mace/MD", exist_ok=True)
    os.chdir("mace/MD")
    
    print("----------------------------")
    print("Running MD example")
    md_config = {
        'project_name': 'system_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 20,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ext_traj': 'y',
        'simulation_environment': 'ase'
    }
    mace_api(run_type='MD', config=md_config)
    
    os.chdir("../..")  # Go back to main mace directory
    os.makedirs("mace/MULTI_MD", exist_ok=True)
    os.chdir("mace/MULTI_MD")
    
    print("----------------------------")
    print("Running MULTI_MD example")
    multi_md_config = {
        'project_name': 'system_multimd',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        # Lists can be passed directly as Python lists
        'foundation_model': ['mace_mp', 'mace_mp', 'mace_off'],
        'model_size': ['small', 'medium', 'small'],
        'dispersion_via_ase': ['n', 'n', 'n'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 1,
        'timestep': 0.5,
        'log_interval': 1,
        'print_ext_traj': 'y',
        'simulation_environment': 'ase'
    }
    mace_api(run_type='MULTI_MD', config=multi_md_config)
    
    os.chdir("../..")  # Go back to main mace directory
    os.makedirs("mace/FINETUNE", exist_ok=True)
    os.chdir("mace/FINETUNE")
    
    print("----------------------------")
    print("Running FINETUNE example")
    finetune_config = {
        'project_name': 'system_ft',
        'train_file': '../../../4KOH_92H2O_333K/data/train_file.xyz',
        'device': 'cuda',
        'stress_weight': 0.0,
        'forces_weight': 10.0,
        'energy_weight': 0.1,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'batch_size': 5,
        'prevent_catastrophic_forgetting': 'n',
        'valid_fraction': 0.1,
        'valid_batch_size': 2,
        'max_num_epochs': 2,
        'seed': 1,
        'lr': 0.01,
        'dir': 'MACE_models',
        'xc_functional_of_dataset': 'BLYP'
    }
    mace_api(run_type='FINETUNE', config=finetune_config)
    
    os.chdir("../..")  # Go back to main mace directory
    os.makedirs("mace/FINETUNE_MULTIHEAD", exist_ok=True)
    os.chdir("mace/FINETUNE_MULTIHEAD")
    
    print("----------------------------")
    print("Running FINETUNE_MULTIHEAD example")
    multihead_config = {
        'project_name': 'system_mhft',
        'train_file': ['../../../4KOH_92H2O_333K/data/train_file.xyz', '../../../4KOH_92H2O_333K/data/train_file2.xyz'],
        'device': 'cuda',
        'stress_weight': 0.0,
        'forces_weight': 10.0,
        'energy_weight': 0.1,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'batch_size': 5,
        'valid_fraction': 0.1,
        'valid_batch_size': 2,
        'max_num_epochs': 2,
        'seed': 1,
        'lr': 0.01,
        'xc_functional_of_dataset': ['BLYP', 'BLYP'],
        'dir': 'MACE_models'
    }
    mace_api(run_type='FINETUNE_MULTIHEAD', config=multihead_config)
    
    os.chdir("../..")  # Go back to main mace directory
    os.makedirs("mace/RECALC", exist_ok=True)
    os.chdir("mace/RECALC")
    
    print("----------------------------")
    print("Running RECALC example")
    recalc_config = {
        'project_name': 'system_recalc',
        'coord_file': '../../../4KOH_92H2O_333K/data/dft_energies.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n',
        'simulation_environment': 'ase'
    }
    mace_api(run_type='RECALC', config=recalc_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("MACE API examples completed")

if __name__ == "__main__":
    main()