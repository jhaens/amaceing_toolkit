def configs_mace(config_name):
  config_dict = {


    'default' : {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD' : {
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_mace': 'n',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ase_traj': 'y'
      },
      'MULTI_MD' : {
        'foundation_model': ['mace_mp', 'mace_mp', 'mace_off'],
        'model_size': ['small', 'medium', 'small'],
        'dispersion_via_mace': ['n', 'n', 'n'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ase_traj': 'y'
      },
      'GEO_OPT': {
        'max_iter': 1000,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_mace': 'n'
      },
      'CELL_OPT': {
        'max_iter': 1000,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_mace': 'n'
      },
      'FINETUNE' : {
        'device': 'cuda',
        'stress_weight': 0.0,
        'forces_weight': 10.0,
        'energy_weight': 0.1,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'prevent_catastrophic_forgetting': 'n',
        'force_file': 'force.xyz',
        'batch_size': 5,
        'valid_batch_size': 2,
        'valid_fraction': 0.1,
        'max_num_epochs': 200,
        'seed': 1,
        'lr': 1e-2, 
        'dir': 'MACE_models'
      },   
      'FINETUNE_MULTIHEAD' : {
        'device': 'cuda',
        'stress_weight': 0.0,
        'forces_weight': 10.0,
        'energy_weight': 0.1,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'train_file': ['train_head0.xyz', 'train_head1.xyz'],
        'batch_size': 5,
        'valid_batch_size': 2,
        'valid_fraction': 0.1,
        'max_num_epochs': 200,
        'seed': 1,
        'lr': 1e-2, 
        'dir': 'MACE_models'
      }, 
      'RECALC' : {
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_mace': 'n'
      },
    },


    'myown_config' : {
      'coord_file' : 'coord.xyz',
      'run_type' : 'MD',
      '...' : '...'
    }

  }

  return config_dict[config_name]  