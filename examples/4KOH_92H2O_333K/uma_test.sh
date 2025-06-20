#!/bin/bash
echo ============================
echo Testing amaceing_uma
echo ============================
mkdir -p uma
cd uma
echo ----------------------------
echo Testing input file generation: MD 
mkdir -p MD
cd MD
amaceing_uma --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': 'omol', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ase_traj': 'y'}" 
cd ..
echo ----------------------------
echo Testing input file generation: MULTI_MD
mkdir -p MULTI_MD
cd MULTI_MD
amaceing_uma --run_type="MULTI_MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'foundation_model': '['omol' 'omat']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ase_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: RECALC
mkdir -p RECALC
cd RECALC
amaceing_uma --run_type="RECALC" --config="{'project_name': '4koh_92h2o_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067', 'foundation_model': 'omol'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_uma done
echo ============================

