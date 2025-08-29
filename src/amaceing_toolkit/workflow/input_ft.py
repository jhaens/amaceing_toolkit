import datetime
import os
import numpy as np

from amaceing_toolkit.default_configs.runscript_loader import RunscriptLoader

class FTInputGenerator:
    """Generates input configurations for different finetuning frameworks."""
    
    def __init__(self, config, run_type, framework):
        self.config = config
        self.run_type = run_type
        self.framework = framework
        
    def _get_filename(self, run_type):
        if run_type == 'FINETUNE':
            return 'finetune.py', 'config_finetune.yaml'
        elif run_type == 'FINETUNE_MULTIHEAD':
            return 'finetune_multihead.py', 'config_finetune_multihead.yaml'
        
    def _runscript_wrapper(self, device, filename, mattersim_string=None):
        """
        Generate the runscript for the input file: CPU and GPU version.
        """
        if self.framework.lower() == 'grace':
            device = 'gpu' if device == 'cuda' else 'cpu'
            # Generate the runscript content for Grace finetuning
            runscript_content = RunscriptLoader('grace_ft', self.config['project_name'], filename, 'py', device).load_runscript
        elif mattersim_string is None:
            device = 'gpu' if device == 'cuda' else 'cpu'
            # Generate the runscript content
            runscript_content = RunscriptLoader(self.framework, self.config['project_name'], filename, 'py', device).load_runscript
        else:
            runscript_content = RunscriptLoader(self.framework, self.config['project_name'], filename, 'py', 'gpu', mattersim_string).load_runscript
        rs_name = {'cpu': 'runscript.sh', 'gpu': 'gpu_script.job'}
        
        # Write the runscript files
        with open(rs_name[device], 'w') as file:
            file.write(runscript_content())
        os.chmod(rs_name[device], 0o755)  # Make the script executable

        print(f"Runscript for {device} has been written to {rs_name[device]}")

    def mace_ft(self):
        """Generate input files for MACE finetuning."""
        if self.run_type == 'FINETUNE':
            self._write_mace_ft_config(self.config)
        elif self.run_type == 'FINETUNE_MULTIHEAD':
            self._write_mace_mhft_config(self.config)
        else:
            raise ValueError(f"Unsupported run type for MACE finetuning: {self.run_type}")

    def _translate_mace_foundation_model(self, foundation_model):
        """Translate the foundation model list to a FT-config-compatible format."""
        if foundation_model[0] == 'mace_mp':
            if foundation_model[1] == 'medium-mpa-0':
                return 'mpa_medium'
            else:
                return foundation_model[1]
        elif foundation_model[0] == 'mace_off':
            return f"{foundation_model[1]}_off"
        elif foundation_model[0] == 'mp_anicc':
            return "anicc"

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
        ener_key, frc_key = "REF_TotEnergy", "REF_Force"
        for key in expected_keys['energy_key']:
            if key in keys:
                ener_key = key
                break
        for key in expected_keys['forces_key']:
            if key in keys:
                frc_key = key
                break
        # If no key is found, raise an error
        if ener_key not in keys:
            raise ValueError(f"Energy key '{ener_key}' not found in the train file. Expected one of: {expected_keys['energy_key']}")
        if frc_key not in keys:
            raise ValueError(f"Forces key '{frc_key}' not found in the train file. Expected one of: {expected_keys['forces_key']}")
        return [ener_key, frc_key]

    def _write_mace_pyft_script(self, config_filename):
        """Write the MACE finetuning script to a Python file."""
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

    def _write_mace_ft_config(self, config):
        """Write the MACE finetuning configuration to a YAML file."""
        filenames = self._get_filename(self.run_type)
        multihead_or_naive_ft = 'multiheads_finetuning: True' if config['prevent_catastrophic_forgetting'] == 'y' else 'multiheads_finetuning: False'
        keys = self._check_extxyz_keys(config['train_file'])

        config_content = f"""model: "MACE"
foundation_model: {self._translate_mace_foundation_model(config['foundation_model'])}
name: "{config['project_name']}"
train_file: "{config['train_file']}" 
E0s: "{config['E0s']}"
batch_size: {config['batch_size']}
max_num_epochs: {config['epochs']}
seed: {config['seed']}
lr: {config['lr']}
energy_key: "{keys[0]}"
forces_key: "{keys[1]}"
stress_weight: {config['stress_weight']}
forces_weight: {config['forces_weight']}
energy_weight: {config['energy_weight']}
device: {config['device']}
{multihead_or_naive_ft}
{self._is_cuequivariance_installed()}
valid_fraction: {config['valid_fraction']}
valid_batch_size: {config['valid_batch_size']}
default_dtype: float32
model_dir: {config['dir']}
log_dir: {config['dir']}
results_dir: {config['dir']}
checkpoints_dir: {config['dir']}
save_all_checkpoints: True

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        python_content = self._write_mace_pyft_script(filenames[1])

        # Write the configuration and python content to files
        with open(filenames[0], 'w') as file:
            file.write(python_content)
        with open(filenames[1], 'w') as file:
            file.write(config_content)

        # Write runscript    
        self._runscript_wrapper(config['device'], filenames[0])

    def _write_mace_mhft_heads(self, config):
        train_files = config['train_file']
        e0_dict = config['E0s']
        head_text = "heads: "
        for i in range(len(train_files)):
            keys = self._check_extxyz_keys(train_files[i])
            head_text += f"""
  head_{i}:
    train_file: "{train_files[i]}"  
    energy_key: "{keys[0]}"
    forces_key: "{keys[1]}"
    E0s: "{e0_dict[i]}" """
        return head_text

    def _write_mace_mhft_config(self, config):
        """Write the MACE multihead-finetuning configuration to a YAML file."""
        filenames = self._get_filename(self.run_type)
        heads_config = self._write_mace_mhft_heads(self.config)
        
        config_content = f"""model: "MACE"
