import os
import sys
import argparse
import datetime
import numpy as np
from typing import Dict, Any, Optional, Union

from amaceing_toolkit.default_configs.runscript_loader import RunscriptLoader


class ASEInputGeneratorWrapper:
    """
    Wrapper class for generating ASE input files for different run types.
    """
    
    SUPPORTED_RUN_TYPES = ['GEO_OPT', 'CELL_OPT', 'MD', 'RECALC']
    SUPPORTED_FRAMEWORKS = ['mace', 'mattersim', 'sevennet', 'orb', 'grace']
    
    def __init__(self, run_type: str, framework: str, config: Dict[str, Any]):
        if run_type not in self.SUPPORTED_RUN_TYPES:
            raise ValueError(f"Unsupported run type: {run_type}. Supported: {self.SUPPORTED_RUN_TYPES}")
        if framework not in self.SUPPORTED_FRAMEWORKS:
            raise ValueError(f"Unsupported framework: {framework}. Supported: {self.SUPPORTED_FRAMEWORKS}")

        self.run_type = run_type
        self.framework = framework
        self.config = config


        # Build the Input file from the config
        self.input_generator = ASEInputGenerator(framework, config)

        if run_type == 'GEO_OPT':
            self.build_input_file = self.input_generator.generate_geoopt_input
        elif run_type == 'CELL_OPT':
            self.build_input_file = self.input_generator.generate_cellopt_input
        elif run_type == 'MD':
            self.build_input_file = self.input_generator.generate_md_input
        elif run_type == 'RECALC':
            self.build_input_file = self.input_generator.generate_recalc_input


    def run_and_save(self) -> str:

        # Generate the input file content
        input_content = self.build_input_file()
        
        # Write to file
        filenames = {
            'GEO_OPT': 'geoopt.py',
            'CELL_OPT': 'cellopt.py',
            'MD': 'md.py',
            'RECALC': 'recalc.py'
        }

        filename = filenames.get(self.run_type)

        with open(filename, 'w') as f:
            f.write(input_content)
        
        print(f"ASE input file written to: {filename}")

        # Write runscript
        self.runscript_wrapper(filename)

        return filename
    
    def runscript_wrapper(self, filename) -> None:
        """
        Generate the runscript for the input file: CPU and GPU version.
        """
        # Generate the runscript content
        cpu_runscript_content = RunscriptLoader(self.framework, self.config['project_name'], filename, 'py', 'cpu').load_runscript()
        gpu_runscript_content = RunscriptLoader(self.framework, self.config['project_name'], filename, 'py', 'gpu').load_runscript()

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

    def __str__(self):
        return f"ASEInputGeneratorWrapper(run_type={self.run_type}, framework={self.framework}, config={self.config})"


