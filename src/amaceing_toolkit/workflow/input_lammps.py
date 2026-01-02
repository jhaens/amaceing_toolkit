import os
import sys
import argparse
import datetime
import numpy as np
import subprocess
from typing import Dict, Any, Optional, Union
from ase.io import read, write

from amaceing_toolkit.default_configs.runscript_loader import RunscriptLoader


class LAMMPSInputGeneratorWrapper:
    """
    Wrapper class for generating LAMMPS input files for different run types and MLIP frameworks.
    """
    
    SUPPORTED_RUN_TYPES = ['GEO_OPT', 'CELL_OPT', 'MD', 'RECALC']
    SUPPORTED_FRAMEWORKS = ['mace', 'sevennet', 'grace']

    def __init__(self, run_type: str, framework: str, config: Dict[str, Any]):
        if run_type not in self.SUPPORTED_RUN_TYPES:
            raise ValueError(f"Unsupported run type: {run_type}. Supported: {self.SUPPORTED_RUN_TYPES}")
        if framework not in self.SUPPORTED_FRAMEWORKS:
            raise ValueError(f"Unsupported framework: {framework}. Supported: {self.SUPPORTED_FRAMEWORKS}")
        
        self.run_type = run_type
        self.framework = framework
        self.config = config

        # Build the Input file from the config
        self.input_generator = LAMMPSInputGenerator(framework, config)
        
        if run_type == 'GEO_OPT':
            self.build_input_file = self.input_generator.generate_geoopt_input
        elif run_type == 'CELL_OPT':
            self.build_input_file = self.input_generator.generate_cellopt_input
        elif run_type == 'MD':
            self.build_input_file = self.input_generator.generate_md_input
        elif run_type == 'RECALC':
            self.build_input_file = self.input_generator.generate_recalc_input


    def run_and_save(self) -> str:
        """Generate and save the LAMMPS input file."""

        # Generate the input file content
        input_content = self.build_input_file()
        
        # Write to file
        filenames = {
            'GEO_OPT': f'lammps_geoopt.inp',
            'CELL_OPT': f'lammps_cellopt.inp',
            'MD': f'lammps_md.inp',
            'RECALC': f'lammps_recalc.inp'
        }

        filename = filenames.get(self.run_type)

        with open(filename, 'w') as f:
            f.write(input_content)
        
        print(f"LAMMPS input file written to: {filename}")

        # Write runscript
        self.runscript_wrapper(filename)

        return filename

    def runscript_wrapper(self, filename) -> None:
        """
        Generate the runscript for the input file: CPU and GPU version.
        """
        # Generate the runscript content
        cpu_runscript_content = RunscriptLoader(self.framework, self.config['project_name'], filename, 'lmp', 'cpu').load_runscript()
        gpu_runscript_content = RunscriptLoader(self.framework, self.config['project_name'], filename, 'lmp', 'gpu').load_runscript()

        if cpu_runscript_content == '0' or gpu_runscript_content == '0':
            return

        rs_name = {'cpu': 'runscript.sh', 'gpu': 'gpu_script.job'}

        # Save the runscript files
        with open(rs_name['cpu'], 'w') as f_cpu:
            f_cpu.write(cpu_runscript_content)
        os.chmod(rs_name['cpu'], 0o755)

        with open(rs_name['gpu'], 'w') as f_gpu:
            f_gpu.write(gpu_runscript_content)
        os.chmod(rs_name['gpu'], 0o755)

        print(f"Runscripts written to: {rs_name['cpu']} and {rs_name['gpu']}")

