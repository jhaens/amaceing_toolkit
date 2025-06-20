4KOH_92H2O Example
==================

Overview
--------

This example demonstrates the capabilities of the aMACEing toolkit with a system containing 4 potassium hydroxide molecules (4 KOH) and 92 water molecules at 333 K. This system represents a dilute basic solution relevant for studying proton transfer and hydroxide solvation dynamics.

The example shows how to set up various types of calculations using CP2K, MACE, MatterSim, and SevenNet, including:

* Geometry optimization
* Cell optimization
* Molecular dynamics simulations
* Reference trajectory recalculation
* Energy calculations

System Structure
----------------

The example is organized with the following directory structure:

.. code-block:: none

    4KOH_92H2O_333K/
    ├── data/
    │   ├── system.xyz            # Initial structure file
    │   ├── pbc                   # Cell vectors file
    │   ├── train_file.xyz        # Training file (including positions, energies, forces)
    │   ├── train_file2.xyz       # Second training file (including positions, energies, forces)
    │   ├── train_file_7net.xyz   # Training file with 7net-Keywords (including positions, energies, forces)
    │   ├── system.model          # Small fined-tuned model file
    │   ├── dft_energies.xyz      # Postion and energies file of short dft md 
    │   ├── dft_forces.xyz        # Force file of short dft md
    │   ├── mace_energies.xyz     # Position and energies file of short mace md
    │   ├── mace_forces.xyz       # Force file of short mace md
    │   ├── trajectory.traj       # ASE trajectory file
    │   ├── mace_input.log        # Log file of an aMACEing_mace run
    │   └── ref_trajectory.xyz    # Reference trajectory for recalculation
    ├── cp2k_test.sh              # CP2K examples script
    ├── mace_test.sh              # MACE examples script
    ├── mattersim_test.sh         # MatterSim examples script
    ├── sevennet_test.sh          # SevenNet examples script
    └── utils_test.sh             # Utilities examples script

Each test script demonstrates the corresponding module's functionality with the 4KOH_92H2O system.

Running the Examples
--------------------

CP2K Examples
~~~~~~~~~~~~~

The ``cp2k_test.sh`` script demonstrates five different types of CP2K calculations:

1. **Geometry Optimization**: Optimizes atomic positions to find the minimum energy structure
2. **Cell Optimization**: Optimizes both atomic positions and cell parameters
3. **Molecular Dynamics**: Runs an NVT simulation with equilibration
4. **Reference Trajectory Recalculation**: Recomputes energies and forces along a reference trajectory
5. **Energy Calculation**: Performs a single point energy calculation

You can run the CP2K examples with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/cp2k_test.sh

To run these examples manually using Q&A sessions instead of command line parameters:

.. code-block:: bash

    # For geometry optimization
    mkdir -p cp2k/GEO_OPT
    cd cp2k/GEO_OPT
    amaceing_cp2k
    # Then answer the prompts:
    # - Run type: GEO_OPT
    # - Project name: 4koh_92h2o_geoopt
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Max iterations: 10
    # - XC functional: BLYP
    # - Print forces: OFF
    # - CP2K version newer than 2023: y
    cd ../..

    # For molecular dynamics
    mkdir -p cp2k/MD
    cd cp2k/MD
    amaceing_cp2k
    # Then answer the prompts:
    # - Run type: MD
    # - Project name: 4koh_92h2o_md
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Ensemble: NVT
    # - Number of steps: 10
    # - Timestep: 0.5
    # - Temperature: 300
    # - Print forces: ON
    # - Print velocities: OFF
    # - XC functional: BLYP
    # - Equilibration run: y
    # - Equilibration steps: 5
    # - Pressure: 1.0
    # - CP2K version newer than 2023: y
    cd ../..

After running the examples, each calculation type will have its own directory structure:

.. code-block:: none

    cp2k/
    ├── GEO_OPT/
    │   ├── geoopt_cp2k.inp          # CP2K input file
    │   ├── runscript.sh             # HPC runscript
    │   └── cp2k_input.log           # Log of choices
    ├── CELL_OPT/
    │   ├── cellopt_cp2k.inp
    │   ├── runscript.sh
    │   └── cp2k_input.log
    ├── MD/
    │   ├── equi_md_cp2k.inp         # Equilibration run input
    │   ├── runscript_equi.sh        # Equilibration runscript
    │   ├── md_cp2k.inp              # Production run input
    │   ├── runscript.sh             # Production runscript
    │   └── cp2k_input.log
    ... (and similarly for other calculation types)

Technical Details: 

* The simulation cell is cubic with dimensions 14.2067 × 14.2067 × 14.2067 Å³
* The BLYP exchange-correlation functional is used for CP2K calculations
* For MACE calculations, the Materials Project foundation model is used
* For molecular dynamics, the timestep is set to 0.5 fs
* The system temperature is set to 300 K (rather than the 333 K indicated in the system name)
* The pressure is set to 1.0 bar for NPT simulations


MACE Examples
~~~~~~~~~~~~~

The ``mace_test.sh`` script demonstrates seven different types of MACE calculations:

1. **Geometry Optimization**: Optimizes atomic positions using a MACE foundation model
2. **Cell Optimization**: Optimizes both atomic positions and cell parameters
3. **Molecular Dynamics**: Runs an MD simulation using a MACE model
4. **Multi-Configuration MD**: Runs multiple MD calculations with different foundation models
5. **Fine-tuning**: Fine-tunes a MACE foundation model with custom data
6. **Multihead Fine-tuning**: Fine-tunes a model with multiple data types
7. **Reference Trajectory Recalculation**: Recomputes energies and forces along a reference trajectory

You can run all MACE examples at once with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/mace_test.sh

To run these examples manually using Q&A sessions instead of command line parameters:

.. code-block:: bash

    # For geometry optimization
    mkdir -p mace/GEO_OPT
    cd mace/GEO_OPT
    amaceing_mace
    # Then answer the prompts:
    # - Run type: GEO_OPT
    # - Project name: 4koh_92h2o_geoopt
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Foundation model: mace_mp
    # - Model size: small
    # - Use dispersion via ASE: n
    # - Max iterations: 10
    # - Simulation environment: ASE
    cd ../..

    # For molecular dynamics
    mkdir -p mace/MD
    cd mace/MD
    amaceing_mace
    # Then answer the prompts:
    # - Run type: MD
    # - Project name: 4koh_92h2o_md
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Foundation model: mace_mp
    # - Model size: small
    # - Use dispersion via ASE: n
    # - Temperature: 300
    # - Pressure: 1.0
    # - Thermostat: Langevin
    # - Number of steps: 20
    # - Write interval: 10
    # - Timestep: 0.5
    # - Log interval: 10
    # - Print ext trajectory: y
    # - Simulation environment: ASE
    cd ../..

    # For multi-configuration molecular dynamics
    mkdir -p mace/MULTI_MD
    cd mace/MULTI_MD
    amaceing_mace
    # Then answer the prompts:
    # - Run type: MULTI_MD
    # - Project name: 4koh_92h2o_multimd
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Number of configurations: 3
    # - For Configuration 1:
    #   - Foundation model: mace_mp
    #   - Model size: small
    #   - Use dispersion via ASE: n
    # - For Configuration 2:
    #   - Foundation model: mace_mp
    #   - Model size: medium
    #   - Use dispersion via ASE: n
    # - For Configuration 3:
    #   - Foundation model: mace_off
    #   - Model size: small
    #   - Use dispersion via ASE: n
    # - Temperature: 300
    # - Pressure: 1.0
    # - Thermostat: Langevin
    # - Number of steps: 10
    # - Write interval: 1
    # - Timestep: 0.5
    # - Log interval: 1
    # - Print ext trajectory: y
    # - Simulation environment: ASE
    cd ../..

    # For fine-tuning
    mkdir -p mace/FINETUNE
    cd mace/FINETUNE
    amaceing_mace
    # Then answer the prompts:
    # - Run type: FINETUNE
    # - Project name: 4koh_92h2o_ft
    # - Training file: ../../data/train_file.xyz
    # - Device: cuda
    # - Stress weight: 0.0
    # - Forces weight: 10.0
    # - Energy weight: 0.1
    # - Foundation model: mace_mp
    # - Model size: small
    # - Prevent catastrophic forgetting: n
    # - Batch size: 5
    # - Validation fraction: 0.1
    # - Validation batch size: 2
    # - Max epochs: 2
    # - Random seed: 1
    # - Learning rate: 0.01
    # - XC functional of dataset: BLYP
    # - Models directory: MACE_models
    cd ../..

    # For reference trajectory recalculation
    mkdir -p mace/RECALC
    cd mace/RECALC
    amaceing_mace
    # Then answer the prompts:
    # - Run type: RECALC
    # - Project name: 4koh_92h2o_recalc
    # - Coordinate file: ../../data/dft_energies.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Foundation model: mace_mp
    # - Model size: small
    # - Use dispersion via ASE: n
    # - Simulation environment: ASE
    cd ../..