class ASEInputGenerator:
    """
    Only to create the input file for ASE calculations.
    """

    def __init__(self, framework, config: Dict[str, Any]):
        self.framework = framework
        self.config = config

    def _footer(self) -> str:
        """
        Footer for the input file.
        """
        return f"""
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
    
    def _get_thermostat_code(self) -> Dict[str, str]:
        """Get thermostat-specific code."""
        thermostat = self.config.get('thermostat', 'Langevin')
        temperature = self.config['temperature']
        timestep = self.config['timestep']
        
        if thermostat == 'Langevin':
            return {
                'import': 'from ase.md import Langevin',
                'dynamics': f'dyn = Langevin(atoms, {timestep} * units.fs, temperature_K={temperature}, friction = 0.01 / units.fs)'
            }
        elif thermostat == 'NoseHooverChainNVT':
            return {
                'import': 'from ase.md.nose_hoover_chain import NoseHooverChainNVT',
                'dynamics': f'dyn = NoseHooverChainNVT(atoms, {timestep} * units.fs, {temperature}, 50 * units.fs)'
            }
        elif thermostat == 'Bussi':
            return {
                'import': 'from ase.md.bussi import Bussi',
                'dynamics': f'dyn = Bussi(atoms, {timestep} * units.fs, temperature_K={temperature}, taut = 100 * units.fs)'
            }
        elif thermostat == 'NPT':
            pressure = self.config.get('pressure', 1.0)
            return {
                'import': 'from ase.md.npt import NPT',
                'dynamics': f'dyn = NPT(atoms, {timestep} * units.fs, temperature_K={temperature}, externalstress={pressure}*units.bar, ttime=20.0*units.fs, pfactor = 2e6*units.GPa*(units.fs**2))'
            }
        else:
            # Default to Langevin
            return {
                'import': 'from ase.md.langevin import Langevin',
                'dynamics': f'dyn = Langevin(atoms, {timestep} * units.fs, temperature_K={temperature}, friction=0.002)'
            }

    def _get_model_code(self) -> list:
        """
        Get the model code based on the foundation model, model size, dispersion and framework.
        """
        foundation_model = self.config['foundation_model'][0] if isinstance(self.config['foundation_model'], list) else self.config['foundation_model']
        model_size = self.config['foundation_model'][1] if isinstance(self.config['foundation_model'], list) else None # only for MACE
        dispersion = self.config.get('dispersion_via_simenv', 'none')

        if self.framework == 'mace':
            model_dict = MLIPFrameworkHandler(self.framework, self.config).model_code(foundation_model, model_size, dispersion)
            return model_dict
        elif self.framework == 'mattersim':
            model_dict = MLIPFrameworkHandler(self.framework, self.config).model_code(foundation_model, dispersion)
            return model_dict
        elif self.framework == 'sevennet':
            modal = model_size
            model_dict = MLIPFrameworkHandler(self.framework, self.config).model_code(foundation_model, modal, dispersion)
            return model_dict
        elif self.framework == 'orb':
            modal = model_size
            model_dict = MLIPFrameworkHandler(self.framework, self.config).model_code(foundation_model, modal, dispersion)
            return model_dict
        elif self.framework == 'grace':
            model_dict = MLIPFrameworkHandler(self.framework, self.config).model_code(foundation_model)
            return model_dict
        else:
            raise ValueError(f"Unsupported framework: {self.framework}.")

    
    def _get_cell_matrix_code(self) -> str:
        """
        Generate the cell matrix code from the PBC list.
        """
        pbc_list = self.config['pbc_list']
        return f"""np.array([[{float(pbc_list[0,0])}, {float(pbc_list[0,1])}, {float(pbc_list[0,2])}], [{float(pbc_list[1,0])}, {float(pbc_list[1,1])}, {float(pbc_list[1,2])}], [{float(pbc_list[2,0])}, {float(pbc_list[2,1])}, {float(pbc_list[2,2])}]])"""

    def generate_geoopt_input(self) -> str:
        """
        Generate geometry optimization input.
        """
        config = self.config
        dict_foundation_model = self._get_model_code()

        return f"""import time
import numpy as np
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import read, write
from ase.optimize import BFGS
{dict_foundation_model['import']}

# Load the MLIP model
mlip_calc = {dict_foundation_model['model']}
print("Loading of MLIP model ({self.framework}) completed: {config['foundation_model']} model")

# Load the coordinates
atoms = read('{config['coord_file']}')			

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({self._get_cell_matrix_code()})

atoms.calc = mlip_calc

# Write the xyz trajectory
xyz_file = 'geoopt_output.xyz'
def save_positions(atoms):
    write(xyz_file, atoms, append=True)

# Set up the optimizer
optimizer = BFGS(atoms, trajectory='geoopt_output.traj', logfile='geoopt_output.log')
optimizer.attach(save_positions, interval=10, atoms=atoms)

# Run the optimizer:
optimizer.run(fmax=0.01, steps={int(config['max_iter'])}) 

# Write the final coordinates
print("Final positions:", atoms.get_positions())
print("Total energy:", atoms.get_potential_energy())

write("{config['project_name']}_geoopt_final.xyz", atoms)
""" + self._footer()
    
    def generate_cellopt_input(self) -> str:
        """
        Generate cell optimization input.
        """
        config = self.config
        dict_foundation_model = self._get_model_code()

        return f"""import time
import numpy as np
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import read, write
from ase.optimize import BFGS, LBFGS
from ase.constraints import ExpCellFilter, StrainFilter
{dict_foundation_model['import']}

