#!/usr/bin/env python3
"""
Example script demonstrating how to use the UMA API from amaceing_toolkit.
This script replicates the functionality in the uma_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import uma_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("uma/MD", exist_ok=True)
    os.chdir("uma/MD")
    
    print("----------------------------")
    print("Running MD example")
    md_config = {
        'project_name': 'system_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'omol',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ase_traj': 'y'
    }
    uma_api(run_type='MD', config=md_config)
    
    os.chdir("../..")  # Go back to main uma directory
    os.makedirs("uma/MULTI_MD", exist_ok=True)
    os.chdir("uma/MULTI_MD")
    
    print("----------------------------")
    print("Running MULTI_MD example")
    multi_md_config = {
        'project_name': 'system_multimd',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': ['omol', 'omat'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 10,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 10,
        'print_ase_traj': 'y'
    }
    uma_api(run_type='MULTI_MD', config=multi_md_config)
    
    os.chdir("../..")  # Go back to main uma directory
    os.makedirs("uma/RECALC", exist_ok=True)
    os.chdir("uma/RECALC")
    
    print("----------------------------")
    print("Running RECALC example")
    recalc_config = {
        'project_name': 'system_recalc',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'foundation_model': 'omol'
    }
    uma_api(run_type='RECALC', config=recalc_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("UMA API examples completed")

if __name__ == "__main__":
    main()