After running these examples, each calculation will generate appropriate Python scripts, configuration files, and runscripts. The file structure will include:

.. code-block:: none

    mace/
    ├── GEO_OPT/
    │   ├── geoopt_mace.py          # Python script for geometry optimization
    │   ├── runscript.sh            # CPU runscript
    │   ├── gpu_script.job          # GPU runscript
    │   └── mace_input.log          # Log of configuration parameters
    ├── MD/
    │   ├── md_mace.py              # Python script for molecular dynamics
    │   ├── runscript.sh            # CPU runscript
    │   ├── gpu_script.job          # GPU runscript
    │   └── mace_input.log
    ├── MULTI_MD/
    │   ├── md_mace_1/              # Directory for first configuration
    │   │   ├── md_mace.py
    │   │   ├── runscript.sh
    │   │   └── gpu_script.job
    │   ├── md_mace_2/              # Directory for second configuration
    │   ├── md_mace_3/              # Directory for third configuration
    │   └── mace_input.log
    ├── FINETUNE/
    │   ├── config_4koh_92h2o_ft.yml  # Configuration file for fine-tuning
    │   ├── finetune_mace.py         # Fine-tuning script
    │   ├── gpu_script.job           # GPU runscript
    │   └── mace_input.log
    └── RECALC/
        ├── recalc_mace.py          # Script for trajectory recalculation
        ├── gpu_script.job          # GPU runscript
        └── mace_input.log


MatterSim Examples
~~~~~~~~~~~~~~~~~~

The ``mattersim_test.sh`` script demonstrates four different types of MatterSim calculations:

1. **Molecular Dynamics**: Runs an MD simulation using a MatterSim model
2. **Multi-Configuration MD**: Runs multiple MD calculations with different foundation models
3. **Fine-tuning**: Fine-tunes a MatterSim foundation model with custom data
4. **Reference Trajectory Recalculation**: Recomputes energies and forces along a reference trajectory

You can run all MatterSim examples at once with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/mattersim_test.sh

To run these examples manually using Q&A sessions instead of command line parameters:

.. code-block:: bash

    # For molecular dynamics
    mkdir -p mattersim/MD
    cd mattersim/MD
    amaceing_mattersim
    # Then answer the prompts:
    # - Run type: MD
    # - Project name: 4koh_92h2o_md
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Foundation model: large
    # - Temperature: 300
    # - Pressure: 1.0
    # - Thermostat: Langevin
    # - Number of steps: 10
    # - Write interval: 10
    # - Timestep: 0.5
    # - Log interval: 100
    # - Print ext trajectory: y
    cd ../..

    # For multi-configuration molecular dynamics
    mkdir -p mattersim/MULTI_MD
    cd mattersim/MULTI_MD
    amaceing_mattersim
    # Then answer the prompts:
    # - Run type: MULTI_MD
    # - Project name: 4koh_92h2o_md
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Number of configurations: 2
    # - For Configuration 1:
    #   - Foundation model: small
    # - For Configuration 2:
    #   - Foundation model: large
    # - Temperature: 300
    # - Pressure: 1.0
    # - Thermostat: Langevin
    # - Number of steps: 10
    # - Write interval: 10
    # - Timestep: 0.5
    # - Log interval: 100
    # - Print ext trajectory: y
    cd ../..

    # For fine-tuning
    mkdir -p mattersim/FINETUNE
    cd mattersim/FINETUNE
    amaceing_mattersim
    # Then answer the prompts:
    # - Run type: FINETUNE
    # - Project name: 4koh_92h2o_ft
    # - Training data path: ../../data/train_file_trainset.xyz
    # - Device: cuda
    # - Force loss ratio: 10.0
    # - Load model path: small
    # - Batch size: 5
    # - Save checkpoint: y
    # - Checkpoint interval: 25
    # - Epochs: 200
    # - Random seed: 1
    # - Learning rate: 0.01
    # - Save path: MatterSim_models
    cd ../..

    # For reference trajectory recalculation
    mkdir -p mattersim/RECALC
    cd mattersim/RECALC
    amaceing_mattersim
    # Then answer the prompts:
    # - Run type: RECALC
    # - Project name: 4koh_92h2o_recalc
    # - Coordinate file: ../../data/dft_energies.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Foundation model: large
    cd ../..

After running these examples, each calculation will generate appropriate Python scripts, configuration files, and runscripts. The file structure will include:

.. code-block:: none

    mattersim/
    ├── MD/
    │   ├── md_mattersim.py          # Python script for molecular dynamics
    │   ├── runscript.sh             # CPU runscript
    │   ├── gpu_script.job           # GPU runscript
    │   └── mattersim_input.log      # Log of configuration parameters
    ├── MULTI_MD/
    │   ├── md_mattersim_1/          # Directory for first configuration
    │   │   ├── md_mattersim.py
    │   │   ├── runscript.sh
    │   │   └── gpu_script.job
    │   ├── md_mattersim_2/          # Directory for second configuration
    │   └── mattersim_input.log
    ├── FINETUNE/
    │   ├── finetune_mattersim.py    # Fine-tuning script
    │   ├── gpu_script.job           # GPU runscript
    │   └── mattersim_input.log
    └── RECALC/
        ├── recalc_mattersim.py      # Script for trajectory recalculation
        ├── gpu_script.job           # GPU runscript
        └── mattersim_input.log

SevenNet Examples
~~~~~~~~~~~~~~~~~

The ``sevennet_test.sh`` script demonstrates four different types of SevenNet calculations:

1. **Molecular Dynamics**: Runs an MD simulation using a SevenNet model
2. **Multi-Configuration MD**: Runs multiple MD calculations with different foundation models
3. **Fine-tuning**: Currently marked as "NOT IMPLEMENTED YET" in the script
4. **Reference Trajectory Recalculation**: Recomputes energies and forces along a reference trajectory

You can run all SevenNet examples at once with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/sevennet_test.sh

To run these examples manually using Q&A sessions instead of command line parameters:

.. code-block:: bash

    # For molecular dynamics
    mkdir -p sevennet/MD
    cd sevennet/MD
    amaceing_sevennet
    # Then answer the prompts:
    # - Run type: MD
    # - Project name: 4koh_92h2o_md
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Foundation model: 7net-mf-ompa
    # - Modal: mpa
    # - Use dispersion via ASE: n
    # - Temperature: 300
    # - Pressure: 1.0
    # - Thermostat: Langevin
    # - Number of steps: 10
    # - Write interval: 10
    # - Timestep: 0.5
    # - Log interval: 10
    # - Print ext trajectory: y
    cd ../..

    # For multi-configuration molecular dynamics
    mkdir -p sevennet/MULTI_MD
    cd sevennet/MULTI_MD
    amaceing_sevennet
    # Then answer the prompts:
    # - Run type: MULTI_MD
    # - Project name: 4koh_92h2o_md
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Number of configurations: 2
    # - For Configuration 1:
    #   - Foundation model: 7net-0
    #   - Modal: (leave empty)
    #   - Use dispersion via ASE: n
    # - For Configuration 2:
    #   - Foundation model: 7net-mf-ompa
    #   - Modal: mpa
    #   - Use dispersion via ASE: n
    # - Temperature: 300
    # - Pressure: 1.0
    # - Thermostat: Langevin
    # - Number of steps: 10
    # - Write interval: 10
    # - Timestep: 0.5
    # - Log interval: 10
    # - Print ext trajectory: y
    cd ../..

    # For fine-tuning
    mkdir -p sevennet/FINETUNE
    cd sevennet/FINETUNE
    amaceing_sevennet
    # Then answer the prompts:
    # - Run type: FINETUNE
    # - Project name: 4koh_92h2o_ft
    # - Training data path: ../../data/train_file_7net.xyz
    # - Foundation model: 7net-0
    # - Batch size: 4
    # - Epochs: 200
    # - Random seed: 1
    # - Learning rate: 0.01
    cd ../..

    # For reference trajectory recalculation
    mkdir -p sevennet/RECALC
    cd sevennet/RECALC
    amaceing_sevennet
    # Then answer the prompts:
    # - Run type: RECALC
    # - Project name: 4koh_92h2o_recalc
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Foundation model: 7net-mf-ompa
    # - Modal: mpa
    # - Use dispersion via ASE: n
    cd ../..

After running these examples, each calculation will generate appropriate Python scripts, configuration files, and runscripts. The file structure will include:

.. code-block:: none

    sevennet/
    ├── MD/
    │   ├── md_sevennet.py          # Python script for molecular dynamics
    │   ├── runscript.sh            # Runscript
    │   └── sevennet_input.log      # Log of configuration parameters
    ├── MULTI_MD/
    │   ├── md_sevennet_1/          # Directory for first configuration
    │   │   ├── md_sevennet.py
    │   │   └── runscript.sh
    │   ├── md_sevennet_2/          # Directory for second configuration
    │   └── sevennet_input.log
    ├── FINETUNE/
    │   ├── finetune_sevennet.py    # Fine-tuning script
    │   ├── gpu_script.job          # GPU runscript
    │   └── sevennet_input.log  
    └── RECALC/
        ├── recalc_sevennet.py      # Script for trajectory recalculation
        ├── runscript.sh            # Runscript
        └── sevennet_input.log

Note that SevenNet models have specific naming conventions:
* 7net-0: Base SevenNet model
* 7net-mf-ompa: Multi-fidelity organic-materials/properties-average model
* The "modal" parameter refers to the specific modal variant (mpa = materials/properties average)

Utility Examples
~~~~~~~~~~~~~~~~

The ``utils_test.sh`` script demonstrates six different utilities that help with various aspects of molecular dynamics workflows:

1. **Model Error Evaluation (EVAL_ERROR)**: Calculates errors between reference (DFT) data and ML model predictions
2. **Trajectory Preparation (PREPARE_EVAL_ERROR)**: Prepares files for CP2K reference calculations from trajectory data
3. **Frame Extraction (EXTRACT_XYZ)**: Extracts every nth frame from a trajectory file
4. **Citation Generation (MACE_CITATIONS)**: Generates proper citations for the models used
5. **Benchmarking (MD mode)**: Sets up multiple ML model simulations with identical starting conditions
6. **Benchmarking (RECALC mode)**: Sets up recalculations of a reference trajectory with multiple ML models

You can run all utilities examples at once with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/4KOH_92H2O_333K/utils_test.sh

To run these examples manually using Q&A sessions instead of command line parameters:

.. code-block:: bash

    # For model error evaluation
    mkdir -p utils/EVAL_ERROR
    cd utils/EVAL_ERROR
    amaceing_utils
    # Then answer the prompts:
    # - Function to use: EVAL_ERROR
    # - Ground truth energy file: ../../data/dft_energies.xyz
    # - Ground truth force file: ../../data/dft_forces.xyz
    # - Model energy file: ../../data/mace_energies.txt
    # - Model force file: ../../data/mace_forces.xyz
    cd ../..

    # For trajectory preparation
    mkdir -p utils/PREPARE_EVAL_ERROR
    cd utils/PREPARE_EVAL_ERROR
    amaceing_utils
    # Then answer the prompts:
    # - Function to use: PREPARE_EVAL_ERROR
    # - Trajectory file: ../../data/trajectory.traj
    # - Extract every nth frame: 1
    # - Start CP2K reference calculations: y
    # - Log file with information about the model: ../../data/mace_input.log
    # - XC functional used in reference calculations: BLYP
    cd ../..

    # For frame extraction
    mkdir -p utils/EXTRACT_XYZ
    cd utils/EXTRACT_XYZ
    amaceing_utils
    # Then answer the prompts:
    # - Function to use: EXTRACT_XYZ
    # - Coordinate file: ../../data/ref_trajectory.xyz
    # - Extract every nth frame: 2
    cd ../..

    # For citation generation
    mkdir -p utils/MACE_CITATIONS
    cd utils/MACE_CITATIONS
    amaceing_utils
    # Then answer the prompts:
    # - Function to use: MACE_CITATIONS
    # - Log file: ../../data/mace_input.log
    cd ../..

    # For benchmarking (MD mode)
    mkdir -p utils/BENCHMARK_MD
    cd utils/BENCHMARK_MD
    amaceing_utils
    # Then answer the prompts:
    # - Function to use: BENCHMARK
    # - Benchmark mode: MD
    # - Coordinate file: ../../data/system.xyz
    # - Cell dimensions: 14.2067 0 0 0 14.2067 0 0 0 14.2067
    # - Number of steps: 10
    # - MACE model to use: mace_mp
    # - MACE model size: small
    # - MatterSim model to use: large
    # - SevenNet model to use: 7net-mf-ompa
    # - SevenNet modal: mpa
    cd ../..

After running these examples, each utility will produce different outputs:

.. code-block:: none

    utils/
    ├── EVAL_ERROR/
    │   └── errors.txt              # Statistical error analysis
    ├── PREPARE_EVAL_ERROR/
    │   ├── mace_coord.xyz          # Extracted coordinates
    │   ├── mace_force.xyz          # Extracted forces
    │   ├── pbc                     # PBC file
    │   └── cp2k_geopt_run.inp      # CP2K input for reference calculations
    ├── EXTRACT_XYZ/
    │   └── ref_trajectory_every_2.xyz  # Trajectory with extracted frames
    ├── MACE_CITATIONS/
    │   └── citations.txt           # BibTeX citations
    ├── BENCHMARK_MD/
    │   ├── mace/                   # MACE benchmark files
    │   ├── mattersim/             # MatterSim benchmark files
    │   └── sevennet/              # SevenNet benchmark files
    └── BENCHMARK_RECALC/
        ├── mace/                   # MACE recalculation files
        ├── mattersim/             # MatterSim recalculation files
        └── sevennet/              # SevenNet recalculation files

These utilities help with common tasks in the ML-potential workflow, such as:

* Evaluating model accuracy against DFT references
* Preparing training data from trajectories
* Creating smaller trajectory files for visualization
* Setting up benchmarks to compare different ML potentials
* Generating proper citations for publications


Next Steps
----------

After running these examples, you can:

1. Examine the generated input files to understand their structure
2. Modify parameters to test different simulation conditions
3. Run the generated scripts on your computational resources
4. Analyze the results with ``amaceing_ana``