# Load the MLIP model
mlip_calc = {dict_foundation_model['model']}
print("Loading of MLIP model ({self.framework}) completed: {config['foundation_model']} model")

# Load the coordinates
atoms = read('{config['coord_file']}')			

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({self._get_cell_matrix_code()})

atoms.calc = mlip_calc

""" + r"""
# Set up logging
def print_dyn():
    imd = optimizer.get_number_of_steps()
    cell = atoms.get_cell()
    print(f" {imd: >3}   ", cell)
""" + f"""
print("Cell size before: ", atoms.cell)
atoms = ExpCellFilter(atoms, hydrostatic_strain=True)
optimizer = LBFGS(atoms, trajectory="cellopt.traj", logfile='cellopt.log')

# Write the xyz trajectory
xyz_file = 'cellopt_output.xyz'
def save_positions(atoms):
    write(xyz_file, atoms, append=True)

optimizer.attach(print_dyn, interval=10)

# Run the optimizer
optimizer.run(fmax=0.01, steps={int(config['max_iter'])})

# Print the final cell size
print("Cell size after optimization: ", atoms.atoms.cell)

# Write the final coordinates
print("Final positions:", atoms.get_positions())
print("Total energy:", atoms.get_potential_energy())

write("{config['project_name']}_cellopt_final.xyz", atoms.atoms)
""" + self._footer()
    
    def generate_md_input(self) -> str:
        """
        Generate molecular dynamics input.
        """
        config = self.config
        dict_foundation_model = self._get_model_code()
        dict_thermostat = self._get_thermostat_code()

        if config["thermostat"] == "NPT":
            lines_log_file = f"""# Log file
dyn.attach(MDLogger(dyn, atoms, 'md.log', header=True, stress=True, peratom=False, mode="a"), interval={int(config['log_interval'])})
"""
        else:
            lines_log_file = f"""# Log file
dyn.attach(MDLogger(dyn, atoms, 'md.log', header=True, stress=False, peratom=False, mode="a"), interval={int(config['log_interval'])})
"""
        lines_traj_file = f"""
# Trajectory file
dyn.attach(Trajectory('{config['project_name']}_md.traj', 'a', atoms), interval={int(config['write_interval'])})
"""

        return f"""import time
import numpy as np
import os
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import read, write
from ase.md import MDLogger
{dict_foundation_model['import']}
{dict_thermostat['import']}

# Load the MLIP model
mlip_calc = {dict_foundation_model['model']}
print("Loading of MLIP model ({self.framework}) completed: {config['foundation_model']} model")

# Load the coordinates (take care if it is the first start or a restart)
if os.path.isfile('{config['project_name']}_md.traj'):
    atoms = read('{config['project_name']}_md.traj')
    #atoms = read('{config['project_name']}_restart.traj')
else:
    atoms = read('{config['coord_file']}')

# Set the box
atoms.pbc = (True, True, True)
atoms.set_cell({self._get_cell_matrix_code()})

atoms.calc = mlip_calc

# Set the temperature in Kelvin and initialize the velocities (only if it is the first start)
temperature_K = {int(config['temperature'])}
if os.path.isfile('{config['project_name']}_md.traj') == False:
    MaxwellBoltzmannDistribution(atoms, temperature_K = temperature_K)


# Thermostat and/or barostat
{dict_thermostat['dynamics']}
dyn.fixcm = True

{lines_log_file}
{lines_traj_file}

# Write the xyz trajectory
def write_xyz():
    write('{config['project_name']}_pos.xyz', atoms, format='xyz', append=True)
dyn.attach(write_xyz, interval={int(config['write_interval'])})

start_time = time.time()
dyn.run({int(config['nsteps'])})
end_time = time.time()

# Calculate the runtime
runtime = end_time - start_time
print("Function runtime: "+ str(runtime) + " seconds")
np.savetxt("md_runtime.txt", [runtime])

# Write the final coordinates
write('{config['project_name']}_restart.traj', atoms) 
""" + self._footer()
    
    def generate_recalc_input(self) -> str:
        """
        Generate recalculation input.
        """
        config = self.config
        dict_foundation_model = self._get_model_code()

        return f"""import time