class LAMMPSInputGenerator:
    """
    Main class for generating LAMMPS input files for different MLIP frameworks.
    """
    
    def __init__(self, framework: str, config: Dict[str, Any]):
        self.framework = framework
        self.config = config
        self.mlip_handler = MLIPFrameworkHandler(framework, config)
        
    def _get_element_list(self, list_only: bool = False) -> Union[str, list]:
        """Extract element list from coordinate file."""
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
        if self.config['coord_file'].endswith('.xyz'):
            atoms = read(self.config['coord_file'])
        else:
            atoms = read(self.config['coord_file'], format='lammps-data')
        elements = atoms.get_chemical_symbols()
        unique_elements = [el for el in elements_ordered if el in elements]
        
        if list_only:
            return unique_elements
        else:
            return ' '.join(unique_elements)

    def _prepare_coordinate_file(self) -> str:
        """Prepare coordinate file for LAMMPS."""
        if self.config['coord_file'].endswith('.xyz'):
            # Convert XYZ to LAMMPS data format
            atoms = read(self.config['coord_file'], format='xyz', index=0)
            atoms.set_cell(np.array(self.config['pbc_list']).reshape(3, 3))
            atoms.set_pbc([True, True, True])
            
            data_file = self.config['coord_file'].replace('.xyz', '.data')
            write(data_file, atoms, units="metal", masses=True, 
                  specorder=self._get_element_list(list_only=True), 
                  format="lammps-data", atom_style="atomic")
            return data_file
        else:
            return self.config['coord_file']

    def _get_header(self) -> str:
        """Generate LAMMPS header."""
        return f"""# --------- Units and System Setup ---------
units         metal
atom_style    atomic
atom_modify   map yes
newton        on
boundary      p p p
variable      p equal press
variable      v equal vol 
variable      pot_e equal pe"""

    def _get_coordinates_section(self) -> str:
        """Generate coordinates reading section."""
        data_file = self._prepare_coordinate_file()
        return f"\nread_data     {data_file}\n"

    def _get_potential_section(self) -> str:
        """Generate potential section using MLIP handler."""
        return self.mlip_handler.get_potential_section(self._get_element_list())

    def _get_neighbors_section(self) -> str:
        """Generate neighbors section."""
        return """# --------- Neighbors ---------
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes"""

    def _get_footer(self) -> str:
        """Generate footer."""
        return f"""
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""

    def generate_geoopt_input(self) -> str:
        """Generate geometry optimization input."""
        element_list = self._get_element_list()
        
        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}
{self._get_neighbors_section()}

# --------- Minimization ---------
thermo        1
dump          d_go all xyz 1 geoopt_traj.xyz
dump_modify   d_go element {element_list} sort id
fix           log_energy all print {self.config.get('write_interval', 1)} """ + r'"${pot_e}"' + f""" file energies.txt screen no title ""
minimize      1.0e-5 1.0e-7 {int(self.config['max_iter'])} {10*int(self.config['max_iter'])}
undump        d_go
unfix         log_energy

write_dump all xyz {self.config['project_name']}_geoopt.xyz modify sort id element {element_list}
{self._get_footer()}"""
        
        return content

    def generate_cellopt_input(self) -> str:
        """Generate cell optimization input."""
        element_list = self._get_element_list()
        
        # Check if PBC matrix is non-orthogonal
        pbc_matrix = np.array(self.config['pbc_list']).reshape(3, 3)
        if np.any(np.abs(pbc_matrix - np.diag(np.diag(pbc_matrix))) > 1e-6):
            cellopt_fix = "cellopt all box/relax tri 0.0 vmax 0.001"
        else:
            # keep symmetry of cell
            cellopt_fix = "cellopt all box/relax iso 0.0 vmax 0.001"
            # do not keep symmetry of cell
            # cellopt_fix = "cellopt all box/relax aniso 0.0 vmax 0.001"

        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}
{self._get_neighbors_section()}

# --------- Minimization ---------
thermo        1
dump          d_co all xyz 1 cellopt_traj.xyz
dump_modify   d_co element {element_list} sort id
fix           log_energy all print {self.config.get('write_interval', 1)} """ + r'"${pot_e}"' + f""" file energies.txt screen no title ""
fix           {cellopt_fix}
minimize      1.0e-5 1.0e-7 {int(self.config['max_iter'])} {10*int(self.config['max_iter'])}
unfix         cellopt
unfix         log_energy
undump        d_co

write_dump all xyz {self.config['project_name']}_cellopt.xyz modify sort id element {element_list}

