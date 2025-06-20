#!/bin/bash
echo ============================
echo Testing amaceing_sevennet
echo ============================
mkdir -p mattersim
cd mattersim
echo ----------------------------
echo Testing input file generation: MD 
mkdir -p MD
cd MD
amaceing_sevennet --run_type="MD" --config="{'project_name': 'csh2po4_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': '7net-mf-ompa', 'modal': 'mpa', 'dispersion_via_simenv': 'n', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y'}" 
cd ..
echo ----------------------------
echo Testing input file generation: MULTI_MD
mkdir -p MULTI_MD
cd MULTI_MD
amaceing_sevennet --run_type="MULTI_MD" --config="{'project_name': 'csh2po4_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': '['7net-0' '7net-mf-ompa']', 'dispersion_via_simenv': '['n' 'n']', 'modal': '['' 'mpa']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: FINETUNE
mkdir -p FINETUNE
cd FINETUNE
amaceing_sevennet --run_type="FINETUNE" --config="{'project_name': 'csh2po4_finetune', 'train_data_path': '../../data/train_file_7net.xyz', 'foundation_model': '7net-0', 'epochs': 2, 'batch_size': 4, 'seed': 1, 'lr': 0.01}"
cd ..
echo ----------------------------
echo Testing input file generation: RECALC
mkdir -p RECALC
cd RECALC
amaceing_sevennet --run_type="RECALC" --config="{'project_name': 'csh2po4_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': '7net-mf-ompa', 'modal': 'mpa', 'dispersion_via_simenv': 'n'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_sevennet done
echo ============================