import numpy as np
from ase import units
from ase.io.trajectory import Trajectory
from ase.io import read, write
{dict_foundation_model['import']}

# Load the MLIP model
mlip_calc = {dict_foundation_model['model']}
print("Loading of MLIP model ({self.framework}) completed: {config['foundation_model']} model")

# Load the reference trajectory
trajectory = read('{config['coord_file']}', index=':')

# Initialize a list to store forces for each frame
all_forces = []
all_energies = []
frame_counter = 0

# Loop over each frame and calculate forces
for atoms in trajectory:
    if frame_counter % 25 == 0:
        print(frame_counter)
    frame_counter += 1
    atoms.pbc = (True, True, True)
    atoms.set_cell({self._get_cell_matrix_code()})
    atoms.calc = mlip_calc
    forces = atoms.get_forces()
    all_forces.append(forces)
    energies = atoms.get_total_energy()
    all_energies.append(energies)

# Saving the energies and forces to files
all_forces = np.array(all_forces)
np.savetxt("ener_recalc_mlip_{config['project_name']}", all_energies)
atom = trajectory[0].get_chemical_symbols()
atom = np.array(atom)
with open('frc_recalc_mlip_{config['project_name']}.xyz', 'w') as f: """+r"""
    for i in range(0, all_forces.shape[0]):
        f.write(f"{len(atom)} \n")
        f.write(f"# Frame {i}\n")
        for j in range(0, len(atom)):
            f.write('%s %f %f %f \n' % (atom[j], all_forces[i][j][0], all_forces[i][j][1], all_forces[i][j][2]))
""" + self._footer()
    
class MLIPFrameworkHandler:
    """
    Class to handle different MLIP frameworks.
    """
    
    def __init__(self, framework: str, config: Dict[str, Any]):
        self.framework = framework
        self.config = config

        if framework == 'mace':
            self.model_code = self._mace_model_code
        elif framework == 'mattersim':
            self.model_code = self._mattersim_model_code
        elif framework == 'sevennet':
            self.model_code = self._sevennet_model_code
        elif framework == 'orb':
            self.model_code = self._orb_model_code
        elif framework == 'grace':
            self.model_code = self._grace_model_code

    def _check_cuequivariance(self) -> bool:
        """
        Check if cuequivariance is installed.
        """
        try:
            import cuequivariance
            return True
        except ImportError:
            return False

    def _mace_model_code(self, foundation_model: str, model_size: Optional[str], dispersion: str) -> str:
        """
        Generate MACE model code.
        """
        # Check if cuequivariance is installed
        if self._check_cuequivariance():
            cuequivariance = ", enable_cueq = True"
        else:
            cuequivariance = ", enable_cueq = False"

        # Check if dispersion is enabled
        if dispersion == 'y':
            dispersion = ", dispersion = True"
        else:
            dispersion = ", dispersion = False"

        if model_size:
            # Foundation model
            if foundation_model == 'mace_mp':
                return {
                    'import': 'from mace.calculators import mace_mp',
                    'model': f"mace_mp(model='{model_size}' {dispersion} {cuequivariance})"
                }
            elif foundation_model == 'mace_omol':
                model_size = model_size.replace('-', '_')
                return {
                    'import': 'from mace.calculators import mace_omol',
                    'model': f"mace_omol(model='{model_size}' {dispersion} {cuequivariance})"
                }
            elif foundation_model == 'mace_off':
                return {
                    'import': 'from mace.calculators import mace_off',
                    'model': f"mace_off(model='{model_size}' {dispersion} {cuequivariance})"
                }
            elif foundation_model == 'mace_anicc':
                return {
                    'import': 'from mace.calculators import mace_anicc',
                    'model': f"mace_anicc({dispersion[1:]} {cuequivariance})"
                }
        else:
            # Custom model: Assuming that a mace_mp model was fine-tuned
            return {
                'import': 'from mace.calculators import mace_mp',
                'model': f"mace_mp(model='{foundation_model}' {dispersion} {cuequivariance})"
            }

    def _mattersim_model_code(self, foundation_model: str, dispersion: str) -> str:
        """
        Generate Mattersim model code.
        """
        # No possibility to include dispersion into the Calculator

        if foundation_model == 'small':
            return {
                'import': """from mattersim.forcefield import MatterSimCalculator