print "avecx avecy avecz" file pbc_new screen no
print "bvecx bvecy bvecz" append pbc_new screen no
print "cvecx cvecy cvecz" append pbc_new screen no
{self._get_footer()}"""
        
        return content

    def generate_md_input(self) -> str:
        """Generate molecular dynamics input."""
        element_list = self._get_element_list()
        timestep = float(self.config['timestep']) * 0.001  # Convert fs to ps
        
        # Get thermostat-specific content
        thermostat_content = self._get_thermostat_content(element_list)
        
        # Get trajectory printing if requested
        ext_traj_content = self._get_ext_traj_content(element_list)
        
        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}

# --------- Timestep and Neighbors ---------
timestep      {timestep}     # ps
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes

# --------- Initial Velocity ---------
velocity      all create {self.config['temperature']} 42 dist uniform rot yes mom yes

# --------- Equilibration ---------
# 
fix           integrator all nve
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        1000
dump          d_equi all xyz 1000 equilibration.xyz
dump_modify   d_equi element {element_list} sort id
fix           equi all langevin {self.config['temperature']} {self.config['temperature']} $(100.0*dt) 42
run           10000
unfix         equi
unfix         fcom
undump        d_equi
unfix         integrator
reset_timestep 0

{thermostat_content}
{self._get_footer()}"""
        
        restart_content = f"""{self._get_header()}
read_restart  md.restart.* 
{self._get_potential_section()}

# --------- Timestep and Neighbors ---------
timestep      {timestep}     # ps
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes

{thermostat_content}
{self._get_footer()}"""
        
        # Write the restart input file
        with open('lammps_md_restart.inp', 'w') as f_restart:
            f_restart.write(restart_content)

        return content

    def generate_recalc_input(self) -> str:
        """Generate recalculation input."""
        element_list = self._get_element_list()
        
        # Convert trajectory to LAMMPS format
        self._convert_trajectory_to_lammps()
        
        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}
{self._get_neighbors_section()}

# --------- Rerun ---------
thermo        1
thermo_style  custom step temp pe ke etotal press vol
dump          d_rerun all xyz 1 rerun.xyz
dump_modify   d_rerun element {element_list} sort id
dump          d_forces all custom 1 md_frc.lammpstrj type fx fy fz
dump_modify   d_forces sort id
fix           log_energy all print 1 """ + r'"${pot_e}"' + f""" file energies.txt screen no title ""

rerun         {self.config['coord_file'].replace('.xyz', '.lammpstrj')} dump x y z

undump        d_rerun
undump        d_forces
unfix         log_energy
{self._get_footer()}"""
        
        return content

    def _get_thermostat_content(self, element_list: str) -> str:
        """Generate thermostat-specific content for MD."""
        thermostat = self.config.get('thermostat', 'Langevin')
        temperature = self.config['temperature']
        nsteps = self.config['nsteps']
        write_interval = self.config['write_interval']
        log_interval = self.config['log_interval']
        print_ext_traj = self.config.get('print_ext_traj', 'n')
        ext_traj_content = self._get_ext_traj_content(element_list)
        
        base_content = f"""# --------- {thermostat} MD ---------
fix           pressavg all ave/time 1 1 1 v_p ave running
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        {log_interval}
thermo_style  custom step temp pe ke etotal press vol
dump          d_prod all xyz {write_interval} md_traj.xyz
dump_modify   d_prod element {element_list} sort id
dump_modify   d_prod append yes
fix           log_energy all print {write_interval} """ + r'"${pot_e}"' + """ append energies.txt screen no

"""
        
        if thermostat == 'Langevin':
            content = f"""{base_content}
fix           integrator all nve
fix           prod all langevin {temperature} {temperature} $(100.0*dt) 42
{ext_traj_content[0]}

restart       {write_interval} md.restart.1 md.restart.2

run           {nsteps}

write_restart final.restart

{ext_traj_content[1]}
unfix         prod
unfix         integrator"""
        
        elif thermostat == 'NoseHooverChainNVT':
            content = f"""{base_content}
fix           prod all nvt temp {temperature} {temperature} $(100.0*dt)
{ext_traj_content[0]}

restart       {write_interval} md.restart.1 md.restart.2


run           {nsteps}

write_restart final.restart

{ext_traj_content[1]}
unfix         prod"""
        
        elif thermostat == 'Bussi':
            content = f"""{base_content}
fix           integrator all nve
fix           prod all temp/csvr {temperature} {temperature} $(100.0*dt) 42
{ext_traj_content[0]}

restart       {write_interval} md.restart.1 md.restart.2


run           {nsteps}

write_restart final.restart

