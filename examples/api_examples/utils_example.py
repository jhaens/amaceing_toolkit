#!/usr/bin/env python3
"""
Example script demonstrating how to use the Utils API from amaceing_toolkit.
This script replicates the functionality in the utils_test.sh example file.
"""
import os
from amaceing_toolkit.workflow import utils_api

def main():
    # Create directory structure similar to the bash scripts
    os.makedirs("utils/EVAL_ERROR", exist_ok=True)
    os.chdir("utils/EVAL_ERROR")
    
    print("----------------------------")
    print("Running EVAL_ERROR example")
    eval_error_config = {
        'ener_filename_ground_truth': '../../../4KOH_92H2O_333K/data/dft_energies.xyz',
        'force_filename_ground_truth': '../../../4KOH_92H2O_333K/data/dft_forces.xyz',
        'ener_filename_compare': '../../../4KOH_92H2O_333K/data/mace_energies.txt',
        'force_filename_compare': '../../../4KOH_92H2O_333K/data/mace_forces.xyz'
    }
    utils_api(run_type='EVAL_ERROR', config=eval_error_config)
    
    os.chdir("../..")  # Go back to main utils directory
    os.makedirs("utils/PREPARE_EVAL_ERROR", exist_ok=True)
    os.chdir("utils/PREPARE_EVAL_ERROR")
    
    print("----------------------------")
    print("Running PREPARE_EVAL_ERROR example")
    prepare_eval_config = {
        'traj_file': '../../../4KOH_92H2O_333K/data/trajectory.traj',
        'each_nth_frame': 1,
        'start_cp2k': 'y',
        'log_file': '../../../4KOH_92H2O_333K/data/mace_input.log',
        'xc_functional': 'BLYP'
    }
    utils_api(run_type='PREPARE_EVAL_ERROR', config=prepare_eval_config)
    
    os.chdir("../..")  # Go back to main utils directory
    os.makedirs("utils/EXTRACT_XYZ", exist_ok=True)
    os.chdir("utils/EXTRACT_XYZ")
    
    print("----------------------------")
    print("Running EXTRACT_XYZ example")
    extract_xyz_config = {
        'coord_file': '../../../4KOH_92H2O_333K/data/ref_trajectory.xyz',
        'each_nth_frame': 2
    }
    utils_api(run_type='EXTRACT_XYZ', config=extract_xyz_config)
    
    os.chdir("../..")  # Go back to main utils directory
    os.makedirs("utils/MACE_CITATIONS", exist_ok=True)
    os.chdir("utils/MACE_CITATIONS")
    
    print("----------------------------")
    print("Running MACE_CITATIONS example")
    mace_citations_config = {
        'log_file': '../../../4KOH_92H2O_333K/data/mace_input.log'
    }
    utils_api(run_type='MACE_CITATIONS', config=mace_citations_config)
    
    os.chdir("../..")  # Go back to main utils directory
    os.makedirs("utils/BENCHMARK", exist_ok=True)
    os.chdir("utils/BENCHMARK")
    
    print("----------------------------")
    print("Running BENCHMARK MD example")
    benchmark_md_config = {
        'mode': 'MD',
        'coord_file': '../../../4KOH_92H2O_333K/data/system.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'force_nsteps': 10,
        'mace_model': ['mace_mp', 'small'],
        'mattersim_model': 'large',
        'sevennet_model': ['7net-mf-ompa', 'mpa']
    }
    utils_api(run_type='BENCHMARK', config=benchmark_md_config)
    
    os.chdir("../..")  # Go back to main utils directory
    os.makedirs("utils/BENCHMARK_RECALC", exist_ok=True)
    os.chdir("utils/BENCHMARK_RECALC")
    
    print("----------------------------")
    print("Running BENCHMARK RECALC example")
    benchmark_recalc_config = {
        'mode': 'RECALC',
        'coord_file': '../../../4KOH_92H2O_333K/data/dft_energies.xyz',
        'pbc_list': [19.8196, 19.8196, 19.8196],
        'force_nsteps': '../../../4KOH_92H2O_333K/data/dft_forces.xyz',  # In RECALC mode, this is a file path
        'mace_model': ['mace_mp', 'small'],
        'mattersim_model': 'large',
        'sevennet_model': ['7net-mf-ompa', 'mpa']
    }
    utils_api(run_type='BENCHMARK', config=benchmark_recalc_config)
    
    os.chdir("../..")  # Go back to root directory
    print("----------------------------")
    print("Utils API examples completed")

if __name__ == "__main__":
    main()