import torch
device = "cuda" if torch.cuda.is_available() else "cpu" """,
                'model': f"MatterSimCalculator(load_path='MatterSim-v1.0.0-1M.pth', device=device)"
            }
        elif foundation_model == 'large':
            return {
                'import': """from mattersim.forcefield import MatterSimCalculator
import torch
device = "cuda" if torch.cuda.is_available() else "cpu" """,
                'model': f"MatterSimCalculator(load_path='MatterSim-v1.0.0-5M.pth', device=device)"
            }
        else:
            # Fine-tuned model
            return {
                'import': """from mattersim.forcefield import MatterSimCalculator
import torch
device = "cuda" if torch.cuda.is_available() else "cpu" """,
                'model': f"MatterSimCalculator(load_path='{foundation_model}', device=device)"
            }

    def _sevennet_model_code(self, foundation_model: str, modal: Optional[str], dispersion: str) -> Dict[str, str]:
        """
        Generate SevenNet model code.
        """
        if dispersion == 'y':
            calc = 'SevenNetD3Calculator'
        else:
            calc = 'SevenNetCalculator'

        if modal is not None:
            return {
                'import': f'from sevenn.calculator import {calc}',
                'model': f"{calc}(model='{foundation_model}', modal='{modal}')"
            }
        elif modal is None:
            return {
                'import': f'from sevenn.calculator import {calc}',
                'model': f"{calc}(model='{foundation_model}')"
            }
        else:
            # Fine-tuned model
            return {
                'import': f'from sevenn.calculator import {calc}',
                'model': f"{calc}(model='{foundation_model}')"
            }
        
    def _orb_model_code(self, foundation_model: str, modal: Optional[str], dispersion: str) -> Dict[str, str]:
        """
        Generate ORB model code.
        """

        if modal is not None:
            # v3 Model
            return {
                'import': f"""from orb_models.forcefield import pretrained
from orb_models.forcefield.calculator import ORBCalculator
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
orbff = pretrained.{foundation_model}_{modal}(
  device=device,
  precision="float32-high",
)
                """,
                'model': "ORBCalculator(orbff, device=device)"
            }
        elif foundation_model not in ['orb_v2', 'orb_v3_conservative_inf']:
            # Custom model
            return {
                'import': f"""from orb_models.forcefield import pretrained
from orb_models.forcefield.calculator import ORBCalculator
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
base_model = 'orb_v2' # or 'orb_v3_conservative_inf_omat'
model = getattr(pretrained, base_model)(
  weights_path='{foundation_model}', 
  device=device,
  precision="float32-high",
)
                """,
                'model': "ORBCalculator(model, device=device)"
            }
        else:
            # v2 Model
            foundation_model_disp = 'orb_v2' if dispersion == 'n' else 'orb_d3_v2'
            return {
                'import': f"""from orb_models.forcefield import pretrained
from orb_models.forcefield.calculator import ORBCalculator
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
orbff = pretrained.{foundation_model_disp}(
  device=device,
  precision="float32-high",
)
                """,
                'model': "ORBCalculator(orbff, device=device)"
            }

    def _grace_model_code(self, foundation_model: str) -> Dict[str, str]:
        """
        Generate GRACE model code.
        """
        if foundation_model in ['GRACE-1L-OMAT', 'GRACE-2L-OMAT', 'GRACE-1L-OAM', 'GRACE-2L-OAM']:
            # Foundation model
            return {
                'import': 'from tensorpotential.calculator import grace_fm',
                'model': f"grace_fm('{foundation_model}')"
            }
        else:
            # Custom model
            return {
                'import': 'from tensorpotential.calculator import TPCalculator',
                'model': f"TPCalculator(model='{foundation_model}')"
            }


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
#     generator = ASEInputGeneratorWrapper(run_type, framework, config['MD'])
#     #generator.run_and_save()
#     print("Input file generation completed.")