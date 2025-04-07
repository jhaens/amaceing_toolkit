# aMACEing_toolkit

## Table of Contents
- [Description](#description)
- [Installation](#installation)
  - [(i) Installation from source](#i-installation-from-source)
  - [(ii) Installation via pip](#ii-installation-via-pip)
- [Getting started](#getting-started)
- [Full list of the main functions](#full-list-of-the-main-functions)
  - [CP2K input creation](#cp2k-input-creation-amaceing_cp2k)
  - [MACE input creation](#mace-input-creation-amaceing_mace)
  - [MatterSim input creation](#mattersim-input-creation-amaceing_mattersim)
  - [SevenNet input creation](#sevennet-input-creation-amaceing_sevennet)
  - [Analyzer](#analyzer-amaceing_ana)
  - [Utilities](#utilities-amaceing_utils)
- [Examples](#examples)
- [Run & Model logger](#run--model-logger)
- [Configuration of default values for input files](#configuration-of-default-values-for-input-files)
- [Configuration of the runscript creator](#configuration-of-the-runscript-creator)

## Description
This package is designed to help you with the creation of CP2K input files for MACE, MatterSim and SevenNet. It is a command line tool which allows you to create CP2K input files via a Q&A session. The package also includes a run and model logger to keep track of your runs and models. The package is designed to be easy to use and to help you get started with CP2K, MACE, MatterSim and SevenNet.

## Installation
The package is available on GitHub and can be installed via pip.

### (i) Installation from source
**We recommend to use the installation from source. This is the most flexible way to install the package.**

1. It is very strongly recommended to use a virtual environment for the installation of this package. This can be done via conda or venv. If you are using conda, please create a new environment with the following command:

    ```bash
    conda create -n atk python=3.9          # create the environment
    conda activate atk                      # activate the environment
    ```

2. Please look for the right PyTorch installation for your system. You can find the right command for your system here: https://pytorch.org/get-started/locally/. For example, if you are using a CUDA 12.4 you can install PyTorch 2.6.0 with the following command:

    ```bash
    pip install torch torchvision torchaudio
    ```

    If you are using a CPU only system, you can use the following command:

    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    ```

3. Ensure openmpi is installed. This can be done via conda:

    ```bash
    mpirun --version
    ```

    If not installed, you can install it via conda:

    ```bash
    conda install conda-forge::openmpi
    ```

4. To install the aMACEing_toolkit clone this git repository and use pip:

    ```bash
    git clone https://github.com/jhaens/amaceing_toolkit.git
    cd amaceing_toolkit
    ```
    First install the requirements:
    ```bash
    pip install -r requirements.txt
    ```
    and now install the package itself. This can be done via:
    ```bash
    pip install -e .
    ```


    If everything worked fine, you should be able to run the following command:

    ```bash
    amaceing_cp2k --help
    ```
    and the following package should be installed: mace-torch
    ```bash
    pip show mace-torch
    ```
    
5. OPTIONAL: If you want profit from a faster MACE installation, you can install the following packages:

    ```bash
    pip install cuequivariance==0.1.0 cuequivariance-torch==0.1.0 cuequivariance-ops-torch-cu12==0.1.0
    ```
    Further informations concerning these packages are 

6. In order to be able to use the package also with MatterSim and SevenNet you need to create a second environment. This can be done via the following command:

    ```bash
    conda create -n atk_ms7n python=3.9    # create the environment
    conda activate atk_ms7n                # activate the environment
    ```

    Now you can install the package via:

    ```bash
    pip install mattersim==1.1.2 sevenn==0.11.0
    ```
    The second environment is needed because the package mace and MatterSim/SevenNet have som conflicting dependencies:mace-torch depends on e3nn v0.4.4 and MatterSim/SevenNet depend on e3nn v0.5.0. 
    It is also possible to use other names for the environments, but please make sure to change the names in the script `/amaceing_toolkit/src/amaceing_toolkit/default_config/runscript_templates.py` and `/amaceing_toolkit/src/amaceing_toolkit/default_config/hpc_setup.txt`. The names are used in the runscript generation.


7. Congrats you are ready to go! You can now use the package via the command line. 

    ```bash
    amaceing_cp2k
    ```
    If you want to use it in a python script, you can import it via:

    ```python
    import amaceing_cp2k from amaceing_toolkit
    ```

### (ii) Installation via pip
This is the easiest way to install the package. The package is available on PyPI and can be installed via pip. (Please not that with this installation can't run MatterSim and SevenNet simulations via the toolkit directly. You will be able to only create input files for these packages. For this please use the installation from source.)

1. Create a new virtual environment. Please create a new environment with the following command:

    ```bash
    conda create -n atk python=3.9          # create the environment
    conda activate atk                      # activate the environment
    ```

2. Please look for the right PyTorch installation for your system. You can find the right command for your system here: https://pytorch.org/get-started/locally/. For example, if you are using a CUDA 12.4 you can install PyTorch 2.6.0 with the following command:

    ```bash
    pip install torch torchvision torchaudio
    ```
    If you are using a CPU only system, you can use the following command:

    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    ```

3. Install the package via pip:

    ```bash
    pip install amaceing_toolkit
    ```

    If everything worked fine, you should be able to run the following command:

    ```bash
    amaceing_cp2k --help
    ```
    and the following package should be installed: mace-torch
    ```bash
    pip show mace-torch
    ```

## Getting started

This package is designed to be easy to use: via a Q&A you obtain a ready to use CP2K/MACE/MatterSim/SevenNet input file for different types of projects. If enabled and setup your are also able to automatically create the respetive runscript to send your project to a HPC. The setup process for the automatical runscript generation is called at your first run. You can also change them yourself editing the hpc_setup.txt file in the folder /amaceing_toolkit/src/amaceing_toolkit/default_config, its configuration is explained below.

The main functions available (until now) are the creation of MACE, MatterSim (, SevenNet) and CP2K input files. Also other useful small scripts are available via an third main function. These could be achieved via the following commands:

```bash
amaceing_cp2k # Starts Q&A session for cp2k input creation

amaceing_mace # Starts Q&A session for mace-torch input creation

amaceing_mattersim # Starts Q&A session for mattersim input creation

amaceing_sevennet # Starts Q&A session for sevennet input creation

amaceing_ana # Starts Q&A session for the analyzer (only RDF, MSD and single particle MSD)

amaceing_utils # Starts Q&A session for some useful tools including the evaluation of the performance of a (fine-tuned) model
```

## Full list of the main functions

The package includes the following main functions. All of the functions can be run via the command line: 
1. within just **one** line: `amaceing_cp2k -rt="GEOOPT" -c="{'project_name': 'first_test', ...}"`or,
2. via a Q&A session: `amaceing_cp2k`.

All of the functions include a extensive help function. You can get the help function via the command line with the following command:

```bash
amaceing_cp2k --help
```
The syntax of the one-line commands is the same for all of the functions:
```bash
amaceing_<function> -rt="<run_type>" -c="{'project_name': 'first_test', 'pbc_list': '[10 10 10]', ...}"
```
> [!IMPORTANT]
> Please do **NOT** use **double quotes inside the dictionary**. Also do **NOT** use **commas inside of lists** in the dictionary. The dictionary is passed as a string and double quotes are not allowed. 

### CP2K input creation: amaceing_cp2k
The CP2K input creation is designed to be easy to use. You can create a CP2K input file for different types of projects. The following types are available:
- Geometry optimization
- Cell optimization
- Molecular dynamics
- Recalculation of a reference trajectory
- Single point energy calculation

### MACE input creation: amaceing_mace
The MACE input creation is designed to be easy to use. You can create a MACE input file for different types of projects. The following types are available:
- Geometry optimization
- Cell optimization
- Molecular dynamics
- Multi-configuration molecular dynamics
- Fine-tuning of a foundation model
- Multihead fine-tuning of a foundation model
- Recalculation of a reference trajectory

### MatterSim input creation: amaceing_mattersim
The MatterSim input creation is designed to be easy to use. You can create a MatterSim input file for different types of projects. The following types are available:
- Molecular dynamics
- Multi-configuration molecular dynamics
- Fine-tuning of a foundation model
- Recalculation of a reference trajectory

### SevenNet input creation: amaceing_sevennet
The SevenNet input creation is designed to be easy to use. You can create a SevenNet input file for different types of projects. The following types are available:
- Molecular dynamics
- Multi-configuration molecular dynamics
- SOON: Fine-tuning of a foundation model 
- Recalculation of a reference trajectory

### Analyzer: amaceing_ana
The analyzer is designed to be easy to use. You can analyze the results of the runs you have done with the package. The main focus is to get a fast overview over very basic properties: MSD, RDF, single-particle MSD. The analyzer will be available via the command:

 - Single Trajectory Analysis
 - Multiple Trajectory Analysis
 - Radial distribution function (RDF)
 - Mean square displacement (MSD)
 - Single particle mean square displacement (sMSD)

### Utilities: amaceing_utils
The package also includes some small utilities which are designed to help you while working with fine-tuned models and trajectories. The following utilities are available:
- Evaluation of the error of a (fine-tuned) model with respect to a reference AIMD trajectory
- Preparation of an AIMD reference trajectory for the error evaluation of a (fine-tuned) of a model
- Extraction of every n-th frame of a trajectory
- Get the right citations of a calculation run
- Benchmark the different models against a reference AIMD trajectory
- Print the content of the run and model logger

## Examples
Each of the main functions has its test script in the main examples folder: `/amaceing_toolkit/examples/`. Here you can find different systems on which you can test the functions of the  aMACEing_toolkit: `4KOH_92H2O` and `CsH2PO4`. More examples will be added in the future. 
The examples are designed to be easy to use and to help you get started with the package. You can run each example via the respective test script. The test scripts are located in the folder `/amaceing_toolkit/examples/<system_name>/`. The test scripts can be started via the following command: 

```bash
bash /path/to/amaceing_toolkit/examples/4KOH_92H2O/mace_test.sh
```

Examples for the analyzer are also included in the folder `/amaceing_toolkit/examples/analyzer/`. The test script can be started via the following command:

```bash
bash /path/to/amaceing_toolkit/examples/analyzer/analyzer_test.sh
```

## Run & Model logger
The package also includes a run and model logger. This is a small tool to keep track of the runs you have done with the package. The logger is located in the folder `/amaceing_toolkit/src/amaceing_toolkit/runs/`. You can get an overview over the runs you have done and models you have fine-tuned with the package via the commands:

```bash
amaceing_utils --logger=runs
amaceing_utils --logger=models
```


## Configuration of default values for input files

This package allows for the use of predefined input values. The setup of this values is done in the following files. There you can add your own preset values, change the default values and define whitch preset should be used in the main runs.

```bash
/path/to/amaceing_toolkit/src/amaceing_toolkit/default_configs/cp2k_config.py # Open and change the cp2k config file 

/path/to/amaceing_toolkit/src/amaceing_toolkit/default_configs/mace_config.py # Open and change the mace config file 

/path/to/amaceing_toolkit/src/amaceing_toolkit/default_configs/mattersim_config.py # Open and change the mattersim config file 

/path/to/amaceing_toolkit/src/amaceing_toolkit/default_configs/sevennet_config.py # Open and change the sevennet config file 
```

The different calculation programs are sometimes using data which is stored in dictionary files (e.g. basis sets, xc functionals, atomic energies), these can be found in the same folder. If needed please insert here the required data.

```bash
/path/to/amaceing_toolkit/src/amaceing_toolkit/default_configs/cp2k_kind_data.py # Open and add data to the basis set and xc functional file 

/path/to/amaceing_toolkit/src/amaceing_toolkit/default_configs/mace_e0s.py # Open and add data to the atomic energies file
```


## Configuration of the runscript creator

Until now only specific runscripts for the workload managers LSF (utilized at TU Ilmenau) and SLURM (utilized MLU Halle-Wittenberg) are supported. Other will follow soon. The relevant information is saved and set in the `hpc_setup.txt` file. It is created upon first run of any `amaceing`-command.

```bash
vi /path/to/amaceing_toolkit/src/amaceing_toolkit/default_configs/hpc_setup.txt # Open and change the config file 

```


## Planned features
Not implemented yet, but planned:

- [x] Second example system
- [x] Test SevenNet implementation
- [ ] Support for non-orthorhombic systems
- [x] Analyzer
- [ ] Implement rotation autocorrelation function
- [x] Visualization of Analyzer results
- [ ] SevenNet Fine-tuning
- [ ] Web-API to monitor the runs
- [ ] More examples
- [ ] Support of other workload managers (Contributions are welcome!)




## Authors and acknowledgment
This package was developed by Jonas Hänseroth, a PhD student at the Institute of Physics at the Technische Universität Ilmenau. I would like to thank all members of the Theoretical Solid-State Physics Group at Ilmenau for their support and help during the development of this package, especially Johannes Wolf and my supervisor Christian Dreßler.  
The package is based on the work of the MACE, MatterSim, SevenNet and CP2K team. 

## License
This project is licensed under the MIT License (Non-Commercial Use Only).

***
**Please help the development of this package by sending any suggestions and you have to the author!**

**THANK YOU FOR USING THIS PACKAGE!**
***
