#!/bin/bash
echo ============================
echo Testing amaceing_mace
echo ============================
mkdir -p mace
cd mace
echo ----------------------------
echo Testing input file generation: GEO_OPT
mkdir -p GEO_OPT
cd GEO_OPT
amaceing_mace --run_type="GEO_OPT" --config="{'project_name': '4koh_92h2o_geoopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_mace': 'n', 'max_iter': '10'}"
cd ..
echo ----------------------------
echo Testing input file generation: CELL_OPT
mkdir -p CELL_OPT
cd CELL_OPT
amaceing_mace --run_type="CELL_OPT" --config="{'project_name': '4koh_92h2o_geoopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_mace': 'n', 'max_iter': '10'}"
cd ..
echo ----------------------------
echo Testing input file generation: MD
mkdir -p MD
cd MD
amaceing_mace --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_mace': 'n', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '20', 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ase_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: MULTI-MD
mkdir -p MULTI_MD
cd MULTI_MD
amaceing_mace --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_multimd', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'foundation_model': '['mace_mp' 'mace_mp' 'mace_off']', 'model_size': '['small' 'medium' 'small']', 'dispersion_via_mace': '['n' 'n' 'n']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': '10', 'write_interval': '1', 'timestep': 0.5, 'log_interval': '1', 'print_ase_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: FINETUNE
mkdir -p FINETUNE
cd FINETUNE
amaceing_mace --run_type="FINETUNE" --config="{'project_name': '4koh_92h2o_ft', 'train_file': '../../data/train_file.xyz', 'device': 'cuda', 'stress_weight': 0.0, 'forces_weight': 10.0, 'energy_weight': 0.1, 'foundation_model': 'mace_mp', 'model_size': 'small', 'batch_size': 5, 'prevent_catastrophic_forgetting': 'n', 'valid_fraction': 0.1, 'valid_batch_size': 2, 'max_num_epochs': '2', 'seed': 1, 'lr': 0.01, 'dir': 'MACE_models', 'xc_functional_of_dataset' : 'BLYP'}"
cd ..
echo ----------------------------
echo Testing input file generation: FINETUNE_MULTIHEAD
mkdir -p FINETUNE_MULTIHEAD
cd FINETUNE_MULTIHEAD
amaceing_mace --run_type="FINETUNE_MULTIHEAD" --config="{'project_name': '4koh_92h2o_mhft', 'train_file': '['../../data/train_file.xyz' '../../data/train_file2.xyz']', 'device': 'cuda', 'stress_weight': 0.0, 'forces_weight': 10.0, 'energy_weight': 0.1, 'foundation_model': 'mace_mp', 'model_size': 'small', 'batch_size': 5, 'valid_fraction': 0.1, 'valid_batch_size': 2, 'max_num_epochs': 2, 'seed': 1, 'lr': 0.01, 'xc_functional_of_dataset': '['BLYP' 'BLYP']', 'dir': 'MACE_models'}"
cd ..
echo ----------------------------
echo Testing input file generation: RECALC
mkdir -p RECALC
cd RECALC
amaceing_mace --run_type="RECALC" --config="{'project_name': '25koh_50h2o', 'coord_file': '../../data/dft_energies.xyz', 'pbc_list': '[14.2067 14.2067 14.2067]', 'foundation_model': 'mace_mp', 'model_size': 'small', 'dispersion_via_mace': 'n'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_mace done
echo ============================
