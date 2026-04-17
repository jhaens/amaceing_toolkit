import datetime
import os
import numpy as np

from amaceing_toolkit.default_configs.runscript_loader import RunscriptLoader

class TrainInputGenerator:
    """Generates input configurations for training different frameworks from scratch."""
    
    def __init__(self, config, run_type, framework):
        self.config = config
        self.run_type = run_type
        self.framework = framework
        
    def _get_filename(self, run_type):
        return 'train.py', 'config_train.yaml'
        
    def _runscript_wrapper(self, device, filename, mattersim_string=None):
        """
        Generate the runscript for the input file: CPU and GPU version.
        """
        if self.framework.lower() == 'grace':
            device = 'gpu' if device == 'cuda' else 'cpu'
            # Generate the runscript content for Grace training-from-scratch (similar to finetuned one)
            runscript_content = RunscriptLoader('grace_ft', self.config['project_name'], filename, 'py', device).load_runscript()
        else:
            runscript_content = RunscriptLoader(self.framework, self.config['project_name'], filename, 'py', 'gpu', mattersim_string).load_runscript()
        rs_name = {'cpu': 'runscript.sh', 'gpu': 'gpu_script.job', 'cuda': 'gpu_script.job'}
        
        if runscript_content == '0':
            return

        # Save the runscript files
        with open(rs_name[device], 'w') as file:
            file.write(runscript_content)
        os.chmod(rs_name[device], 0o755)  # Make the script executable

        print(f"Runscript for {device} has been written to {rs_name[device]}")

    def cuequivariance_import(self):
        """Check if the cuequivariance package is installed."""
        try:
            import cuequivariance
            return True
        except ImportError:
            return False

    def _is_cuequivariance_installed(self):
        if self.cuequivariance_import() == False:
            return "enable_cueq: False"
        else:
            return "enable_cueq: True"
        
    def _check_extxyz_keys(self, train_file):
        """Check if the keys in the extxyz file match the expected keys."""
        expected_keys = {
            'energy_key': ['REF_TotEnergy', 'REF_Energy', 'REF_TotEner', 'REF_Ener', 'ref_TotEnergy', 'ref_Energy', 'ref_TotEner', 'ref_Ener', 'TotEnergy', 'Energy', 'TotEner', 'Ener', 'totenergy', 'energy', 'totener', 'ener', 'REF_TotEnergies', 'REF_Energies', 'TotEnergies', 'Energies','totenergies', 'energies', 'free_energy', 'free_energies', 'REF_FreeEnergy', 'REF_FreeEnergies', 'ref_FreeEnergy', 'ref_FreeEnergies'],
            'forces_key': ['REF_Force', 'REF_Forces', 'Force', 'Forces', 'ref_force', 'ref_forces', 'force', 'forces', 'frc', 'frcs', 'REF_Frc', 'REF_Frcs', 'REF_frc', 'REF_frcs', 'ref_Frc', 'ref_Frcs', 'ref_frc', 'ref_frcs'],
            'stress_key': ['REF_Stress', 'REF_Stresses', 'stress', 'Stress', 'stresses', 'Stresses', 'ref_stress', 'ref_stresses', 'REF_stress', 'REF_stresses']
        }
        # Read the first two lines of the train file to check the keys, forget the first line
        with open(train_file, 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                raise ValueError("The train file must contain at least two lines.")
            # Split the line at spaces, '=' and ':'
            line = lines[1].strip()
            separators = [' ', '=', ':']
            keys = []
            current = ''
            for char in line:
                if char in separators:
                    if current:
                        keys.append(current)
                        current = ''
                else:
                    current += char
            if current:
                keys.append(current)

        # Check which of the expected force and energy key is present in the file
        ener_key, frc_key, stress_key = "REF_TotEnergy", "REF_Force", None
        for key in expected_keys['energy_key']:
            if key in keys:
                ener_key = key
                break
        for key in expected_keys['forces_key']:
            if key in keys:
                frc_key = key
                break
        for key in expected_keys['stress_key']:
            if key in keys:
                stress_key = key
                break
        # If no key is found, raise an error
        if ener_key not in keys:
            raise ValueError(f"Energy key '{ener_key}' not found in the train file. Expected one of: {expected_keys['energy_key']}")
        if frc_key not in keys:
            raise ValueError(f"Forces key '{frc_key}' not found in the train file. Expected one of: {expected_keys['forces_key']}")
        if stress_key != None:
            if stress_key not in keys:
                raise ValueError(f"Stress key '{stress_key}' not found in the train file. Expected one of: {expected_keys['stress_key']}")
        return [ener_key, frc_key, stress_key]

    def _write_mace_pytrain_script(self, config_filename):
        """Write the MACE training script to a Python file."""
        python_content = f"""
import warnings, sys, logging
warnings.filterwarnings("ignore")
from mace.cli.run_train import main as mace_run_train_main  
def train_mace(config_file_path):
    logging.getLogger().handlers.clear()
    sys.argv = ["program", "--config", config_file_path]
    mace_run_train_main()
train_mace("{config_filename}")
"""
        return python_content

    def mace_train(self):
        """Generate input files for MACE training-from-scratch."""
        config = self.config
        filenames = self._get_filename(self.run_type)
        keys = self._check_extxyz_keys(config['train_file'])
        stress_line = ""
        if keys[2] != None:
            stress_line = f"""stress_key: "{keys[2]}" 
loss: "universal" """

        config_content = f"""model: "MACE"
name: "{config['project_name']}"
train_file: "{config['train_file']}" 
E0s: "{config['E0s']}"
batch_size: {config['batch_size']}
max_num_epochs: {config['epochs']}
seed: {config['seed']}
lr: {config['lr']}
energy_key: "{keys[0]}"
forces_key: "{keys[1]}"
{stress_line}
stress_weight: {config['stress_weight']}
forces_weight: {config['forces_weight']}
energy_weight: {config['energy_weight']}
device: {config['device']}
{self._is_cuequivariance_installed()}
valid_fraction: {config['valid_fraction']}
valid_batch_size: {config['valid_batch_size']}
default_dtype: float32
model_dir: {config['dir']}
log_dir: {config['dir']}
results_dir: {config['dir']}
checkpoints_dir: {config['dir']}
save_all_checkpoints: False

loss: "universal"
eval_interval: 1
error_table: 'PerAtomMAE'
interaction_first: "RealAgnosticResidualInteractionBlock"
interaction: "RealAgnosticResidualInteractionBlock"
num_interactions: 2
correlation: 3
max_ell: 3
r_max: 6.0
max_L: 1
num_channels: 128
num_radial_basis: 10
MLP_irreps: "16x0e"
scaling: 'rms_forces_scaling'
num_workers: 4
weight_decay: 1e-8
ema: True
ema_decay: 0.995
scheduler_patience: 5
patience: 50
amsgrad: True
distributed: True
clip_grad: 100
keep_checkpoints: False
save_cpu: True

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        python_content = self._write_mace_pytrain_script(filenames[1])

        # Write the configuration and python content to files
        with open(filenames[0], 'w') as file:
            file.write(python_content)
        with open(filenames[1], 'w') as file:
            file.write(config_content)

        # Write runscript    
        self._runscript_wrapper(config['device'], filenames[0])

    def _write_sevennet_pytrain_script(self, train_filename):
        """Prepare the dataset for the SevenNet training."""
        python_content = f"""
# This script prepares the dataset for SevenNet training-from-scratch. Please run it before starting the training process.
import os
from sevenn.train.graph_dataset import SevenNetGraphDataset

cutoff = 5.0
working_dir = os.getcwd()
dataset = SevenNetGraphDataset(cutoff=cutoff, root=working_dir, files='{train_filename}', processed_name='graph.pt')
"""
        return python_content

    def sevennet_train(self):
        """Generate input files for SevenNet training-from-scratch."""
        
        config = self.config
        filenames = self._get_filename(self.run_type)

        keys = self._check_extxyz_keys(config['train_file'])
        if keys != ['energy', 'forces', 'stress']:
            with open(config['train_file'], 'r') as file:
                filedata = file.read()
            filedata = filedata.replace(keys[0], 'energy').replace(keys[1], 'forces')
            with open(config['train_file'], 'w') as file:
                file.write(filedata)
        
        config_content =f"""model:
    chemical_species: 'Auto'
    cutoff: 5.0
    channel: 128
    lmax: 2 
    num_convolution_layer: 5
    irreps_manual:
        - "128x0e"
        - "128x0e+64x1e+32x2e"
        - "128x0e+64x1e+32x2e"
        - "128x0e+64x1e+32x2e"
        - "128x0e+64x1e+32x2e"
        - "128x0e"

    weight_nn_hidden_neurons: [64, 64]
    radial_basis:
        radial_basis_name: 'bessel'
        bessel_basis_num: 8
    cutoff_function:
        cutoff_function_name: 'XPLOR'
        cutoff_on: 4.5
"""+r"""
    act_gate: {'e': 'silu', 'o': 'tanh'} 
    act_scalar: {'e': 'silu', 'o': 'tanh'}
"""+f"""
    is_parity: False

    self_connection_type: 'nequip'

    conv_denominator: "avg_num_neigh"
    train_denominator: False 
    train_shift_scale: False 

train:  # Customizable
    random_seed: {config['seed']}
    is_train_stress: True
    epoch: {config['epochs']}

    loss: 'Huber'
    loss_param:
        delta: 0.01

    optimizer: 'adam'
    optim_param:
        lr: {config['lr']}
    scheduler: 'exponentiallr'
    scheduler_param:
        gamma: 0.99

    force_loss_weight: {config['force_loss_ratio']}
    stress_loss_weight: 0.01

    per_epoch: 10  # Generate checkpoints every this epoch

    error_record:
        - ['Energy', 'RMSE']
        - ['Force', 'RMSE']
        - ['TotalLoss', 'None']

data:
    batch_size: {config['batch_size']}
    data_divide_ratio: 0.1

    data_format_args:
        index: ':'
    load_trainset_path: ['./sevenn_data/graph.pt']
"""
        # Write the configuration and python content to files
        python_content = self._write_sevennet_pytrain_script(config['train_file'])
        
        with open(filenames[0], 'w') as file:
            file.write(python_content)
        with open(filenames[1], 'w') as file:
            file.write(config_content)

        # Write runscript    
        self._runscript_wrapper(config['device'], filenames[0])
        # Add line to runscript
        if os.path.exists('runscript.sh'):
            with open('runscript.sh', 'a') as file:
                file.write(f"\nsevenn {filenames[1]} -s\n")
        else: 
            with open('gpu_script.job', 'a') as file:
                file.write(f"\nsevenn {filenames[1]} -s\n")

    def grace_train(self):
        """Generate input files for GRACE training-from-scratch."""
        
        config = self.config
        filenames = self._get_filename(self.run_type)

        keys = self._check_extxyz_keys(config['train_file'])
        if keys != ['energy', 'forces']:
            with open(config['train_file'], 'r') as file:
                filedata = file.read()
            filedata = filedata.replace(keys[0], 'free_energy').replace(keys[1], 'forces')
            new_filename = config['train_file'].split('/')[-1]
            config['train_file'] = new_filename.replace('.', '_modified_keys.')

            with open(config['train_file'], 'w') as file:
                file.write(filedata)

        # Create the dataframe via Grace: extxyz2df
        try:
            import tensorpotential
            os.system(f"extxyz2df {config['train_file']}")
        except ImportError:
            print(f"WARNING: The dataset {config['train_file']} could not be converted to the appropriate format (because TensorPotential is not installed)!")
            print(f"WARNING: Please do: 'extxyz2df {config['train_file']}' to convert the dataset to a dataframe format.")

        config['train_file'] = config['train_file'].replace('.xyz', '.pkl.gz')

        config_content = f"""
# Note:
# The original code for the Training-from-Scratch Python script is adapted from the 'gracemaker -t' command
seed: {config['seed']}
cutoff: 6.0

data:
  filename: "{config['train_file']}" 
  test_size: 0.05
  reference_energy: 0 """+r"""
  reference_energy: 0

potential:
  elements:
  preset: GRACE_1LAYER # LINEAR, FS, GRACE_1LAYER, GRACE_2LAYER
  kwargs: {lmax: 4, n_rad_max: 32, max_order: 4, n_mlp_dens: 12}
  scale: True """+r"""  
fit:
  loss: {
    energy: { weight: 1, type: huber , delta: 0.01 },
    forces: { weight: """+str(config['force_loss_ratio'])+""", type: huber , delta: 0.01 },
  }

  maxiter: """+str(config['epochs'])+""" # Number of epochs / iterations

  optimizer: Adam
  opt_params: {
            learning_rate: """ + str(config['lr']) + """,
            amsgrad: True,
            use_ema: True,
            ema_momentum: 0.99,
            weight_decay: null,
            clipvalue: 1.0,
        }

  # for learning-rate reduction
  learning_rate_reduction: { patience: 5, factor: 0.98, min: 5.0e-4, stop_at_min: True, resume_lr: True, }

  compute_convex_hull: False
  batch_size: """+str(config['batch_size'])+""" # Important hyperparameter for Adam and irrelevant (but must be) for L-BFGS-B
  test_batch_size: 4

  jit_compile: True
  eval_init_stats: False # to evaluate initial metrics

  train_max_n_buckets: 10 # max number of buckets (group of batches of same shape) in train set
  test_max_n_buckets: 5 # same for test

  checkpoint_freq: 2 # frequency for **REGULAR** checkpoints.
  # save_all_regular_checkpoints: True # to store ALL regular checkpoints
  progressbar: True # show batch-evaluation progress bar
  train_shuffle: True # shuffle train batches on every epoch
"""
        # Write the config content to file
        with open(filenames[1], 'w') as file:
            file.write(config_content)

        # Write runscript    
        self._runscript_wrapper('cuda', filenames[1])