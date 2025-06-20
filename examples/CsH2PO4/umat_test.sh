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
amaceing_uma --run_type="MD" --config="{'project_name': 'csh2po4_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': 'omol', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ase_traj': 'y'}" 
cd ..
echo ----------------------------
echo Testing input file generation: MULTI_MD
mkdir -p MULTI_MD
cd MULTI_MD
amaceing_uma --run_type="MULTI_MD" --config="{'project_name': 'csh2po4_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': '['omat', 'omol']', 'temperature': '300', 'pressure': '1.0', 'thermostat': 'Langevin', 'nsteps': 10, 'write_interval': 10, 'timestep': 0.5, 'log_interval': 10, 'print_ase_traj': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: RECALC
mkdir -p RECALC
cd RECALC
amaceing_uma --run_type="RECALC" --config="{'project_name': 'csh2po4_recalc', 'coord_file': '../../data/system.xyz', 'pbc_list': '[19.8196 0 0 0 19.8196 0 0 0 19.8196]', 'foundation_model': 'omat'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_uma done
echo ============================

