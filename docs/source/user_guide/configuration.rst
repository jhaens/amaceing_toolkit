Configuration Guide
===================

Default Values for Input Files
------------------------------

You can customize default values for input files in the following configuration files:

* CP2K: ``/src/amaceing_toolkit/default_configs/cp2k_config.py``
* MACE: ``/src/amaceing_toolkit/default_configs/mace_config.py``
* MatterSim: ``/src/amaceing_toolkit/default_configs/mattersim_config.py``
* SevenNet: ``/src/amaceing_toolkit/default_configs/sevennet_config.py``

Additional data files:

* CP2K basis sets and XC functionals: ``/src/amaceing_toolkit/default_configs/cp2k_kind_data.py``
* MACE atomic energies: ``/src/amaceing_toolkit/default_configs/mace_e0s.py``

HPC Runscript Creator
---------------------

The package supports LSF and SLURM workload managers. Configuration is stored in:

.. code-block:: bash

    /src/amaceing_toolkit/default_configs/hpc_setup.txt

Edit this file to customize your HPC setup.

Logger
------

The run and model logger is located in:

.. code-block:: bash

    /src/amaceing_toolkit/runs/

View logs with:

.. code-block:: bash

    amaceing_utils --logger=runs
    amaceing_utils --logger=models