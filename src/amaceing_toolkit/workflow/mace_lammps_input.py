import os
import numpy as np
import datetime
import sys
import argparse, textwrap
import mace
from ase.io import read, write
from ase import Atoms
from ase.io.trajectory import Trajectory
from amaceing_toolkit.default_configs import lammps_runscript

from .utils import ask_for_yes_no
import subprocess

def get_element_list(coord_file, list_only=False):
    """
    Function to extract the list of elements from a coordinate file.
    """
    elements_ordered = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
                         "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
                         "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe",
                         "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se",
                         "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo",
                         "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
                         "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce",
                         "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
                         "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W",
                         "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb",
                         "Bi", "Po", "At", "Rn"]

    atoms = read(coord_file, format='xyz')
    elements = atoms.get_chemical_symbols()
    unique_elements = [el for el in elements_ordered if el in elements]
    if list_only:
        return unique_elements
    else:
        return ' '.join(unique_elements)

def print_ext_traj_lines(config_dict, element_list):
    """
    Function to generate the lines for printing extended trajectory information.
    """
    if config_dict['print_ext_traj'] == 'y':
        return f"""
dump          d_prod_frc all custom {config_dict['write_interval']} md_frc.lammpstrj type fx fy fz
dump_modify   d_prod_frc sort id""", """
undump        d_prod_frc"""
    else:
        return "", ""
    
    

