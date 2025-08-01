def configs_mattersim(config_name):
  config_dict = {


    'default' : {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD' : {
        'foundation_model': 'large',
        #'dispersion_via_ase': 'n',
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
        'foundation_model': ['small', 'large'],
        #'dispersion_via_ase': ['n', 'n'],
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
        'max_iter': 1000,
        'foundation_model': 'large',
        #'dispersion_via_ase': 'n'
      },
      'CELL_OPT': {
        'max_iter': 1000,
        'foundation_model': 'large',
        #'dispersion_via_ase': 'n'
      },
      'FINETUNE' : {
        'device': 'cuda',
        'force_loss_ratio': 0.5,
        'foundation_model': 'small',
        'batch_size': 5,
        'save_checkpoint': 'y',
        'ckpt_interval': 25,
        'epochs': 300,
        'seed': 1,
        'lr': 0.0005,
        'force_file': 'force.xyz',
        'save_path': 'MatterSim_models',
        'early_stopping': 'n'
      },   
      'RECALC' : {
        'foundation_model': 'large',
        #'dispersion_via_ase': 'n'
      },
    },


    'myown_config' : {
      'coord_file' : 'coord.xyz',
      'run_type' : 'MD',
      '...' : '...'
    }

  }

  return config_dict[config_name]  