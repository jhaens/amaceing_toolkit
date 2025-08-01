#!/bin/bash
echo ============================
echo Testing amaceing_grace
echo ============================
mkdir -p sevennet
cd sevennet
echo ----------------------------
echo Testing input file generation: MD 
mkdir -p MD
cd MD
amaceing_grace --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'GRACE-1L-OMAT', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y', 'simulation_environment': 'ase'}" 
cd ..
echo ----------------------------
echo Testing input file generation: MULTI_MD
mkdir -p MULTI_MD
cd MULTI_MD
amaceing_grace --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['GRACE-1L-OMAT' 'GRACE-1L-OAM']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ext_traj': 'y', 'simulation_environment': 'ase'}"
cd ..
echo ----------------------------
echo Testing input file generation: FINETUNE
mkdir -p FINETUNE
cd FINETUNE
amaceing_grace --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'train_file': '../../data/train_file_7net.xyz', 'foundation_model': 'GRACE-1L-OAM', 'epochs': 2, 'batch_size': 4, 'seed': 1, 'lr': 0.01, 'force_loss_ratio': 1.0}"
cd ..
echo ----------------------------
echo Testing input file generation: RECALC
mkdir -p RECALC
cd RECALC
amaceing_grace --run_type="RECALC" --config="{'project_name': '4koh_92h2o_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'GRACE-1L-OMAT', 'simulation_environment': 'ase'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_grace done
echo ============================