def lammps_input_writer (
    config_dict,
    run_type
):
    """
    Function to write LAMMPS input files based on the provided configuration.
    
    Parameters:
        config_dict (dict): Configuration dictionary containing settings for LAMMPS input.
        run_type (str): Type of run (e.g., 'MD', 'GEO_OPT', etc.).
    
        
    """
    # project_name = input("What is the name of the project?: ")
    # if project_name == '':
    #     project_name = f'{run_type}_{datetime.datetime.now().strftime("%Y%m%d")}'
    # config_dict['project_name'] = project_name
    
    # Create the first part of the input file
    input_file_content = f"""# --------- Units and System Setup ---------
units         metal
atom_style    atomic
atom_modify   map yes
newton        on
boundary      p p p
variable      p equal press
variable      v equal vol 
variable      pot_e equal pe"""
    
    
    # Load the coordinates file
    #if run_type != "RECALC":
    if config_dict['coord_file'].endswith('.xyz'):
        # Convert the xyz file to a LAMMPS data file
        atoms = read(config_dict['coord_file'], format='xyz', index="0")
        atoms.set_cell(config_dict['pbc_list'])
        atoms.set_pbc([True, True, True])
        write(config_dict['coord_file'].replace('.xyz', '.data'), atoms, units="metal", masses=True, specorder=get_element_list(config_dict['coord_file'], list_only=True), format="lammps-data", atom_style="atomic")
        input_file_content += f"\nread_data     {config_dict['coord_file'].replace('.xyz', '.data')}\n"
    else:
        input_file_content += f"\nread_data     {config_dict['coord_file']}\n"

    # Get the element list from the coordinates/trajectory file
    element_list = get_element_list(config_dict['coord_file'])

    # Convert the Mace model to LAMMPS format
    if config_dict['foundation_model'].endswith('.pt'):
        model_file = config_dict['foundation_model']
    else:
        converter_script_path = mace.__file__.replace('__init__.py', 'cli/create_lammps_model.py')
        if config_dict['foundation_model'].endswith('.model'):
            # Convert the custom model file to LAMMPS format
            convert_command = f"python {converter_script_path} {config_dict['foundation_model']}"
            print(f"Converting model {config_dict['foundation_model']} to LAMMPS format...")
            try:
                subprocess.run(convert_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"Error: Model conversion failed with exit code {e.returncode}")
            model_file = f"{config_dict['foundation_model']}-lammps.pt"
        else:
            # No custom model file provided, download the default model and convert it
            download_model_dict = {'mp_small': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2023-12-10-mace-128-L0_energy_epoch-249.model',
                                   'mp_medium': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2023-12-03-mace-128-L1_epoch-199.model',
                                   'mp_large': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2024-01-07-mace-128-L2_epoch-199.model',
                                   'mpa_medium': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mpa_0/mace-mpa-0-medium.model',
                                   'off_small': 'https://github.com/ACEsuit/mace-off/blob/main/mace_off23/MACE-OFF23_small.model',
                                   'off_medium': 'https://github.com/ACEsuit/mace-off/blob/main/mace_off23/MACE-OFF23_medium.model',
                                   'off_large': 'https://github.com/ACEsuit/mace-off/blob/main/mace_off23/MACE-OFF23_large.model'}

            # Build key string for the model
            dataset_key = config_dict['foundation_model'].split('_')[-1]
            size_key = config_dict['model_size']

            if size_key == 'medium-mpa-0': 
                model_key = 'mpa_medium'
            else:
                model_key = f"{dataset_key}_{size_key}"
            if model_key not in download_model_dict:
                raise ValueError(f"Model {model_key} not found in the download dictionary. Please check the model name or add it to the dictionary.")
            model_url = download_model_dict[model_key]
            # Download the model file
            print(f"Downloading model {model_key} from {model_url}...")
            model_file = f"{model_key}.model"
            if not os.path.exists(model_file):
                os.system(f"wget {model_url} -O {model_file}")
            # Convert the downloaded model file to LAMMPS format
            convert_command = f"python {converter_script_path} {model_file}"
            print(f"Converting model {model_file} to LAMMPS format...")
            os.system(convert_command)
            model_file = f"{model_file}-lammps.pt"


    

    # Setup the Mace Potential settings
    input_file_content += f"""# --------- Potential Setup ---------
pair_style    mace no_domain_decomposition
pair_coeff    * * {model_file} {element_list}
"""


    if run_type == "GEO_OPT":

        # Insert code for geometry optimization
        input_file_content += f"""# --------- Neighbors ---------
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes

# --------- Minimization ---------
thermo        1
dump          d_go all xyz 1 geoopt_traj.xyz
dump_modify   d_go element {element_list} sort id
fix           log_energy all print {config_dict['write_interval']} """+r""" "${pot_e}" file energies.txt screen no title "" """+f"""
minimize      1.0e-5 1.0e-7 {int(config_dict['max_iter'])} {10*int(config_dict['max_iter'])}
undump	      d_go
unfix         log_energy

write_dump all xyz {config_dict['project_name']}_geoopt.xyz modify sort id element {element_list}"""


    elif run_type == "CELL_OPT":
        # Check if PBC 3x3 matrix is non-orhtogonal: off diagonal elements are not zero
        pbc_matrix = np.array(config_dict['pbc_list']).reshape(3, 3)
        if np.any(np.abs(pbc_matrix - np.diag(np.diag(pbc_matrix))) > 1e-6):
            cellopt_fix = "cellopt all box/relax tri 0.0 vmax 0.001"
        else:
            keep_symmetry = ask_for_yes_no("Do you want to keep the symmetry of the cell? (y/n)", 'y')
            if keep_symmetry:
                cellopt_fix = "cellopt all box/relax iso 0.0 vmax 0.001"
            else:
                cellopt_fix = "cellopt all box/relax aniso 0.0 vmax 0.001"

        # Insert code for cell optimization
        input_file_content += f"""# --------- Neighbors ---------
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes

# --------- Minimization ---------
thermo        1
dump          d_co all xyz 1 cellopt_traj.xyz
dump_modify   d_co element {element_list} sort id
fix           log_energy all print {config_dict['write_interval']} """+r""" "${pot_e}" file energies.txt screen no title "" """+f"""
fix           {cellopt_fix}
minimize      1.0e-5 1.0e-7 {int(config_dict['max_iter'])} {10*int(config_dict['max_iter'])}
unfix         cellopt
unfix	      log_energy
undump	      d_co

write_dump all xyz {config_dict['project_name']}_cellopt.xyz modify sort id element {element_list}


print "avecx avecy avecz" file pbc_new screen no
print "bvecx bvecy bvecz" append pbc_new screen no
print "cvecx cvecy cvecz" append pbc_new screen no
"""

    
    elif run_type == "MD":
        timestep = float(config_dict['timestep']) * 0.001  # Convert fs to ps
        print_production = print_ext_traj_lines(config_dict, element_list)
        # Insert code for molecular dynamics
        input_file_content += f"""# --------- Timestep and Neighbors ---------
timestep      {timestep}     # ps
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes

# --------- Initial Velocity ---------
velocity      all create {config_dict['temperature']} 42 dist uniform rot yes mom yes

# --------- Equilibration ---------
fix  	      integrator all nve
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo	      1000
dump          d_equi all xyz 1000 equilibration.xyz
dump_modify   d_equi element {element_list} sort id
fix           equi all langevin {config_dict['temperature']} {config_dict['temperature']} $(100.0*dt) 42
run 	      10000
unfix         equi
unfix	      fcom
undump	      d_equi
unfix 	      integrator
reset_timestep 0
"""
        if config_dict['thermostat'] == 'Langevin':
            input_file_content += f"""# --------- Langevin MD ---------
fix  	      integrator all nve
fix	          pressavg all ave/time 1 1 1 v_p ave running
fix           prod all langevin {config_dict['temperature']} {config_dict['temperature']} $(100.0*dt) 42
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        {config_dict['log_interval']}
thermo_style  custom step temp pe ke etotal press vol
dump          d_prod all xyz {config_dict['write_interval']} md_traj.xyz
dump_modify   d_prod element {element_list} sort id
fix           log_energy all print {config_dict['write_interval']} """+r""" "${pot_e}" file energies.txt screen no title "" """
            input_file_content += print_production[0] + f"""


run           {config_dict['nsteps']}     

unfix         prod
undump        d_prod"""
            input_file_content += print_production[1] + f"""
unfix         integrator
unfix         log_energy
"""+r"""
variable      apre equal f_pressavg
print         ">>> Average pressur is ${apre} bar."
unfix 	      fcom 
unfix 	      pressavg
"""
        elif config_dict['thermostat'] == 'NoseHooverChainNVT':
            input_file_content += f"""# --------- NVT MD ---------
fix           pressavg all ave/time 1 1 1 v_p ave running
fix           prod all nvt temp {config_dict['temperature']} {config_dict['temperature']} $(100.0*dt)
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        {config_dict['log_interval']}
thermo_style  custom step temp pe ke etotal press vol
dump          d_prod all xyz {config_dict['write_interval']} md_traj.xyz
dump_modify   d_prod element {element_list} sort id
fix           log_energy all print {config_dict['write_interval']} """+r""" "${pot_e}" file energies.txt screen no title "" """
            input_file_content += print_production[0] + f"""

run           {config_dict['nsteps']}     

unfix         prod
unfix         log_energy
undump        d_prod"""
            input_file_content += print_production[1] + r"""
variable      apre equal f_pressavg
print         ">>> Average pressur is ${apre} bar."
unfix 	      fcom 
unfix 	      pressavg
"""

        elif config_dict['thermostat'] == 'Bussi':
            input_file_content += f"""# --------- Bussi MD ---------
fix  	      integrator all nve
fix	          pressavg all ave/time 1 1 1 v_p ave running
fix           prod all temp/csvr {config_dict['temperature']} {config_dict['temperature']} $(100.0*dt) 42
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        {config_dict['log_interval']}
thermo_style  custom step temp pe ke etotal press vol
dump          d_prod all xyz {config_dict['write_interval']} md_traj.xyz
dump_modify   d_prod element {element_list} sort id
fix           log_energy all print {config_dict['write_interval']} """+r""" "${pot_e}" file energies.txt screen no title "" """
            input_file_content += print_production[0] + f"""

run           {config_dict['nsteps']}     

unfix         prod
unfix         log_energy
undump        d_prod
unfix         integrator"""
            input_file_content += print_production[1] + r"""
variable      apre equal f_pressavg
print         ">>> Average pressur is ${apre} bar."
unfix 	      fcom 
unfix 	      pressavg
"""

        elif config_dict['thermostat'] == 'NPT':  
            # Check if PBC 3x3 matrix is non-orhtogonal: off diagonal elements are not zero
            pbc_matrix = np.array(config_dict['pbc_list']).reshape(3, 3)
            if np.any(np.abs(pbc_matrix - np.diag(np.diag(pbc_matrix))) > 1e-6):
                npt_fix = f" tri {config_dict['pressure']} {config_dict['pressure']} $(1000.0*dt)"
            else:
                npt_fix = f" iso {config_dict['pressure']} {config_dict['pressure']} $(1000.0*dt)"
 
            input_file_content += f"""# --------- NPT Run ---------
fix 	      integrator all npt temp {config_dict['temperature']} {config_dict['temperature']} $(100.0*dt) {npt_fix}
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        {config_dict['log_interval']}
dump          d_npt all xyz {config_dict['write_interval']} npt_run.xyz
dump_modify   d_npt element {element_list} sort id
fix           log_energy all print {config_dict['write_interval']} """+r""" "${pot_e}" file energies.txt screen no title "" """
            input_file_content += print_production[0] + f"""

fix           volavg all ave/time 1 1 1 v_v ave running
fix           pressavg all ave/time 1 1 1 v_p ave running
thermo_style  custom step temp pe etotal press vol f_pressavg f_volavg avecx avecy avecz bvecx bvecy bvecz cvecx cvecy cvecz
run 	      {config_dict['nsteps']}
unfix 	      fcom
unfix	      integrator
unfix         log_energy
"""+r"""
variable      boxvol equal f_volavg
variable      rdens equal (mass(all)/6.02214086E-1/${boxvol})
print         ">>> Average volume is ${boxvol} Angstrom^3"
print         ">>> Resulting density is ${rdens} g/cm^3."

variable      a1 equal avecx
variable      a2 equal avecy
variable      a3 equal avecz
variable      b1 equal bvecx
variable      b2 equal bvecy
variable      b3 equal bvecz
variable      c1 equal cvecx
variable      c2 equal cvecy
variable      c3 equal cvecz
print         "----------------------------------------------------------------"
print	      "------------------------NEW CELL VECTORS------------------------" 
print         ">>> Cell A-vector ${a1} ${a2} ${a3}."
print         ">>> Cell B-vector ${b1} ${b2} ${b3}."
print         ">>> Cell C-vector ${c1} ${c2} ${c3}."
print         "----------------------------------------------------------------"
variable      alpha equal xy
variable      beta equal xz
variable      gamma equal yz
variable      len_a equal lx 
variable      len_b equal ly
variable      len_c equal lz

print         "----------------------------------------------------------------"
print         "------------------------NEW CELL LENGTHS------------------------"
print         ">>> A length ${len_a} A."
print         ">>> B length ${len_b} A."
print         ">>> C length ${len_c} A."
print         ">>> A tilt ${alpha}."
print         ">>> B tilt ${beta}."
print         ">>> C tilt ${gamma}."
print         "----------------------------------------------------------------"

print "${a1} ${a2} ${a3}" file deformed_pbc screen no
print "${b1} ${b2} ${b3}" append deformed_pbc screen no
print "${c1} ${c2} ${c3}" append deformed_pbc screen no


undump        d_npt"""
            input_file_content += print_production[1] + r"""
unfix         pressavg
unfix	      volavg
"""+f"""
write_dump all xyz last_coord.xyz modify sort id element {element_list}
"""+r"""
# --------- Shrink to Final Density ---------
fix 	      defo all deform 1 x final 0.0 ${len_a} y final 0.0 ${len_b} z final 0.0 ${len_c} units box
if "${alpha} != 0 && ${beta} != 0 && ${gamma} != 0" then fix defo all deform 1 xy final ${alpha} xz final ${beta} yz final ${gamma} units box
"""+f"""
fix 	      integrator all nvt temp {config_dict['temperature']} {config_dict['temperature']} $(100.0*dt)
fix 	      fcom all momentum 10000 linear 1 1 1 rescale
dump          d_shrink all xyz 10 shrink_traj.xyz
dump_modify   d_shrink element {element_list} sort id
thermo_style  custom step temp pe etotal press vol 

run 	      1000

unfix 	      defo
unfix 	      fcom
unfix 	      integrator
undump 	      d_shrink

write_dump all xyz deformed_system.xyz modify sort id element {element_list}
"""

    elif run_type == "RECALC":
        # Convert the xyz trajectory file to LAMMPS data format
        convert_trajectory_to_lammps(config_dict['coord_file'], config_dict['pbc_list'], get_element_list(config_dict['coord_file'], list_only=True))
        input_file_content += f"""
# --------- Neighbors ---------
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes

# --------- Rerun ---------
thermo        1
thermo_style  custom step temp pe ke etotal press vol
dump          d_rerun all xyz 1 rerun.xyz
dump_modify   d_rerun element {element_list} sort id
dump          d_forces all custom 1 md_frc.lammpstrj type fx fy fz
dump_modify   d_forces sort id
fix           log_energy all print 1 """+r""" "${pot_e}" file energies.txt screen no title "" """+f"""

rerun         {config_dict['coord_file'].replace('.xyz', '.lammpstrj')} dump x y z

undump	      d_rerun
undump	      d_forces
unfix         log_energy
"""
    else:
        raise ValueError(f"Unsupported run type: {run_type}")

    
    input_file_content += f"""# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
    
    # Write the input file
    input_file_names_dict = {
        'GEO_OPT': "lammps_geoopt.inp",
        'CELL_OPT': "lammps_cellopt.inp",
        'MD': "lammps_md.inp",
        'RECALC': "lammps_rerun.inp"
    }

    open(input_file_names_dict[run_type], 'w').write(input_file_content)

    # Write the runscript
    runscript_writer(run_type, config_dict)

def runscript_writer(run_type, config_dict):
    """
    Function to write the runscript for LAMMPS based on the run type.
    """
    input_file_names_dict = {
        'GEO_OPT': "lammps_geoopt.inp",
        'CELL_OPT': "lammps_cellopt.inp",
        'MD': "lammps_md.inp",
        'RECALC': "lammps_rerun.inp"
    }

    # Load the template for the runscript
    cpu_template, gpu_template = lammps_runscript()

    # Define the variables from the templates
    cpu_script = cpu_template.replace("$$PROJECT_NAME$$", f"{config_dict['project_name']}")
    cpu_script = cpu_script.replace("$$INPUT_FILE$$", input_file_names_dict[run_type])
    gpu_script = gpu_template.replace("$$PROJECT_NAME$$", f"{config_dict['project_name']}")
    gpu_script = gpu_script.replace("$$INPUT_FILE$$", input_file_names_dict[run_type])

    open("runscript.sh", 'w').write(cpu_script)
    open("gpu_script.job", 'w').write(gpu_script)

    if "$$" in cpu_script or "$$" in gpu_script:
            raise ValueError("The template includes variable placeholders that need to be replaced.")
    print("The Runscripts were created for GPU and CPU! ")
    # Check if BSUB is in cpu_script
    if "BSUB" in cpu_script:
        print("Start the calculation with 'bsub < runscript.sh' or with 'batch.1gpu gpu_script.job'")
    else:
        print("Start the calculation with 'sbatch runscript.sh' or 'sbatch runscript.sh'")

def convert_trajectory_to_lammps(traj_file, cell, element_list):
    """
    Function to convert an xyz trajectory file to LAMMPS data format using ASE
    """
    from ase.data import atomic_numbers

    # --- Load trajectory ---
    frames = read(traj_file, index=":")

    # --- Set periodic cell for each frame ---
    for atoms in frames:
        atoms.set_cell(cell)
        atoms.set_pbc([True, True, True])

    # --- Atom element to type mapping ---
    element_order = element_list
    element_to_type = {el: i + 1 for i, el in enumerate(element_order)}

    # --- Write LAMMPS-style trajectory ---
    with open(traj_file.replace('.xyz', '.lammpstrj'), "w") as f:
        for i, atoms in enumerate(frames):
            natoms = len(atoms)
            symbols = atoms.get_chemical_symbols()
            positions = atoms.get_positions()
            cell = atoms.get_cell()

            # Check if the cell is orthogonal
            if not np.allclose(cell, np.diag(np.diag(cell)), atol=1e-6):
                h = np.array(cell)
                lx = np.linalg.norm(h[0])
                xy = np.dot(h[1], h[0]) / lx
                xz = np.dot(h[2], h[0]) / lx
                ly = np.sqrt(np.linalg.norm(h[1])**2 - xy**2)
                yz = (np.dot(h[2], h[1]) - xy * xz) / ly
                lz = np.sqrt(np.linalg.norm(h[2])**2 - xz**2 - yz**2)

                xlo, xhi = 0.0, lx
                ylo, yhi = 0.0, ly
                zlo, zhi = 0.0, lz
                line1 = f"{xlo} {xhi} {xy}\n"
                line2 = f"{ylo} {yhi} {xz} {yz}\n"
                line3 = f"{zlo} {zhi} {yz}\n"

            else:
                # Orthogonal cell
                xlo, xhi = 0.0, cell[0, 0]
                ylo, yhi = 0.0, cell[1, 1]
                zlo, zhi = 0.0, cell[2, 2]
                line1 = f"{xlo} {xhi}\n"
                line2 = f"{ylo} {yhi}\n"
                line3 = f"{zlo} {zhi}\n"

            f.write("ITEM: TIMESTEP\n")
            f.write(f"{i}\n")
            f.write("ITEM: NUMBER OF ATOMS\n")
            f.write(f"{natoms}\n")
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(line1)
            f.write(line2)
            f.write(line3)
            f.write("ITEM: ATOMS id type x y z\n")
            for j, (el, pos) in enumerate(zip(symbols, positions)):
                atom_type = element_to_type[el]
                f.write(f"{j+1} {atom_type} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n")
    