{ext_traj_content[1]}
unfix         prod
unfix         integrator"""
        
        elif thermostat == 'NPT':
            pressure = self.config.get('pressure', 1.0)
            # Check if PBC matrix is non-orthogonal
            pbc_matrix = np.array(self.config['pbc_list']).reshape(3, 3)
            if np.any(np.abs(pbc_matrix - np.diag(np.diag(pbc_matrix))) > 1e-6):
                npt_fix = f"tri {pressure} {pressure} $(1000.0*dt)"
            else:
                npt_fix = f"iso {pressure} {pressure} $(1000.0*dt)"
            
            content = f"""{base_content}
fix           integrator all npt temp {temperature} {temperature} $(100.0*dt) {npt_fix}
{ext_traj_content[0]}

restart       100000 md.restart.1 md.restart.2

run           {nsteps}

write_restart final.restart

{ext_traj_content[1]}
unfix         integrator
""" + r"""
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
print "${c1} ${c2} ${c3}" append deformed_pbc screen no """
        
        else:
            raise ValueError(f"Unsupported thermostat: {thermostat}")
        
        content += f"""
undump        d_prod
unfix         log_energy
"""
        if thermostat == 'NPT':
            content += self._shrink_module(element_list)


        content += r"""
variable      apre equal f_pressavg
print         ">>> Average pressure is ${apre} bar."
unfix         fcom 
unfix         pressavg"""
        
        return content

    def _get_ext_traj_content(self, element_list: str) -> str:
        """Generate extended trajectory content if requested."""
        if self.config['print_ext_traj'] == 'n':
            return ["", ""]
        else:
            write_interval = self.config['write_interval']
            return [f"""dump          d_prod_frc all custom {write_interval} md_frc.lammpstrj type fx fy fz
dump_modify   d_prod_frc sort id
dump_modify   d_prod_frc append yes""", """
undump        d_prod_frc"""]

    def _shrink_module(self, element_list: str) -> str:
        return f"""write_dump all xyz last_coord.xyz modify sort id element {element_list}
""" +r"""# --------- Shrink to Final Density ---------
fix 	      defo all deform 1 x final 0.0 ${len_a} y final 0.0 ${len_b} z final 0.0 ${len_c} units box
if "${alpha} != 0 && ${beta} != 0 && ${gamma} != 0" then fix defo all deform 1 xy final ${alpha} xz final ${beta} yz final ${gamma} units box
"""+f"""
fix 	      integrator all nvt temp {self.config['temperature']} {self.config['temperature']} $(100.0*dt)
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

    def _convert_trajectory_to_lammps(self):
        """Convert XYZ trajectory to LAMMPS format."""
        from ase.data import atomic_numbers
        
        traj_file = self.config['coord_file']
        cell = self.config['pbc_list']
        element_list = self._get_element_list(list_only=True)
        
        # Load trajectory
        frames = read(traj_file, index=":")
        
        # Set periodic cell for each frame
        for atoms in frames:
            atoms.set_cell(cell)
            atoms.set_pbc([True, True, True])
        
        # Atom element to type mapping
        element_to_type = {el: i + 1 for i, el in enumerate(element_list)}
        
        # Write LAMMPS-style trajectory
        with open(traj_file.replace('.xyz', '.lammpstrj'), "w") as f:
            for i, atoms in enumerate(frames):
                positions = atoms.get_positions()
                symbols = atoms.get_chemical_symbols()
                cell_params = atoms.get_cell()

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
                
                f.write(f"ITEM: TIMESTEP\n{i}\n")
                f.write(f"ITEM: NUMBER OF ATOMS\n{len(atoms)}\n")
                f.write("ITEM: BOX BOUNDS pp pp pp\n")
                f.write(line1)
                f.write(line2)
                f.write(line3)
                f.write("ITEM: ATOMS id type x y z\n")
                
                for j, (symbol, pos) in enumerate(zip(symbols, positions)):
                    atom_type = element_to_type[symbol]
                    f.write(f"{j+1} {atom_type} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n")


