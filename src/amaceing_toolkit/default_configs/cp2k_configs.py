def configs_cp2k(config_name):
  config_dict = {


    'default' : {
      'cp2k_newer_than_2023x': 'y',
      'coord_file' : 'coord.xyz',
      'box_cubic' : 'y',
      'run_type' : 'MD',
      'use_default_input' : 'y',
      'MD' : {
        'ensemble' : 'NVT',
        'nsteps' : 200000,
        'timestep' : 0.5,
        'temperature' : 300,
        'print_forces' : 'y',
        'print_velocities' : 'n',
        'xc_functional' : 'BLYP',
        'equilibration_steps' : 2000,
        'pressure_b': 1.0,
        'equilibration_run' : 'y'
      },
      'GEO_OPT': {
        'max_iter': 1000,
        'print_forces': 'n',
        'xc_functional': 'BLYP'
      },
      'CELL_OPT': {
        'max_iter': 1000,
        'keep_symmetry': 'y',
        'xc_functional': 'BLYP',
        'symmetry': 'CUBIC'
      },
      'REFTRAJ' : {
        'nsteps' : 400000,
        'stride' : 200,
        'print_forces' : 'y',
        'print_velocities' : 'n',
        'xc_functional' : 'BLYP'
      },
      'ENERGY': {
        'xc_functional': 'BLYP'
      }
    },


    'myown_config' : {
      'cp2k_newer_than_2023x': 'y',
      'coord_file' : 'coord.xyz',
      'run_type' : 'MD',
      '...' : '...'
    }

  }

  return config_dict[config_name]  
