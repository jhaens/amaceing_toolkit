4KOH_92H2O Example
==================

.. toctree::
   :maxdepth: 1
   :caption: Example Framework Implementations

   ./cp2k
   ./mace
   ./mattersim
   ./sevennet
   ./orb
   ./grace
   ./utils

Overview
--------

This example demonstrates the capabilities of the aMACEing toolkit with a system containing 4 potassium hydroxides (4 KOH) and 92 water molecules at 333 K. This system represents a dilute basic solution relevant for studying proton transfer and hydroxide solvation dynamics in aqueous environments.

The example showcases comprehensive workflows for setting up and analyzing various types of calculations using multiple simulation engines: CP2K, MACE, MatterSim, SevenNet, and ORB. The calculation types include:

* Geometry optimization (GEO_OPT)
* Cell optimization (CELL_OPT)
* Molecular dynamics simulations (MD)
* Multi-model molecular dynamics (MULTI_MD)
* Reference trajectory recalculation (REFTRAJ)
* Single-point energy calculations (ENERGY)
* Fine-tuning of machine learning potentials (FINETUNE)
* Multi-head fine-tuning for multiple datasets (FINETUNE_MULTIHEAD)
* Energy recalculation for trajectory analysis (RECALC)

System Structure
----------------

The example is organized with the following directory structure:

.. code-block:: none

    4KOH_92H2O_333K/
    ├── data/
    │   ├── system.xyz            # Initial structure file (4 KOH + 92 H2O)
    │   ├── ref_trajectory.xyz    # Reference trajectory for recalculation
    │   ├── train_file.xyz        # Training file with positions, energies, forces
    │   ├── train_file2.xyz       # Secondary training file for multi-head fine-tuning
    │   ├── train_file_7net.xyz   # Training file formatted for SevenNet/ORB
    │   ├── dft_energies.xyz      # DFT-calculated energies for structures
    │   └── other auxiliary files
    ├── cp2k_test.sh              # CP2K examples script
    ├── mace_test.sh              # MACE examples script
    ├── mattersim_test.sh         # MatterSim examples script
    ├── sevennet_test.sh          # SevenNet examples script
    ├── orb_test.sh               # ORB examples script
    ├── grace_test.sh             # Grace examples script
    └── utils_test.sh             # Utilities examples script

Each test script demonstrates comprehensive functionality for the respective simulation engine with the 4KOH_92H2O system. The scripts create separate directories for each calculation type and generate the appropriate input files.

Select a specific framework from the navigation to see detailed examples for that framework.
