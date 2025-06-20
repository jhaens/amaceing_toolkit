def configs_mace(config_name):
  config_dict = {


    'default' : {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD' : {
        'simulation_environment': 'ase',
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ext_traj': 'y'
      },
      'MULTI_MD' : {
        'simulation_environment': 'ase',
        'foundation_model': ['mace_mp', 'mace_mp', 'mace_off'],
        'model_size': ['small', 'medium', 'small'],
        'dispersion_via_ase': ['n', 'n', 'n'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ext_traj': 'y'
      },
      'GEO_OPT': {
        'simulation_environment': 'ase',
        'max_iter': 1000,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n'
      },
      'CELL_OPT': {
        'simulation_environment': 'ase',
        'max_iter': 1000,
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n'
      },
      'FINETUNE' : {
        'device': 'cuda',
        'stress_weight': 0.0,
        'forces_weight': 10.0,
        'energy_weight': 1.0,
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
        'energy_weight': 1.0,
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
        'simulation_environment': 'ase',
        'foundation_model': 'mace_mp',
        'model_size': 'small',
        'dispersion_via_ase': 'n'
      },
    },


    'myown_config' : {
      'coord_file' : 'coord.xyz',
      'run_type' : 'MD',
      '...' : '...'
    }

  }

  return config_dict[config_name]  