foundation_model: {self._translate_mace_foundation_model(config['foundation_model'])}
name: "{config['project_name']}"
multiheads_finetuning: True
{heads_config}
batch_size: {config['batch_size']}
max_num_epochs: {config['epochs']}
seed: {config['seed']}
lr: {config['lr']}
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
save_all_checkpoints: True

# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        python_content = self._write_mace_pyft_script(filenames[1])
        
        # Write the configuration and python content to files
        with open(filenames[0], 'w') as file:
            file.write(python_content)
        with open(filenames[1], 'w') as file:
            file.write(config_content)
        
        # Write runscript    
        self._runscript_wrapper(config['device'], filenames[0])

    def _write_sevennet_pyft_script(self, train_filename):
        """Prepare the dataset for the SevenNet finetuning."""
        python_content = f"""
# This script prepares the dataset for SevenNet finetuning. Please run it before starting the finetuning process.
import os
from sevenn.train.graph_dataset import SevenNetGraphDataset

cutoff = 5.0
working_dir = os.getcwd()
dataset = SevenNetGraphDataset(cutoff=cutoff, root=working_dir, files='{train_filename}', processed_name='graph.pt')
"""
        return python_content

    def sevennet_ft(self):
        """Generate input files for SevenNet finetuning."""
        
        config = self.config
        filenames = self._get_filename(self.run_type)

        keys = self._check_extxyz_keys(config['train_file'])
        if keys != ['energy', 'forces']:
            with open(config['train_file'], 'r') as file:
                filedata = file.read()
            filedata = filedata.replace(keys[0], 'energy').replace(keys[1], 'forces')
            with open(config['train_file'], 'w') as file:
                file.write(filedata)
        
        config_content =f"""model:
    chemical_species: 'Auto'
    cutoff: 5.0
    channel: 128
    is_parity: False
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
    self_connection_type: 'linear'

    train_shift_scale: False   # customizable (True | False)
    train_denominator: False   # customizable (True | False)

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

    continue:
        reset_optimizer: True
        reset_scheduler: True
        reset_epoch: True
        checkpoint: 'SevenNet-0_11July2024'

data:  # Customizable
    batch_size: {config['batch_size']}
    data_divide_ratio: 0.1

    data_format_args:
        index: ':'
    load_trainset_path: ['./sevenn_data/graph.pt']
"""
        # Write the configuration and python content to files
        python_content = self._write_sevennet_pyft_script(config['train_file'])
        
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

    def mattersim_ft(self):
        """Generate input files for MatterSim finetuning."""
        
        config = self.config
        truefalse_dict = {'y': '--save_checkpoint', 'n': ''}
        early_stopping_dict = {'y': '', 'n': '--early_stop_patience 1000'}
        if config['foundation_model'] == 'small':
            model_path = 'MatterSim-v1.0.0-1M.pth' 
        elif config['foundation_model'] == 'large':
            model_path = 'MatterSim-v1.0.0-5M.pth'
        else:
            model_path = config['foundation_model']
        
        # MatterSim needs specific keys in the train file (energy, forces)
        keys = self._check_extxyz_keys(config['train_file'])
        if keys != ['energy', 'forces']:
            with open(config['train_file'], 'r') as file:
                filedata = file.read()
            filedata = filedata.replace(keys[0], 'energy').replace(keys[1], 'forces')
            with open(config['train_file'], 'w') as file:
                file.write(filedata)
            
        train_command = f""" --load_model_path {model_path} --train_data_path {config['train_file']} --device {config['device']} --force_loss_ratio {config['force_loss_ratio']} --batch_size {config['batch_size']} {truefalse_dict[config['save_checkpoint']]} --ckpt_interval {config['ckpt_interval']} --epochs {config['epochs']} {early_stopping_dict[config['early_stopping']]} --seed {config['seed']} --lr {config['lr']} --save_path {config['save_path']}"""

        # Write runscript with the training command
        self._runscript_wrapper('gpu', None, train_command)

    def orb_ft(self):
        """Generate input files for ORB finetuning."""
        
        config = self.config
        filenames = self._get_filename(self.run_type)

        keys = self._check_extxyz_keys(config['train_file'])
        if keys != ['energy', 'forces']:
            with open(config['train_file'], 'r') as file:
                filedata = file.read()
            filedata = filedata.replace(keys[0], 'energy').replace(keys[1], 'forces')
            new_filename = config['train_file'].split('/')[-1]
            config['train_file'] = new_filename.replace('.', '_modified_keys.')

            with open(config['train_file'], 'w') as file:
                file.write(filedata)

        # Create the ase db file: https://wiki.fysik.dtu.dk/ase/ase/db/db.html
        try:
            from ase.db import connect
            from ase.io import read
        except ImportError:
            raise ImportError("ASE and/or the ASE Database Extention is not installed. Please install via:  pip install git+https://gitlab.com/ase/ase-db-backends.git .")

        print("Creating ASE database from the train file...")
        atom_list = read(config['train_file'], ":")
        db = connect('dataset.db')

        for atom in atom_list:
            db.write(atom)

        config['train_file'] = 'dataset.db'

        if np.size(config['foundation_model']) > 1:
            foundation_model = f"{config['foundation_model'][0]}_{config['foundation_model'][1]}"
        else:
            foundation_model = config['foundation_model']
        
        python_content = r"""
# Note:
# The original code for the Finetune Python script is adapted from:
# https://github.com/orbital-materials/orb-models/blob/main/finetune.py
# and is used under the terms of the Apache License 2.0.

import argparse
import logging
import os
from typing import Dict, Optional, Union

import torch
import tqdm
from torch.optim.lr_scheduler import _LRScheduler
from torch.utils.data import BatchSampler, DataLoader, RandomSampler, random_split 

from orb_models import utils
from orb_models.dataset import augmentations
from orb_models.dataset.ase_sqlite_dataset import AseSqliteDataset
from orb_models.forcefield import atomic_system, base, pretrained, property_definitions

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)



def finetune(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    dataloader: DataLoader,
    lr_scheduler: Optional[_LRScheduler] = None,
    num_steps: Optional[int] = None,
    clip_grad: Optional[float] = None,
    log_freq: Optional[int] = None,  # will be auto-set below
    device: torch.device = torch.device("cpu"),
    epoch: int = 0,
    force_loss_ratio: float = 1.0,
):
    if clip_grad is not None:
        hook_handles = utils.gradient_clipping(model, clip_grad)

    metrics = utils.ScalarMetricTracker()
    model.train()

    # Auto-set log_freq to num_steps (once per epoch)
    if log_freq is None:
        log_freq = num_steps if num_steps is not None else 1

    batch_generator = iter(dataloader)
    if num_steps is None:
        try:
            num_steps = len(dataloader)
        except TypeError:
            raise ValueError("Dataloader has no length, and num_steps was not set.")

    i = 0
    batch_iterator = iter(batch_generator)
    while True:
        if i == num_steps:
            break

        optimizer.zero_grad(set_to_none=True)

        step_metrics = {
            "batch_size": 0.0,
            "batch_num_edges": 0.0,
            "batch_num_nodes": 0.0,
        }

        if i % log_freq == 0:
            metrics.reset()

        batch = next(batch_iterator)
        batch = batch.to(device)
        step_metrics["batch_size"] += len(batch.n_node)
        step_metrics["batch_num_edges"] += batch.n_edge.sum()
        step_metrics["batch_num_nodes"] += batch.n_node.sum()

        with torch.autocast("cuda", enabled=False):
            batch_outputs = model.loss(batch)
            loss = batch_outputs.log["forces_loss"] * force_loss_ratio + batch_outputs.log["energy_loss"]
            metrics.update(batch_outputs.log)

        if torch.isnan(loss):
            raise ValueError("nan loss encountered")

        loss.backward()
        optimizer.step()

        if lr_scheduler is not None:
            lr_scheduler.step()

        metrics.update(step_metrics)

        if (i + 1) % log_freq == 0:
            metrics_dict = metrics.get_metrics()
            log_msg = (
                f"Epoch {epoch:03d} | "
                f"loss={metrics_dict.get('loss', 0):.6f} | "
                f"energy_loss={metrics_dict.get('energy_loss', 0):.6f} | "
                f"forces_loss={metrics_dict.get('forces_loss', 0):.6f} | "
                f"energy_mae={metrics_dict.get('energy_mae_raw', 0):.3f} | "
                f"forces_mae={metrics_dict.get('forces_mae_raw', 0):.3f}"
            )
            logging.info(log_msg)

        i += 1

    if clip_grad is not None:
        for h in hook_handles:
            h.remove()

    return metrics.get_metrics()

def evaluate(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: torch.device = torch.device("cpu"),
    epoch: int = 0,
):
    model.eval()
    metrics = utils.ScalarMetricTracker()

    with torch.no_grad():
        for batch in dataloader:
            batch = batch.to(device)
            with torch.autocast("cuda", enabled=False):
                batch_outputs = model.loss(batch)
                metrics.update(batch_outputs.log)

    metrics_dict = metrics.get_metrics()
    log_msg = (
        f"Epoch {epoch:03d} | Test loss={metrics_dict.get('loss', 0):.6f} | "
        f"energy_loss={metrics_dict.get('energy_loss', 0):.6f} | "
        f"forces_loss={metrics_dict.get('forces_loss', 0):.6f} | "
        f"energy_mae={metrics_dict.get('energy_mae_raw', 0):.3f} | "
        f"forces_mae={metrics_dict.get('forces_mae_raw', 0):.3f}"
    )
    logging.info(log_msg)
    return metrics_dict

    
def build_dataloaders(
    dataset_name: str,
    dataset_path: str,
    num_workers: int,
    batch_size: int,
    system_config: atomic_system.SystemConfig,
    target_config: Optional[Dict] = None,
    augmentation: Optional[bool] = True,
    split_ratio: float = 0.8,   # default 80% train, 20% test
    **kwargs,
):
    aug = [augmentations.rotate_randomly] if augmentation else []

    target_config = property_definitions.instantiate_property_config(target_config)
    full_dataset = AseSqliteDataset(
        dataset_name,
        dataset_path,
        system_config=system_config,
        target_config=target_config,
        augmentations=aug,
        **kwargs,
    )

    train_size = int(split_ratio * len(full_dataset))
    test_size = len(full_dataset) - train_size
    train_dataset, test_dataset = random_split(full_dataset, [train_size, test_size])

    logging.info(f"Dataset split into {train_size} train and {test_size} test samples.")

    # --- Train loader ---
    train_sampler = RandomSampler(train_dataset)
    train_batch_sampler = BatchSampler(train_sampler, batch_size=batch_size, drop_last=False)
    train_loader = DataLoader(
        train_dataset,
        num_workers=num_workers,
        worker_init_fn=utils.worker_init_fn,
        collate_fn=base.batch_graphs,
        batch_sampler=train_batch_sampler,
        timeout=10 * 60 if num_workers > 0 else 0,
    )

    # --- Test loader ---
    test_sampler = RandomSampler(test_dataset)
    test_batch_sampler = BatchSampler(test_sampler, batch_size=batch_size, drop_last=False)
    test_loader = DataLoader(
        test_dataset,
        num_workers=num_workers,
        worker_init_fn=utils.worker_init_fn,
        collate_fn=base.batch_graphs,
        batch_sampler=test_batch_sampler,
        timeout=10 * 60 if num_workers > 0 else 0,
    )

    return train_loader, test_loader, len(train_dataset)


def run(args):

    device = utils.init_device(device_id=args.device_id)
    utils.seed_everything(args.random_seed)

    # Setting this is 2x faster on A100 and H100
    # GPUs and does not appear to hurt training
    precision = "float32-high"

    # Instantiate model
    base_model = args.base_model
    model = getattr(pretrained, base_model)(
        device=device, precision=precision, train=True
    )

    if "stress" in model.heads:
        print("Removing stress head from model for finetuning.")
        # Remove the stress head if it exists
        del model.heads["stress"]

    model_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logging.info(f"Model has {model_params} trainable parameters.")
    model.to(device=device)
    
    loader_args = dict(
        dataset_name=args.dataset,
        dataset_path=args.data_path,
        num_workers=args.num_workers,
        batch_size=args.batch_size,
        target_config={"graph": ["energy"], "node": ["forces"]},
    )
    train_loader, test_loader, num_steps = build_dataloaders(
    **loader_args,
    system_config=model.system_config,
    augmentation=True,
    split_ratio=0.8,
    )

    logging.info("Starting training!")

    # num_steps divided by the batch size:
    num_steps = int(num_steps // args.batch_size)

    total_steps = args.max_epochs * num_steps
    optimizer, lr_scheduler = utils.get_optim(args.lr, total_steps, model)

    best_test_loss = float("inf")
    start_epoch = 0

    for epoch in range(start_epoch, args.max_epochs):
        print(f"Start epoch: {epoch} training...")
        finetune(
            model=model,
            optimizer=optimizer,
            dataloader=train_loader,
            lr_scheduler=lr_scheduler,
            clip_grad=args.gradient_clip_val,
            device=device,
            num_steps=num_steps,
            epoch=epoch,
            force_loss_ratio=args.force_loss_ratio,
        )

        test_metrics = evaluate(model, test_loader, device=device, epoch=epoch)
        test_loss = test_metrics.get("loss", float("inf"))

        if test_loss < best_test_loss:
            best_test_loss = test_loss
            if not os.path.exists(args.checkpoint_path):
                os.makedirs(args.checkpoint_path)
            torch.save(
                model.state_dict(),
                os.path.join(args.checkpoint_path, f"best_model.ckpt"),
            )
            logging.info(f"New best model saved with test loss {test_loss:.6f}")


        # Save every X epochs and final epoch
        if (epoch % args.save_every_x_epochs == 0) or (epoch == args.max_epochs - 1):
            # create ckpts folder if it does not exist
            if not os.path.exists(args.checkpoint_path):
                os.makedirs(args.checkpoint_path)
            torch.save(
                model.state_dict(),
                os.path.join(args.checkpoint_path, f"checkpoint_epoch{epoch}.ckpt"),
            )
            logging.info(f"Checkpoint saved to {args.checkpoint_path}")

def after_run():
    models_dir = 'models'
    best_model_file = os.path.join(models_dir, 'best_model.ckpt')

    if not os.path.exists(models_dir):
        raise FileNotFoundError(
            "The 'models' directory does not exist. Please ensure the finetuning script has been run and the models directory is created."
        )

"""+f"""                
def after_run():
    models_dir = 'models'
    best_model_file = os.path.join(models_dir, 'best_model.ckpt')

    if not os.path.exists(models_dir):
        raise FileNotFoundError(
            "The 'models' directory does not exist. Please ensure the finetuning script has been run and the models directory is created."
        )

    if os.path.exists(best_model_file):
        target_file = os.path.join(os.getcwd(), '{config['project_name'] + '.ckpt'}') """+r"""
        os.rename(best_model_file, target_file)
        print(f"Best model '{best_model_file}' has been saved to '{target_file}'.")
    else:
        print("No best_model.ckpt found in models directory.")

"""+f"""

from types import SimpleNamespace
def main():
    args = SimpleNamespace(
        random_seed={config['seed']},
        device_id=0,
        dataset="Custom FT-Dataset",
        data_path="{config['train_file']}",
        num_workers=6,
        batch_size={config['batch_size']},
        gradient_clip_val=0.5,
        max_epochs={config['epochs']},
        save_every_x_epochs=25,
        checkpoint_path=os.path.join(os.getcwd(), "models"),
        lr={config['lr']},
        base_model="{foundation_model}",
        force_loss_ratio={config['force_loss_ratio']}
    )
    run(args)


if __name__ == "__main__":
    main()
    after_run()

"""
        # Write the python content to file
        with open(filenames[0], 'w') as file:
            file.write(python_content)

        # Write runscript    
        self._runscript_wrapper('cuda', filenames[0])

    def grace_ft(self):
        """Generate input files for GRACE finetuning."""
        
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
# The original code for the Finetune Python script is adapted from the 'gracemaker -t' command
seed: {config['seed']}
cutoff: n/a

data:
  filename: "{config['train_file']}" 
  test_size: 0.05
  reference_energy: 0 """+r"""
  # reference_energy: {atom1: reference_energy, atom2: reference_energy}
  # save_dataset: False """+f"""


potential:
  elements: 
  finetune_foundation_model: {config['foundation_model']} # LINEAR, FS, GRACE_1LAYER, GRACE_2LAYER
  reduce_elements: True #  default - False, reduce elements to those provided in dataset """+r"""  
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

  #  optimizer: L-BFGS-B
  #  opt_params: { "maxcor": 100, "maxls": 20 }

  ## needed for low-energy tier metrics and for "convex_hull"-based distance of energy-based weighting scheme
  compute_convex_hull: False
  batch_size: """+str(config['batch_size'])+""" # Important hyperparameter for Adam and irrelevant (but must be) for L-BFGS-B
  test_batch_size: 4 # test batch size (optional)

  jit_compile: True
  eval_init_stats: True # to evaluate initial metrics

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