def configs_grace(config_name):
  config_dict = {


    'default' : {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD' : {
        'simulation_environment': 'ase',
        'foundation_model': 'GRACE-1L-OMAT',
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ext_traj': 'y',
        #'dispersion_via_simenv': 'n'
      },
      'MULTI_MD' : {
        'simulation_environment': 'ase',
        'foundation_model': ['GRACE-1L-OAM', 'GRACE-1L-OMAT'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ext_traj': 'y',
        #'dispersion_via_simenv': ['n', 'n'],
      },
      'GEO_OPT': {
        'simulation_environment': 'ase',
        'max_iter': 1000,
        'foundation_model': 'GRACE-1L-OMAT',
        #'dispersion_via_simenv': 'n'
      },
      'CELL_OPT': {
        'simulation_environment': 'ase',
        'max_iter': 1000,
        'foundation_model': 'GRACE-1L-OMAT',
        #'dispersion_via_simenv': 'n'
      },
      'FINETUNE' : {
        'foundation_model': 'GRACE-1L-OAM',
        'batch_size': 4,
        'epochs': 500,
        'seed': 1,
        'force_file': 'force.xyz',
        'lr': 0.001,
        'force_loss_ratio': 5.0,
      },
      'RECALC' : {
        'simulation_environment': 'ase',
        'foundation_model': 'GRACE-1L-OAM',
        #'dispersion_via_simenv': 'n'
      },
    },


    'myown_config' : {
      'coord_file' : 'coord.xyz',
      'run_type' : 'MD',
      '...' : '...'
    }

  }

  return config_dict[config_name]  