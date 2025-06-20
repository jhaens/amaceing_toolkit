def configs_sevennet(config_name):
  config_dict = {


    'default' : {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD' : {
        'simulation_environment': 'ase',
        'foundation_model': '7net-mf-ompa',
        'modal': 'mpa',
        'dispersion_via_simenv': 'n',
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
        'foundation_model': ['7net-0', '7net-mf-ompa'],
        'modal': ['', 'mpa'],
        'dispersion_via_simenv': ['n', 'n'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ext_traj': 'y'
      },
      'FINETUNE' : {
        'foundation_model': '7net-0',
        'batch_size': 4,
        'epochs': 100,
        'seed': 1,
        'force_file': 'force.xyz',
        'lr': 0.01
      },
      'RECALC' : {
        'simulation_environment': 'ase',
        'foundation_model': '7net-mf-ompa',
        'modal': 'mpa',
        'dispersion_via_simenv': 'n'
      },
    },


    'myown_config' : {
      'coord_file' : 'coord.xyz',
      'run_type' : 'MD',
      '...' : '...'
    }

  }

  return config_dict[config_name]  