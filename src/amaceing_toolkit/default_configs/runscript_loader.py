import os
import numpy as np

class RunscriptLoader:
    """
    Class to parse the runscript content based on the used framework.
    """

    def __init__(self, framework, project_name, input_file, sim_env='py', device='cpu', ft_string=None):
        self.framework = framework
        self.project_name = project_name
        self.input_file = input_file
        self.sim_env = sim_env
        self.device = device
        self.ft_string = ft_string

    def _first_hit(self):
        """
        Search for the hpc_setup_path.txt file. If it exists parse the path. Instead of the non-existence of the file enter the Q&A session of the HPC setup.
        """
        script_directory = os.path.dirname(os.path.abspath(__file__))
        hpc_setup_path_file = os.path.join(script_directory, 'hpc_setup_path.txt')
        if os.path.exists(hpc_setup_path_file):
            with open(hpc_setup_path_file, 'r') as f:
                hpc_setup_path = f.read().strip()
        else:
            print("HPC setting not set. Starting Q&A session to setup the runscript configurator.")
            hpc_setup_path = self._qa_session(self.framework, self.sim_env, self.device)
        return hpc_setup_path

    def _qa_session(self, framework, sim_env, device):
        """
        Q&A session to get the create the runscripts.
        """
        use_runscript_generator = ask_for_yes_no("Do want to get runscript prepared for every toolkit run?", 'y')
        if use_runscript_generator == 'n':
            print("Runscript generation is disabled.")
            script_directory = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(script_directory, 'hpc_setup_path.txt'), 'w') as f:
                f.write('NO_RUNSCRIPT_GENERATION')

        use_predefined_rs = ask_for_yes_no("Do you want to use predefined runscript for the HPC at TU Ilmenau?", 'y')
        if use_predefined_rs == 'y':
            print("Using predefined runscript templates for TU Ilmenau.")
            runscripts = TUIlmenauRunscriptTemplates()
            hpc_setup_path = runscripts.write_runscript()

        else:
            print("Creating a custom runscript template for you to edit.")
            custom_runscript_creator = CustomRunscriptCreator()
            hpc_setup_path = custom_runscript_creator.create_runscript()
        
        return hpc_setup_path

    def load_runscript(self):
        """
        Load the runscript based on the provided configuration.
        """
        hpc_setup_path = self._first_hit()

        if hpc_setup_path == 'NO_RUNSCRIPT_GENERATION':
            return "0"

        # Load the runscript based on the framework, simulation environment, and device
        if self.framework == 'cp2k':
            script_name = 'cp2k'
        elif self.framework == 'cp2k_local':
            script_name = 'cp2k_local'
        elif np.logical_and(self.ft_string is not None, self.framework == 'mattersim'):
            script_name = f"mattersim_ft_gpu"
        elif self.framework == 'grace_ft':
            script_name = f"grace_ft_gpu"
        else:
            script_name = f"{self.framework}_{self.sim_env}_{self.device}"
        script_path = os.path.join(hpc_setup_path, script_name)

        if not os.path.exists(script_path):
            print(f"Runscript {script_name} does not exist in {hpc_setup_path}.")
            return

        with open(script_path, 'r') as file:
            runscript_content = file.read()
        
        # Set $$PROJECT_NAME$$ AND $$INPUT_FILE$$ placeholders
        try: 
            runscript_content = runscript_content.replace("$$PROJECT_NAME$$", self.project_name)
        except TypeError:
            pass
        try:
            runscript_content = runscript_content.replace("$$INPUT_FILE$$", self.input_file)
        except TypeError:
            pass # MatterSim FT has no input file 

        if self.ft_string is not None:
            runscript_content = runscript_content.replace("$$FINETUNE_CONFIG$$", self.ft_string)

        return runscript_content


def ask_for_yes_no(question, default):
    """
    Ask user for a yes or no answer
    """
    value = ' '
    while value != 'y' and value != 'n':
        value = input(question + " [" + default + "]: ")
        if value == '':
            value = default
        elif value != 'y' and value != 'n':
            print("Invalid input. Please enter 'y' or 'n'.")
    return value

