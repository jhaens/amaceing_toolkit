#!/bin/bash
echo ============================
echo Testing amaceing_orb
echo ============================
mkdir -p sevennet
cd sevennet
echo ----------------------------
echo Testing input file generation: MD 
mkdir -p MD
cd MD
amaceing_orb --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'orb_v3_conservative_inf', 'modal': 'omat', 'dispersion_via_simenv': 'n', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y'}" 
cd ..
echo ----------------------------
echo Testing input file generation: MULTI_MD
mkdir -p MULTI_MD
cd MULTI_MD
amaceing_orb --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['orb_v2' 'orb_v3_conservative_inf']', 'dispersion_via_simenv': '['n' 'n']', 'modal': '['' 'omat']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: FINETUNE
mkdir -p FINETUNE
cd FINETUNE
amaceing_orb --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'train_file': '../../data/train_file_7net.xyz', 'foundation_model': 'orb_v2', 'epochs': 2, 'batch_size': 4, 'seed': 1, 'lr': 0.0003, 'force_loss_ratio': 1.0}"
cd ..
echo ----------------------------
echo Testing input file generation: RECALC
mkdir -p RECALC
cd RECALC
amaceing_orb --run_type="RECALC" --config="{'project_name': '4koh_92h2o_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'orb_v3_conservative_inf', 'modal': 'omat', 'dispersion_via_simenv': 'n'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_orb done
echo ============================

