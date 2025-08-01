#!/usr/bin/env python3
"""
Example script demonstrating how to use the CP2K API from amaceing_toolkit.
This script replicates the functionality in the cp2k_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import cp2k_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("cp2k/GEO_OPT", exist_ok=True)
    os.chdir("cp2k/GEO_OPT")
    
    print("----------------------------")
    print("Running GEO_OPT example")
    geo_opt_config = {
        'project_name': 'system_geoopt',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],  # List directly, API handles formatting
        'max_iter': 10,
        'xc_functional': 'BLYP',
        'print_forces': 'OFF',
        'cp2k_newer_than_2023x': 'y'
    }
    cp2k_api(run_type='GEO_OPT', config=geo_opt_config)
    
    os.chdir("../..")  # Go back to main cp2k directory
    os.makedirs("cp2k/CELL_OPT", exist_ok=True)
    os.chdir("cp2k/CELL_OPT")
    
    print("----------------------------")
    print("Running CELL_OPT example")
    cell_opt_config = {
        'project_name': 'system_cellopt',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'max_iter': 10,
        'keep_symmetry': 'OFF',
        'symmetry': 'CUBIC',
        'xc_functional': 'BLYP',
        'cp2k_newer_than_2023x': 'y'
    }
    cp2k_api(run_type='CELL_OPT', config=cell_opt_config)
    
    os.chdir("../..")  # Go back to main cp2k directory
    os.makedirs("cp2k/MD", exist_ok=True)
    os.chdir("cp2k/MD")
    
    print("----------------------------")
    print("Running MD example")
    md_config = {
        'project_name': 'system_md',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'ensemble': 'NVT',
        'nsteps': 10,
        'timestep': 0.5,
        'temperature': 300,
        'print_forces': 'ON',
        'print_velocities': 'OFF',
        'xc_functional': 'BLYP',
        'equilibration_run': 'y',
        'equilibration_steps': 5,
        'pressure_b': 1.0,
        'cp2k_newer_than_2023x': 'y'
    }
    cp2k_api(run_type='MD', config=md_config)
    
    os.chdir("../..")  # Go back to main cp2k directory
    os.makedirs("cp2k/REFTRAJ", exist_ok=True)
    os.chdir("cp2k/REFTRAJ")
    
    print("----------------------------")
    print("Running REFTRAJ example")
    reftraj_config = {
        'project_name': 'system_reftraj',
        'ref_traj': '../../../4KOH_92H2O_333K/data/ref_trajectory.xyz',
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'nsteps': 10,
        'stride': 1,
        'print_forces': 'ON',
        'print_velocities': 'OFF',
        'xc_functional': 'BLYP',
        'cp2k_newer_than_2023x': 'y'
    }
    cp2k_api(run_type='REFTRAJ', config=reftraj_config)

    os.chdir("../..")  # Go back to main cp2k directory
    os.makedirs("cp2k/ENERGY", exist_ok=True)
    os.chdir("cp2k/ENERGY")
    
    print("----------------------------")
    print("Running ENERGY example")
    # Create a sample coord.xyz file to work with
    with open('coord.xyz', 'w') as f:
        # Copy content from system.xyz
        with open('../../../4KOH_92H2O_333K/data/system.xyz', 'r') as src:
            f.write(src.read())
            
    energy_config = {
        'project_name': 'system_energy',
        'coord_file': 'coord.xyz',  # Uses the local copy we just created
        'pbc_list': [14.2067, 0, 0, 0, 14.2067, 0, 0, 0, 14.2067],
        'xc_functional': 'BLYP',
        'cp2k_newer_than_2023x': 'y'
    }
    cp2k_api(run_type='ENERGY', config=energy_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("CP2K API examples completed")

if __name__ == "__main__":
    main()