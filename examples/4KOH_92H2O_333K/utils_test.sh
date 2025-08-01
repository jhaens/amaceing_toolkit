#!/bin/bash
echo ============================
echo Testing amaceing_utils
echo ============================
mkdir -p utils
cd utils
echo ----------------------------
echo Testing utils function: EVAL_ERROR 
mkdir -p EVAL_ERROR
cd EVAL_ERROR
amaceing_utils --run_type="EVAL_ERROR" --config="{'ener_filename_ground_truth': '../../data/dft_energies.xyz', 'force_filename_ground_truth': '../../data/dft_forces.xyz', 'ener_filename_compare': '../../data/mace_energies.txt', 'force_filename_compare': '../../data/mace_forces.xyz'}"
cd ..
echo ----------------------------
echo Testing utils function: PREPARE_EVAL_ERROR 
mkdir -p PREPARE_EVAL_ERROR
cd PREPARE_EVAL_ERROR
amaceing_utils --run_type="PREPARE_EVAL_ERROR" --config="{'traj_file': '../../data/trajectory.traj', 'each_nth_frame': '1', 'start_cp2k': 'y', 'log_file': '../../data/mace_input.log', 'xc_functional': 'BLYP'}"
cd ..
echo ----------------------------
echo Testing utils function: EXTRACT_XYZ
mkdir -p EXTRACT_XYZ
cd EXTRACT_XYZ
amaceing_utils --run_type="EXTRACT_XYZ" --config="{'coord_file': '../../data/ref_trajectory.xyz', 'each_nth_frame': '2'}"
cd ..
echo ----------------------------
echo Testing utils function: CITATIONS
mkdir -p CITIATIONS
cd CITIATIONS
amaceing_utils --run_type="CITATIONS" --config="{'log_file': '../../data/mace_input.log'}"
cd ..
echo ----------------------------
echo Testing utils function: BENCHMARK1
mkdir -p BENCHMARK_MD
cd BENCHMARK_MD
amaceing_utils --run_type="BENCHMARK" --config="{'mode': 'MD', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'force_nsteps': '10', 'mace_model': '['mace_mp' 'small']', 'mattersim_model': 'large', 'sevennet_model': '['7net-mf-ompa' 'mpa']', 'orb_model': '['orb_v3_conservative_inf' 'omat']'}"
cd ..
echo ----------------------------
echo Testing utils function: BENCHMARK2
mkdir -p BENCHMARK_RECALC
cd BENCHMARK_RECALC
amaceing_utils --run_type="BENCHMARK" --config="{'mode': 'RECALC', 'coord_file': '../../data/dft_energies.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'force_nsteps': '../../data/dft_forces.xyz', 'mace_model': '['mace_mp' 'small']', 'mattersim_model': 'large', 'sevennet_model': '['7net-mf-ompa' 'mpa']', 'orb_model': '['orb_v3_conservative_inf' 'omat']'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_utils done
echo ============================
