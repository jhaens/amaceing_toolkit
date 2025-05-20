#!/bin/bash
echo ============================
echo Testing amaceing_cp2k
echo ============================
mkdir -p cp2k
cd cp2k
echo ----------------------------
echo Testing input file generation: GEO_OPT
mkdir -p GEO_OPT
cd GEO_OPT
amaceing_cp2k --run_type="GEO_OPT" --config="{'project_name': '4koh_92h2o_geoopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.20670 0 0 0 14.2067 0 0 0 14.2067]', 'max_iter': 10, 'xc_functional': 'BLYP', 'print_forces': 'OFF', 'cp2k_newer_than_2023x': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: CELL_OPT
mkdir -p CELL_OPT
cd CELL_OPT
amaceing_cp2k --run_type="CELL_OPT" --config="{'project_name': '4koh_92h2o_cellopt', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'max_iter': '10', 'keep_symmetry': 'OFF', 'symmetry': 'CUBIC', 'xc_functional': 'BLYP', 'cp2k_newer_than_2023x': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: MD
mkdir -p MD
cd MD
amaceing_cp2k --run_type="MD" --config="{'project_name': '4koh_92h2o_md', 'coord_file': '../../data/system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'ensemble': 'NVT', 'nsteps': '10', 'timestep': 0.5, 'temperature': 300, 'print_forces': 'ON', 'print_velocities': 'OFF', 'xc_functional': 'BLYP', 'equilibration_run': 'y', 'equilibration_steps': '5', 'pressure_b': 1.0, 'cp2k_newer_than_2023x': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: REFTRAJ
mkdir -p REFTRAJ
cd REFTRAJ
amaceing_cp2k --run_type="REFTRAJ" --config="{'project_name': '4koh_92h2o_reftraj', 'ref_traj': '../../data/ref_trajectory.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'nsteps': '10', 'stride': '1', 'print_forces': 'ON', 'print_velocities': 'OFF', 'xc_functional': 'BLYP', 'cp2k_newer_than_2023x': 'y'}"
cd ..
echo ----------------------------
echo Testing input file generation: ENERGY
mkdir -p ENERGY
cd ENERGY
amaceing_cp2k --run_type="ENERGY" --config="{'project_name': '4koh_92h2o_energy', 'coord_file': 'system.xyz', 'pbc_list': '[14.2067 0 0 0 14.2067 0 0 0 14.2067]', 'xc_functional': 'BLYP', 'cp2k_newer_than_2023x': 'y'}"
cd ..
echo ----------------------------
echo ============================
echo Testing amaceing_cp2k done
echo ============================