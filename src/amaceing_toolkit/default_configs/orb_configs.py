def configs_orb(config_name):
  config_dict = {


    'default' : {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD' : {
        'simulation_environment': 'ase',
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
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
        'foundation_model': ['orb_v2', 'orb_v3_conservative_inf'],
        'modal': ['', 'omat'],
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
      'GEO_OPT': {
        'simulation_environment': 'ase',
        'max_iter': 1000,
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
        'dispersion_via_simenv': 'n'
      },
      'CELL_OPT': {
        'simulation_environment': 'ase',
        'max_iter': 1000,
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
        'dispersion_via_simenv': 'n'
      },
      'FINETUNE' : {
        'foundation_model': 'orb_v2',
        'batch_size': 4,
        'epochs': 200,
        'seed': 1,
        'force_file': 'force.xyz',
        'lr': 3e-4,
        'force_loss_ratio': 1.0,
      },
      'RECALC' : {
        'simulation_environment': 'ase',
        'foundation_model': 'orb_v3_conservative_inf',
        'modal': 'omat',
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