class TUIlmenauRunscriptTemplates:
    """
    Class to create a runscripts for TU Ilmenau (LSF).
    """
    def __init__(self):
        """
        Initialize the runscripts creator.
        """
        self.config = {}

    def _ask_for_conda_folder(self):
        """
        Ask for the conda folder.
        """
        while True:
            conda_folder = input("Please enter the path to your conda environment folder (/path_to_conda_installation/etc/profile.d/conda.sh): ")
            if not os.path.exists(conda_folder):
                print(f"The provided conda folder does not exist: {conda_folder}")
            else:
                return conda_folder

    def _ask_for_env_names(self):
        """
        Ask for the different environment names.
        """
        
        default_envs = {
            'mace': 'atk',
            'mattersim': 'atk_ms7n',
            'sevennet': 'atk_ms7n',
            'orb': 'atk_orb',
            'grace': 'atk_grace'
        }

        print("Default environment names:")
        for key, value in default_envs.items():
            print(f"{key}: {value}")
        use_defaults = ask_for_yes_no("Do you want to use the default environment names?", 'y')

        if use_defaults == 'y':
            return {
                'mace': default_envs['mace'],
                'mattersim': default_envs['mattersim'],
                'sevennet': default_envs['sevennet'],
                'orb': default_envs['orb'], 
                'grace': default_envs['grace']
            }
        else:
            mace_env = input(f"Enter the name of the MACE environment (default: {default_envs['mace']}): ") or default_envs['mace']
            mattersim_env = input(f"Enter the name of the MatterSim/SevenNet environment (default: {default_envs['mattersim']}): ") or default_envs['mattersim']
            sevennet_env = mattersim_env # Can be installed in the same environment as MatterSim
            orb_env = mace_env # Can be installed in the same environment as MACE
            grace_env = input(f"Enter the name of the GRACE environment (default: {default_envs['grace']}): ") or default_envs['grace']
            return {
                'mace': mace_env,
                'mattersim': mattersim_env,
                'sevennet': sevennet_env,
                'orb': orb_env,
                'grace': grace_env
            }
        
    
    def create_runscript(self):
        """
        Create a runscripts based on the provided configuration.
        """
        
        conda_path = self._ask_for_conda_folder()
        env_names = self._ask_for_env_names()

        #####################
        ## CP2K RUNSCRIPTS ##
        #####################

        cp2k = f"""#!/bin/sh
#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 32
#BSUB -R "span[hosts=1]"
export OMP_NUM_THREADS=1
""" + r"""
if [ ! -f ./seq ];  then echo "01" > seq ; fi
export seq=`cat seq`
awk 'BEGIN{printf "%2.2d\n",ENVIRON["seq"]+1}' > seq
""" + f"""
# Check if -1.restart exists:
if [ -f $$PROJECT_NAME$$-1.restart ]; then
    INFILE=$$PROJECT_NAME$$-1.restart
else 
    INFILE=$$INPUT_FILE$$
fi

""" + """
OUTFILE=local-${INFILE}.${seq}.out
""" + f"""
source /home/joha4087/programs/cp2k_easy/source_cp2k_gcc_openmpi_by_jonas
mpirun -np 32 /home/joha4087/programs/cp2k_easy/cp2k-2025.1/exe/local/cp2k.popt $INFILE > $OUTFILE
"""

        cp2k_local = f"""source /home/joha4087/programs/cp2k_easy/source_cp2k_gcc_openmpi_by_jonas
mpirun -np 4 /home/joha4087/programs/cp2k_easy/cp2k-2025.1/exe/local/cp2k.popt
"""

        #####################
        ## MACE RUNSCRIPTS ##
        #####################

        mace_py_gpu = f"""#!/bin/sh
# GPU runscript

source {conda_path}
conda activate {env_names['mace']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mace_py_cpu = f"""#!/bin/sh
# CPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 4
#BSUB -R "span[hosts=1]"

