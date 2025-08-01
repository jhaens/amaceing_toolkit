Configuration Guide
===================

Default Values for Input Files
------------------------------

The amaceing_toolkit provides a comprehensive set of default configurations for various molecular simulation engines. These configurations can be customized to suit your specific needs.

Configuration files are located in the ``src/amaceing_toolkit/default_configs/`` directory:

* CP2K: ``cp2k_configs.py``
* MACE: ``mace_configs.py``
* MatterSim: ``mattersim_configs.py``
* SevenNet: ``sevennet_configs.py``
* ORB: ``orb_configs.py``
* Grace: ``grace_configs.py``

Each configuration file contains a dictionary of settings organized by simulation type (MD, GEO_OPT, etc.) and other parameters relevant to each engine.

Additional Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **CP2K basis sets and XC functionals**: ``cp2k_kind_data.py`` contains basis set information and exchange-correlation functional definitions for CP2K.
* **MACE atomic energies**: ``mace_e0s.py`` contains reference atomic energies used by MACE models.

Example Configuration Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CP2K configuration example:

.. code-block:: python

    'default': {
      'cp2k_newer_than_2023x': 'y',
      'coord_file': 'coord.xyz',
      'box_cubic': 'y',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD': {
        'ensemble': 'NVT',
        'nsteps': 200000,
        'timestep': 0.5,
        'temperature': 300,
        'print_forces': 'y',
        'print_velocities': 'n',
        'xc_functional': 'BLYP',
        'equilibration_steps': 2000,
        'pressure_b': 1.0,
        'equilibration_run': 'y'
      },
      'GEO_OPT': {...}, ...
    }

MACE configuration example:

.. code-block:: python

    'default': {
      'coord_file': 'coord.xyz',
      'box_cubic': 'pbc',
      'run_type': 'MD',
      'use_default_input': 'y',
      'MD': {
        'simulation_environment': 'ase',
        'foundation_model': 'mace_mp',
        'model_size': 'small',
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
      'GEO_OPT': {...}, ...
    }

HPC Runscript Creator
---------------------

The toolkit provides templates for creating HPC job submission scripts for different computing environments. These templates support LSF and SLURM workload managers.

The path to the runscript templates is defined in:

.. code-block:: bash

    src/amaceing_toolkit/default_configs/hpc_setup_path.txt

The toolkit includes templates for various simulation engines and computing platforms:

* **CP2K**: ``cp2k``, ``cp2k_local``
* **MACE**: ``mace_py_cpu``, ``mace_py_gpu``, ``mace_lmp_cpu``, ``mace_lmp_gpu``
* **MatterSim**: ``mattersim_py_cpu``, ``mattersim_py_gpu``, ``mattersim_ft_gpu``
* **SevenNet**: ``sevennet_py_cpu``, ``sevennet_py_gpu``, ``sevennet_lmp_cpu``, ``sevennet_lmp_gpu``
* **ORB**: ``orb_py_cpu``, ``orb_py_gpu``
* **Grace**: ``grace_py_cpu``, ``grace_py_gpu``, ``grace_lmp_cpu``, ``grace_lmp_gpu``, ``grace_ft_gpu``

These templates can be customized to match your specific HPC environment requirements.

Logger
------

The toolkit includes built-in logging capabilities for tracking runs and models:

* **Run logger**: Keeps track of simulation runs in ``run_logger.log`` 
* **Model logger**: Records information about machine learning models in ``finetuned_models.log``

The logger files are located in:

.. code-block:: bash

    src/amaceing_toolkit/runs/

To view logs, use the utility commands:

.. code-block:: bash

    amaceing_utils --logger=run
    amaceing_toolkit --logger=runexport
    amaceing_utils --logger=model

Custom Configurations
---------------------

Users can create their own configuration profiles by modifying the default configuration files or by creating new configuration entries. These custom configurations can be specified when creating new simulation inputs using the toolkit's API or command-line interface.

These modified configurations have to be hard-coded into the input wrapper.