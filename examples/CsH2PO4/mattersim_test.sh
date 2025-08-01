#!/bin/bash
echo ============================
echo Testing amaceing_mattersim
echo ============================
mkdir -p mattersim
cd mattersim
echo ----------------------------
echo Testing input file generation: MD 
mkdir -p MD
cd MD
amaceing_mattersim --run_type="MD" --config="{'project_name': 'csh2po4_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': 'large', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '10', 'write_interval': 10, 'timestep': 0.5, 'log_interval': 100, 'print_ext_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: MULTI_MD
mkdir -p MULTI_MD
cd MULTI_MD
amaceing_mattersim --run_type="MULTI_MD" --config="{'project_name': 'csh2po4_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': '['small' 'large']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '10', 'write_interval': 10, 'timestep': 0.5, 'log_interval': 100, 'print_ext_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: FINETUNE
mkdir -p FINETUNE
cd FINETUNE
amaceing_mattersim --run_type="FINETUNE" --config="{'project_name': 'csh2po4_ft', 'train_file': '../../data/train_file_ms.xyz', 'device': 'cuda', 'force_loss_ratio': 100.0, 'foundation_model': 'small', 'batch_size': 5, 'save_checkpoint': 'y', 'ckpt_interval': 25, 'epochs': 2, 'seed': 1, 'lr': 0.01, 'save_path': 'MatterSim_models', 'early_stopping': 'n'}"
cd ..
echo ----------------------------
echo Testing input file generation: RECALC
mkdir -p RECALC
cd RECALC
amaceing_mattersim --run_type="RECALC" --config="{'project_name': 'csh2po4_recalc', 'coord_file': '../../data/dft_energies.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': 'large'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_mattersim done
echo ============================