source {conda_path}
conda activate {env_names['mace']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mace_lmp_gpu = """#!/bin/sh

INFILE=$$INPUT_FILE$$
OUTFILE=local-${INFILE}.out

source /scratch/joha4087/programs/lammps/lammps_7net_gpunodes/source_lammps7net
module load intel/oneapi/mkl
module load cuda/v12.2

export OMP_NUM_THREADS=4

# GPU LAMMPS with KOKKOS
mpirun -np 1 /scratch/joha4087/programs/lammps/lammps_mace_gpunodes/lammps/build-batchgpu/lmp -k on g 1 -sf kk -in $INFILE > $OUTFILE
"""
        mace_lmp_cpu = r"""#!/bin/sh
#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 16
#BSUB -R "span[hosts=1]"

INFILE=$$INPUT_FILE$$
OUTFILE=local-${INFILE}.out

source /home/joha4087/programs/cp2k_easy/source_cp2k_gcc_openmpi_by_jonas
module load intel/oneapi/mkl

# DEFINE THE NUMBER OF CORES
export OMP_NUM_THREADS=16

# CPU LAMMPS
/home/chdr3860/programs/lammps_mace_cpu/lammps/build/lmp -in $INFILE > $OUTFILE
"""

        ##########################
        ## MATTERSIM RUNSCRIPTS ##
        ##########################

        mattersim_py_gpu = f"""#!/bin/sh
# GPU runscript

source {conda_path}
conda activate {env_names['mattersim']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mattersim_py_cpu = f"""#!/bin/sh
# CPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 4
#BSUB -R "span[hosts=1]"

source {conda_path}
conda activate {env_names['mattersim']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""

        mattersim_ft_train_file_path = conda_path.replace('/etc/profile.d/conda.sh', f"/envs/{env_names['mattersim']}/lib/python3.9/site-packages/mattersim/training/finetune_mattersim.py")
        mattersim_ft_gpu = f"""#!/bin/bash
# GPU runscript

source {conda_path}
conda activate {env_names['mattersim']}

torchrun --nproc_per_node=1 {mattersim_ft_train_file_path} $$FINETUNE_CONFIG$$ > $$PROJECT_NAME$$.out
"""
        
        #########################
        ## SEVENNET RUNSCRIPTS ##
        #########################

        sevennet_py_gpu = mattersim_py_gpu

        sevennet_py_cpu = mattersim_py_cpu

        sevennet_lmp_gpu = """#!/bin/sh
# GPU runscript

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

# Load GCC, CUDA and MKL
source /scratch/joha4087/programs/lammps/lammps_7net_gpunodes/source_lammps7net
module load intel/oneapi/mkl
module load cuda/v12.2

export OMP_NUM_THREADS=4

mpirun -np 1 /scratch/joha4087/programs/lammps/lammps_7net_gpunodes/lammps_sevenn/build_a100/lmp -in $INFILE > $OUTFILE
"""
        sevennet_lmp_cpu = f"""#!/bin/sh
#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 16
#BSUB -R "span[hosts=1]"

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

source /home/joha4087/programs/cp2k_easy/source_cp2k_gcc_openmpi_by_jonas
module load intel/oneapi/mkl

export OMP_NUM_THREADS=16

/home/chdr3860/programs/lammps_mace_cpu/lammps/build/lmp -in $INFILE > $OUTFILE """
        
        ####################
        ## ORB RUNSCRIPTS ##
        ####################

        orb_py_gpu = f"""#!/bin/sh
# GPU runscript

source {conda_path}
conda activate {env_names['orb']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        orb_py_cpu = f"""#!/bin/sh
# CPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 4
#BSUB -R "span[hosts=1]"

source {conda_path}
conda activate {env_names['orb']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""

        ######################
        ## GRACE RUNSCRIPTS ##
        ######################

        grace_py_gpu = f"""#!/bin/sh
# GPU runscript

source {conda_path}
conda activate {env_names['grace']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        grace_py_cpu = f"""#!/bin/sh
# CPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 4
#BSUB -R "span[hosts=1]"

source {conda_path}
conda activate {env_names['grace']}

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        grace_lmp_gpu = f"""#!/bin/sh
# GPU runscript
INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

source {conda_path}
conda activate {env_names['grace']}

source /scratch/joha4087/programs/lammps/lammps_7net_gpunodes/source_lammps7net
module load intel/oneapi/mkl
module load cuda/v12.2

export OMP_NUM_THREADS=4

mpirun -np 1 /scratch/joha4087/programs/lammps/lammps_grace/lammps/build_a100/lmp -in $INFILE > $OUTFILE
"""
        grace_lmp_cpu = r"""#!/bin/sh
#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 16
#BSUB -R "span[hosts=1]"

INFILE=$$INPUT_FILE$$
OUTFILE=local-${INFILE}.out

source /home/joha4087/programs/cp2k_easy/source_cp2k_gcc_openmpi_by_jonas
module load intel/oneapi/mkl

# DEFINE THE NUMBER OF CORES
export OMP_NUM_THREADS=16

# CPU LAMMPS
/home/chdr3860/programs/lammps_mace_cpu/lammps/build/lmp -in $INFILE > $OUTFILE
"""
        grace_ft_gpu = f"""#!/bin/bash
# GPU runscript
source {conda_path}
conda activate {env_names['grace']}

gracemaker $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""

        return [mace_py_gpu, mace_py_cpu, mace_lmp_gpu, mace_lmp_cpu, mattersim_ft_gpu, mattersim_py_gpu, mattersim_py_cpu, sevennet_py_gpu, sevennet_py_cpu, sevennet_lmp_gpu, sevennet_lmp_cpu, cp2k, cp2k_local, orb_py_gpu, orb_py_cpu, grace_py_gpu, grace_py_cpu, grace_lmp_gpu, grace_lmp_cpu, grace_ft_gpu]

    def write_runscript(self):
        """
        Write the runscript to the specified file inside a 'runscript_templates' directory.
        """
        # Create new directory inside the current directory: runscript_templates
        script_directory = os.path.dirname(os.path.abspath(__file__))
        templates_directory = os.path.join(script_directory, "runscript_templates")
        os.makedirs(templates_directory, exist_ok=True)
        filenames = ['mace_py_gpu', 'mace_py_cpu', 'mace_lmp_gpu', 'mace_lmp_cpu', 'mattersim_ft_gpu', 'mattersim_py_gpu', 'mattersim_py_cpu', 'sevennet_py_gpu', 'sevennet_py_cpu', 'sevennet_lmp_gpu', 'sevennet_lmp_cpu', 'cp2k', 'cp2k_local', 'orb_py_gpu', 'orb_py_cpu', 'grace_py_gpu', 'grace_py_cpu', 'grace_lmp_gpu', 'grace_lmp_cpu', 'grace_ft_gpu']
        runscript_templates = self.create_runscript()
        for i, template in enumerate(runscript_templates):
            file_name = filenames[i]
            file_path = os.path.join(templates_directory, file_name)
            with open(file_path, 'w') as file:
                file.write(template)
        
        # Save the path to the runscript templates directory in the config
        with open(os.path.join(script_directory, 'hpc_setup_path.txt'), 'w') as f:
            f.write(templates_directory)

        return templates_directory


class CustomRunscriptCreator:
    """
    Just create the template runscript for the user: LSF or Slurm.
    """

    def __init__(self, config):
        self.config = config

    def _ask_for_workload_manager(self):
        """
        Ask the user for the workload manager they are using.
        """
        
        choice = input("Please select your workload manager (1: LSF or 2: Slurm): ")
        
        if choice == '1':
            return 'lsf'
        elif choice == '2':
            return 'slurm'
        else:
            print("Invalid choice. Please enter 1 or 2.")
            return self._ask_for_workload_manager()
        
    def _lsf_templates(self):
        """
        Return the LSF templates.
        """
        #####################
        ## CP2K RUNSCRIPTS ##
        #####################

        cp2k = f"""#!/bin/sh
#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 32
#BSUB -R "span[hosts=1]"
export OMP_NUM_THREADS=1
""" + r"""
if [ ! -f ./seq ];  then echo "01" > seq ; fi
export seq=`cat seq`
awk 'BEGIN{printf "%2.2d\n",ENVIRON["seq"]+1}' > seq
""" + f"""
# Check if -1.restart exists:
if [ -f $$PROJECT_NAME$$-1.restart ]; then
    INFILE=$$PROJECT_NAME$$-1.restart
else 
    INFILE=$$INPUT_FILE$$
fi

""" + """
OUTFILE=local-${INFILE}.${seq}.out
""" + r"""
{SOURCE GCC, OMP AND CP2K}             # Replace with the source command for your CP2K environment
mpirun -np 32 {PATH TO CP2K EXECUTABLE}/cp2k.popt $INFILE > $OUTFILE    # Replace with the path to your CP2K executable
"""

        cp2k_local = f"""source GCC_OMP_CP2K
mpirun -np 4 /path_to_executable/cp2k.popt
"""
        
        #####################
        ## MACE RUNSCRIPTS ##
        #####################

        mace_py_gpu = r"""#!/bin/sh
# GPU runscript

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MACE

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mace_py_cpu = r"""#!/bin/sh
# CPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -W {hh:mm}                            # Replace with your desired wall time      
#BSUB -q {PARTITION NAME}                   # Replace with your partition name
#BSUB -n {NUMBER OF CORES}                  # Replace with the number of cores you want to use

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MACE

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mace_lmp_gpu = r"""#!/bin/sh

INFILE=$$INPUT_FILE$$
OUTFILE=local-${INFILE}.out

{SOURCE GCC, OMP, CUDA AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=4

# GPU LAMMPS with KOKKOS
mpirun -np 1 {PATH TO LAMMPS EXECUTABLE}/lmp -k on g 1 -sf kk -in $INFILE > $OUTFILE    # Replace with the path to your LAMMPS executable
"""
        mace_lmp_cpu = r"""#!/bin/sh
# CPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -W {hh:mm}                            # Replace with your desired wall time      
#BSUB -q {PARTITION NAME}                   # Replace with your partition name
#BSUB -n {NUMBER OF CORES}                  # Replace with the number of cores you want to use

INFILE=$$INPUT_FILE$$
OUTFILE=local-${INFILE}.out

{SOURCE GCC, OMP and MKL}                   # Replace with the source command for your LAMMPS environment

# DEFINE THE NUMBER OF CORES
export OMP_NUM_THREADS={NUMBER OF CORES}    # Replace with the number of cores you want to use

# CPU LAMMPS
{PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE      # Replace with the path to your LAMMPS executable
"""

        ##########################
        ## MATTERSIM RUNSCRIPTS ##
        ##########################

        mattersim_py_gpu = r"""#!/bin/sh
# GPU runscript

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MatterSim

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mattersim_py_cpu = r"""#!/bin/sh
# CPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -W {hh:mm}                            # Replace with your desired wall time      
#BSUB -q {PARTITION NAME}                   # Replace with your partition name
#BSUB -n {NUMBER OF CORES}                  # Replace with the number of cores you want to use

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MatterSim
"""
        mattersim_ft_gpu = r"""#!/bin/bash
# GPU runscript

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MatterSim


torchrun --nproc_per_node=1 /{PATH TO CONDA}/lib/python3.{X}/site-packages/mattersim/training/finetune_mattersim.py $$FINETUNE_CONFIG$$ > $$PROJECT_NAME$$.out
"""

        #########################
        ## SEVENNET RUNSCRIPTS ##
        #########################

        sevennet_py_gpu = mattersim_py_gpu

        sevennet_py_cpu = mattersim_py_cpu

        sevennet_lmp_gpu = r"""#!/bin/sh
# GPU runscript

#BSUB -J $$PROJECT_NAME$$
#BSUB -W {hh:mm}                            # Replace with your desired wall time      
#BSUB -q {PARTITION NAME}                   # Replace with your partition name
#BSUB -n {NUMBER OF CORES}                  # Replace with the number of cores you want to use

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

{SOURCE GCC, OMP, CUDA AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=4

mpirun -np 1 {PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE    # Replace with the path to your LAMMPS executable
"""
        sevennet_lmp_cpu = r"""#!/bin/sh
#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 16
#BSUB -R "span[hosts=1]"

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

{SOURCE GCC, OMP AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=16

{PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE """

        ####################
        ## ORB RUNSCRIPTS ##
        ####################

        orb_py_gpu = mace_py_gpu
        orb_py_cpu = mace_py_cpu
    
        ######################
        ## GRACE RUNSCRIPTS ##
        ######################
        grace_py_gpu = mace_py_gpu
        grace_py_cpu = mace_py_cpu
        grace_lmp_gpu = r"""#!/bin/sh
# GPU runscript
#BSUB -J $$PROJECT_NAME$$
#BSUB -W {hh:mm}                            # Replace with your desired wall time      
#BSUB -q {PARTITION NAME}                   # Replace with your partition name
#BSUB -n {NUMBER OF CORES}                  # Replace with the number of cores you want to use

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for Grace

{SOURCE GCC, OMP, CUDA AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=4

mpirun -np 1 {PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE    # Replace with the path to your LAMMPS executable
"""
        grace_lmp_cpu = r"""#!/bin/sh
# CPU runscript
#BSUB -J $$PROJECT_NAME$$
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -W 120:00
#BSUB -q BatchXL
#BSUB -n 16
#BSUB -R "span[hosts=1]"
INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out
source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for Grace
{SOURCE GCC, OMP AND MKL}             # Replace with the source command for your LAMMPS environment
export OMP_NUM_THREADS=16
{PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE      # Replace with the path to your LAMMPS executable
"""
        grace_ft_gpu = r"""#!/bin/bash
# GPU runscript
#BSUB -J $$PROJECT_NAME$$
#BSUB -W {hh:mm}                            # Replace with your desired wall time      
#BSUB -q {PARTITION NAME}                   # Replace with your partition name
#BSUB -n {NUMBER OF CORES}                  # Replace with the number of cores you want to use

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for Grace

gracemaker $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""


        return [mace_py_gpu, mace_py_cpu, mace_lmp_gpu, mace_lmp_cpu, mattersim_ft_gpu, mattersim_py_gpu, mattersim_py_cpu, sevennet_py_gpu, sevennet_py_cpu, sevennet_lmp_gpu, sevennet_lmp_cpu, cp2k, orb_py_gpu, orb_py_cpu, grace_py_gpu, grace_py_cpu, grace_lmp_gpu, grace_lmp_cpu, grace_ft_gpu] 


    def _slurm_templates(self):
        """
        Return the Slurm templates.
        """
        #####################
        ## CP2K RUNSCRIPTS ##
        #####################

        cp2k = r"""#SBATCH --job-name $$PROJECT_NAME$$
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name
export OMP_NUM_THREADS=1
""" + r"""
if [ ! -f ./seq ];  then echo "01" > seq ; fi
export seq=`cat seq`
awk 'BEGIN{printf "%2.2d\n",ENVIRON["seq"]+1}' > seq
""" + f"""
# Check if -1.restart exists:
if [ -f $$PROJECT_NAME$$-1.restart ]; then
    INFILE=$$PROJECT_NAME$$-1.restart
else 
    INFILE=$$INPUT_FILE$$
fi

""" + """
OUTFILE=local-${INFILE}.${seq}.out
""" + r"""
{SOURCE GCC, OMP AND CP2K}             # Replace with the source command for your CP2K environment
mpirun -np 32 {PATH TO CP2K EXECUTABLE}/cp2k.popt $INFILE > $OUTFILE    # Replace with the path to your CP2K executable
"""
        cp2k_local = ['source GCC_OMP/CP2K', 'mpirun -np 4 /path_to_executable/cp2k.popt']

        #####################
        ## MACE RUNSCRIPTS ##
        #####################

        mace_py_gpu = r"""#GPU runscript

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MACE

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mace_py_cpu = r"""#SBATCH --job-name $$PROJECT_NAME$$
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MACE

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mace_lmp_gpu = r"""#GPU runscript

INFILE=$$INPUT_FILE$$
OUTFILE=local-${INFILE}.out

{SOURCE GCC, OMP, CUDA AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=4

# GPU LAMMPS with KOKKOS
mpirun -np 1 {PATH TO LAMMPS EXECUTABLE}/lmp -k on g 1 -sf kk -in $INFILE > $OUTFILE    # Replace with the path to your LAMMPS executable
"""
        mace_lmp_cpu = r"""#SBATCH --job-name $$PROJECT_NAME$$
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name

INFILE=$$INPUT_FILE$$
OUTFILE=local-${INFILE}.out

{SOURCE GCC, OMP and MKL}                   # Replace with the source command for your LAMMPS environment

# DEFINE THE NUMBER OF CORES
export OMP_NUM_THREADS={NUMBER OF CORES}    # Replace with the number of cores you want to use

# CPU LAMMPS
{PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE      # Replace with the path to your LAMMPS executable
"""

        ##########################
        ## MATTERSIM RUNSCRIPTS ##
        ##########################

        mattersim_py_gpu = r"""# GPU runscript

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MatterSim

python $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        mattersim_py_cpu = r"""#SBATCH --job-name $$PROJECT_NAME$$
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MatterSim
"""
        mattersim_ft_gpu = r"""#!/bin/bash
# GPU runscript

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for MatterSim


torchrun --nproc_per_node=1 /{PATH TO CONDA}/lib/python3.{X}/site-packages/mattersim/training/finetune_mattersim.py $$FINETUNE_CONFIG$$ > $$PROJECT_NAME$$.out
"""

        #########################
        ## SEVENNET RUNSCRIPTS ##
        #########################

        sevennet_py_gpu = mattersim_py_gpu

        sevennet_py_cpu = mattersim_py_cpu

        sevennet_lmp_gpu = """# GPU runscript

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

{SOURCE GCC, OMP, CUDA AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=4

mpirun -np 1 {PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE    # Replace with the path to your LAMMPS executable
"""
        sevennet_lmp_cpu = r"""#SBATCH --job-name $$PROJECT_NAME$$
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

{SOURCE GCC, OMP AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=16

{PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE """

        ####################
        ## ORB RUNSCRIPTS ##
        ####################

        orb_py_gpu = mace_py_gpu
        orb_py_cpu = mace_py_cpu

        ######################
        ## GRACE RUNSCRIPTS ##
        ######################
        grace_py_gpu = mace_py_gpu
        grace_py_cpu = mace_py_cpu
        grace_lmp_gpu = r"""#!/bin/sh
# GPU runscript
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name

INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for Grace

{SOURCE GCC, OMP, CUDA AND MKL}             # Replace with the source command for your LAMMPS environment

export OMP_NUM_THREADS=4

mpirun -np 1 {PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE    # Replace with the path to your LAMMPS executable
"""
        grace_lmp_cpu = r"""#!/bin/sh
# CPU runscript
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name
INFILE=$$INPUT_FILE$$
OUTFILE=$$PROJECT_NAME$$.out
source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for Grace
{SOURCE GCC, OMP AND MKL}             # Replace with the source command for your LAMMPS environment
export OMP_NUM_THREADS=16
{PATH TO LAMMPS EXECUTABLE}/lmp -in $INFILE > $OUTFILE      # Replace with the path to your LAMMPS executable
"""
        grace_ft_gpu = r"""#!/bin/bash
# GPU runscript
#SBATCH --output output.log                 
#SBATCH --nodes 1
#SBATCH --ntasks-per-node {NUMBER OF CORES}            # Replace with the number of cores you want to use
#SBATCH --time {hh:mm}                                 # Replace with your desired wall time
#SBATCH --partition {PARTITION NAME}                   # Replace with your partition name

source {PATH TO CONDA.SH}                   # Replace with the path to your conda.sh file
conda activate {CONDA ENVIRONMENT NAME}     # Replace with the name of your conda environment for Grace

gracemaker $$INPUT_FILE$$ > $$PROJECT_NAME$$.out
"""
        


        return [mace_py_gpu, mace_py_cpu, mace_lmp_gpu, mace_lmp_cpu, mattersim_ft_gpu, mattersim_py_gpu, mattersim_py_cpu, sevennet_py_gpu, sevennet_py_cpu, sevennet_lmp_gpu, sevennet_lmp_cpu, cp2k, cp2k_local, orb_py_gpu, orb_py_cpu, grace_py_gpu, grace_py_cpu, grace_lmp_gpu, grace_lmp_cpu, grace_ft_gpu]

    def create_runscript(self):
        """
        Create a custom runscript for further refinement by the user.
        """
        print("Creating a custom runscript template for you to edit.")
        workload_manager = self._ask_for_workload_manager()
        directory_path = input("Please enter the path where you want to save the runscript template: ")
        directory_path = os.path.join(directory_path, "runscript_templates")

        runscripts = self._lsf_templates() if workload_manager == 'lsf' else self._slurm_templates()

        os.makedirs(directory_path, exist_ok=True)
        filenames = ['mace_py_gpu', 'mace_py_cpu', 'mace_lmp_gpu', 'mace_lmp_cpu', 'mattersim_ft_gpu', 'mattersim_py_gpu', 'mattersim_py_cpu', 'sevennet_py_gpu', 'sevennet_py_cpu', 'sevennet_lmp_gpu', 'sevennet_lmp_cpu', 'cp2k', 'cp2k_local', 'orb_py_gpu', 'orb_py_cpu', 'grace_py_gpu', 'grace_py_cpu', 'grace_lmp_gpu', 'grace_lmp_cpu', 'grace_ft_gpu']
        for i, template in enumerate(runscripts):
            file_name = filenames[i]
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'w') as file:
                file.write(template + f"\n #AUTOMATICALLY GENERATED RUNSCRIPT TEMPLATE - PLEASE EDIT IT AS NEEDED (LOCATION: {file_path})\n")

        # Save the path to the runscript templates directory in the config
        script_directory = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_directory, 'hpc_setup_path.txt'), 'w') as f:
            f.write(directory_path)

        print(f"Runscript templates created in {directory_path}. Please edit them as needed but keep their names and locations.")

        return directory_path
        