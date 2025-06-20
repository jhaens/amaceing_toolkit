def configs_uma(config_name):
  config_dict = {


    'default' : {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD' : {
        'foundation_model': 'omat',
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
        'foundation_model': ['omat', 'omol'],
        'temperature': '300',
        'pressure': '1.0',
        'thermostat': 'Langevin',
        'nsteps': 2000000,
        'write_interval': 10,
        'timestep': 0.5,
        'log_interval': 100,
        'print_ase_traj': 'y'
      },
      'RECALC' : {
        'foundation_model': 'omat',
      },
    },


    'myown_config' : {
      'coord_file' : 'coord.xyz',
      'run_type' : 'MD',
      '...' : '...'
    }

  }

  return config_dict[config_name]  