class MLIPFrameworkHandler:
    """
    Handler for different MLIP frameworks.
    """
    
    def __init__(self, framework: str, config: Dict[str, Any]):
        self.framework = framework
        self.config = config
        
    def get_potential_section(self, element_list: str) -> str:
        """Get potential section based on framework."""
        if self.framework == 'mace':
            return self._get_mace_potential_section(element_list)
        elif self.framework == 'sevennet':
            return self._get_sevennet_potential_section(element_list)
        elif self.framework == 'grace':
            return self._get_grace_potential_section(element_list)
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
    
    def _get_mace_potential_section(self, element_list: str) -> str:
        """Generate MACE potential section."""
        model_file = self._prepare_mace_model()
        
        return f"""# --------- MACE Potential Setup ---------
pair_style    mace no_domain_decomposition
pair_coeff    * * {model_file} {element_list}
"""
    
    def _get_sevennet_potential_section(self, element_list: str) -> str:
        """Generate SevenNet potential section."""
        model_file = self._prepare_sevennet_model()
        
        dispersion = self.config.get('dispersion_via_simenv', 'n')
        
        if dispersion == 'n':
            return f"""# --------- SevenNet Potential Setup ---------
pair_style    e3gnn
pair_coeff    * * {model_file} {element_list}
"""
        else:
            formatted_functionals = {'BLYP': 'b-lyp', 'PBE': 'pbe'}
            functional = input('Enter the functional for dispersion (e.g., BLYP, PBE): ').strip().lower()
            functional = formatted_functionals.get(functional, functional)

            return f"""# --------- SevenNet Potential Setup (with dispersion) ---------
pair_style    hybrid/overlay e3gnn d3 9000 1600 damp_bj {functional}
pair_coeff    * * e3gnn {model_file} {element_list}
pair_coeff    * * d3 {element_list}
"""
        
    def _get_grace_potential_section(self, element_list: str) -> str:
        """Generate Grace potential section."""
        model_path = self._get_grace_model_path()

        return f"""# --------- Grace Potential Setup ---------
pair_style    grace
pair_coeff    * * {model_path} {element_list}
"""

    def _prepare_mace_model(self) -> str:
        """Prepare MACE model file for LAMMPS."""
        foundation_model = self.config['foundation_model'][0] if isinstance(self.config['foundation_model'], list) else self.config['foundation_model']
        model_size = self.config['foundation_model'][1] if isinstance(self.config['foundation_model'], list) else None
        
        if foundation_model.endswith('.pt'):
            return foundation_model
        
        # Handle model conversion
        try:
            import mace
            converter_script_path = mace.__file__.replace('__init__.py', 'cli/create_lammps_model.py')
        except ImportError:
            raise ImportError("MACE package not found. Please install mace-torch. Or convert the model yourself using the MACE CLI.")
        
        if foundation_model.endswith('.model'):
            # Convert custom model
            convert_command = f"python {converter_script_path} {foundation_model}"
            print(f"Converting model {foundation_model} to LAMMPS format...")
            
            try:
                subprocess.run(convert_command, shell=True, check=True, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Model conversion failed with exit code {e.returncode}")
            
            return f"{foundation_model}-lammps.pt"
        
        else:
            # Handle foundation models
            download_model_dict = {
                'mp_small': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2023-12-10-mace-128-L0_energy_epoch-249.model',
                'mp_medium': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2023-12-03-mace-128-L1_epoch-199.model',
                'mp_large': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2024-01-07-mace-128-L2_epoch-199.model',
                'mpa_medium': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mpa_0/mace-mpa-0-medium.model',
                'off_small': 'https://github.com/ACEsuit/mace-off/blob/main/mace_off23/MACE-OFF23_small.model',
                'off_medium': 'https://github.com/ACEsuit/mace-off/blob/main/mace_off23/MACE-OFF23_medium.model',
                'off_large': 'https://github.com/ACEsuit/mace-off/blob/main/mace_off23/MACE-OFF23_large.model',
                'omol_extra-large': "https://github.com/ACEsuit/mace-foundations/releases/download/mace_omol_0/MACE-omol-0-extra-large-1024.model",
                'small-omat-0': 'https://github.com/ACEsuit/mace-foundations/releases/download/mace_omat_0/mace-omat-0-small.model',
                'medium-omat-0': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_omat_0/mace-omat-0-medium.model',
                'medium-matpes-pbe-0': 'https://github.com/ACEsuit/mace-foundations/releases/download/mace_matpes_0/MACE-matpes-pbe-omat-ft.model',
                'medium-matpes-r2scan-0': 'https://github.com/ACEsuit/mace-foundations/releases/download/mace_matpes_0/MACE-matpes-r2scan-omat-ft.model',
            }
            
            # Build model key
            if model_size == 'medium-mpa-0':
                model_key = 'mpa_medium'
            elif 'matpes' in model_size or 'omat' in model_size:
                model_key = model_size
            else:
                model_key = f"{foundation_model.split('_')[-1]}_{model_size}"
            
            if model_key not in download_model_dict:
                raise ValueError(f"Unknown model: {model_key}")
            
            model_url = download_model_dict[model_key]
            model_file = f"{model_key}.model"
            
            # Download model if not exists
            if not os.path.exists(model_file):
                print(f"Downloading model {model_key} from {model_url}...")
                subprocess.run(f"wget -O {model_file} {model_url}", shell=True, check=True)
            
            # Convert to LAMMPS format
            convert_command = f"python {converter_script_path} {model_file}"
            print(f"Converting model {model_file} to LAMMPS format...")
            subprocess.run(convert_command, shell=True, check=True)
            
            return f"{model_file}-lammps.pt"
    
    def _prepare_sevennet_model(self) -> str:
        """Prepare SevenNet model file for LAMMPS."""
        foundation_model = self.config['foundation_model'][0] if isinstance(self.config['foundation_model'], list) else self.config['foundation_model']
        modal = self.config['foundation_model'][1] if isinstance(self.config['foundation_model'], list) else None
        
        if foundation_model.endswith('.pt'):
            print(f"Model {foundation_model} is already in LAMMPS format.")
            return foundation_model
        
        # Convert model to LAMMPS format
        if "." not in foundation_model:
            # Foundation model name
            if modal:
                convert_command = f"sevenn_get_model {foundation_model} -m {modal} -o {foundation_model}.pt"
            else:
                convert_command = f"sevenn_get_model {foundation_model} -o {foundation_model}.pt"
            
            model_file = f"{foundation_model}.pt"
            
        elif foundation_model.endswith('.pth'):
            # Convert .pth to .pt
            if modal:
                convert_command = f"sevenn_get_model {foundation_model} -m {modal} -o {foundation_model.replace('.pth', '.pt')}"
            else:
                convert_command = f"sevenn_get_model {foundation_model} -o {foundation_model.replace('.pth', '.pt')}"
            
            model_file = foundation_model.replace('.pth', '.pt')
        else:
            raise ValueError("SevenNet model file must be .pt, .pth, or a foundation model name")

        print(f"Converting SevenNet model {foundation_model} to LAMMPS format...")
        
        try:
            subprocess.run(convert_command, shell=True, check=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"SevenNet model conversion failed with exit code {e.returncode}")
        
        return model_file
    
    def _get_grace_model_path(self) -> str:
        """Get the path to the Grace model file."""
        model_path = self.config['foundation_model']

        if self.config['foundation_model'] in ['GRACE-1L-OMAT', 'GRACE-2L-OMAT', 'GRACE-1L-OAM', 'GRACE-2L-OAM']:
            # Foundation model: files are located in /home/<user>/.cache/grace/<foundation_model>
            user_home = os.path.expanduser("~")
            model_path = os.path.join(user_home, '.cache', 'grace', f"{self.config['foundation_model']}")
        else:
            # Custom model path
            if '..' in self.config['foundation_model']:
                model_path = os.path.abspath(self.config['foundation_model'])
            else:
                model_path = self.config['foundation_model']

        return model_path


# TEST the code
# if __name__ == "__main__":
#     run_type = 'MD'  # Example run type
#     framework = 'mace'  # Example framework
#     config = configs_mace('default')  # Load default configuration
#     # add project_name to config
#     config['MD']['foundation_model'] = ['mace_mp', 'small']  # Example foundation model
#     config['MD']['project_name'] = 'example_project'
#     config['MD']['dispersion_via_simenv'] = 'n'
#     config['MD']['pbc_list'] = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
#     config['MD']['coord_file'] = 'coord.xyz'  # Example coordinate file
#     print(config['MD'])
#     generator = LAMMPSInputGeneratorWrapper(run_type, framework, config['MD'])
#     #generator.run_and_save()
#     print("Input file generation completed.")