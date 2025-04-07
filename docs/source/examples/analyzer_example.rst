Analyzer Example
================

Overview
--------

This example demonstrates the trajectory analysis capabilities of the aMACEing toolkit using the analyzer module (``amaceing_ana``). The example analyzes molecular dynamics trajectories of potassium hydroxide (KOH) solutions, showing how to calculate:

* Radial Distribution Functions (RDF) to identify structural characteristics
* Mean Square Displacement (MSD) to measure atomic mobility and diffusion coefficients
* Single-particle Mean Square Displacement (sMSD) to identify heterogeneous dynamics

The example includes both single trajectory analysis and comparative multi-trajectory analysis.

Example Data
------------

The example uses the following files in the ``examples/analyzer/data/`` directory:

* ``koh1.xyz`` - First KOH trajectory file in XYZ format
* ``koh2.xyz`` - Second KOH trajectory file for comparison
* ``pbc_koh1`` - Periodic boundary conditions for the first trajectory
* ``pbc_koh2`` - Periodic boundary conditions for the second trajectory

These files contain atomic positions from molecular dynamics simulations of KOH solutions.

Running the Examples with Bash Script
-------------------------------------

The ``analyzer_test.sh`` script demonstrates two types of analysis:

1. **Single Trajectory Analysis**: Analyzes one KOH trajectory file
2. **Multiple Trajectory Analysis**: Compares two KOH trajectory files

You can run the entire script with:

.. code-block:: bash

    bash /path/to/amaceing_toolkit/examples/analyzer/analyzer_test.sh

The script performs the following operations:

1. Creates a directory for single trajectory analysis (``ana_koh``)
2. Runs the analyzer with the first trajectory
3. Compiles a LaTeX report of the results
4. Creates a directory for multiple trajectory analysis (``ana_koh12``)
5. Runs the analyzer with both trajectories for comparison
6. Compiles a comparative LaTeX report

Running the Examples Manually
-----------------------------

You can run these examples manually using either command-line parameters or the interactive Q&A interface.

Single Trajectory Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Using Command Line Parameters:**

.. code-block:: bash

    mkdir -p ana_koh
    cd ana_koh
    amaceing_ana --file=../data/koh1.xyz --pbc=../data/pbc_koh1 --timestep=50.0 --visualize=y
    pdflatex analysis.tex
    pdflatex analysis.tex  # Run twice for proper table of contents

**Using Q&A Interface:**

.. code-block:: bash

    mkdir -p ana_koh
    cd ana_koh
    amaceing_ana
    # Then answer the prompts:
    # - Trajectory file: ../data/koh1.xyz
    # - Is the box cubic? pbc
    # - Enter path to PBC file: ../data/pbc_koh1
    # - Timestep in fs: 50.0
    # - How many trajectories: 1
    # 
    # You'll see available atom types and smart proposals:
    # - Choose to accept the smart proposal or configure manually
    # - For manual configuration, select analysis types (1=RDF, 2=MSD, 3=sMSD)
    #
    # For diffusion coefficient calculation:
    # - Calculate diffusion coefficients: y
    #
    # For visualization:
    # - Visualize the analysis: y
    #
    # Compile the LaTeX report:
    pdflatex analysis.tex
    pdflatex analysis.tex

Multiple Trajectory Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Using Command Line Parameters:**

.. code-block:: bash

    mkdir -p ana_koh12
    cd ana_koh12
    amaceing_ana --file=../data/koh1.xyz,../data/koh2.xyz --pbc=../data/pbc_koh1,../data/pbc_koh2 --timestep=50.0,50.0 --visualize=y
    pdflatex analysis.tex
    pdflatex analysis.tex

**Using Q&A Interface:**

.. code-block:: bash

    mkdir -p ana_koh12
    cd ana_koh12
    amaceing_ana
    # Then answer the prompts:
    # - Trajectory file: ../data/koh1.xyz
    # - Is the box cubic? pbc
    # - Enter path to PBC file: ../data/pbc_koh1
    # - Timestep in fs: 50.0
    # - How many trajectories: 2
    #
    # For the second trajectory:
    # - What should be the key for this trajectory: koh2
    # - Trajectory file: ../data/koh2.xyz
    # - Is the box cubic? pbc
    # - Enter path to PBC file: ../data/pbc_koh2
    # - Timestep in fs: 50.0
    #
    # Continue with analysis selection as in the single trajectory example
    #
    # Compile the LaTeX report:
    pdflatex analysis.tex
    pdflatex analysis.tex

Output and Results
------------------

After running the analysis, you'll get several output files:

**Data Files:**
* ``rdf_*.csv`` - Radial distribution function data
* ``msd_*.csv`` - Mean square displacement data
* ``smsd_*.csv`` - Single-particle mean square displacement data (if selected)
* ``overview_diffcoeff.csv`` - Summary of calculated diffusion coefficients
* ``diff_coeff_*.csv`` - Diffusion coefficients for individual atom types

**Visualization:**
* ``rdf_*_plot.pdf`` - RDF plots for different atom pairs
* ``msd_*_plot.pdf`` - MSD plots with diffusion coefficient fits
* ``smsd_*_plot.pdf`` - Single-particle MSD plots (if selected)

**LaTeX Report:**
* ``analysis.tex`` - LaTeX source for the comprehensive report
* ``analysis.pdf`` - Final PDF report with all analyses and results
* ``img_dir/`` - Directory containing all plots for the report

The PDF report includes:
* Analysis details and directory structure
* Diffusion coefficient tables (if MSD analysis was performed)
* RDF, MSD, and sMSD plots with captions
* Statistical summary of results

Smart Proposal Feature
----------------------

A key feature demonstrated in this example is the "smart proposal" system, which:

1. Automatically detects atom types in your trajectory
2. Suggests the most relevant RDF pairs based on the system composition
3. Proposes appropriate atom types for MSD analysis
4. Allows you to accept or refine these suggestions

This feature is especially useful for complex systems with many atom types, as it identifies the most scientifically relevant analyses based on the chemical composition.

Technical Notes
---------------

* The diffusion coefficients are calculated by fitting the MSD curve in the time range 10-30 ps
* For comparative analyses, the plots are automatically overlaid with different colors for easy comparison
* The LaTeX report includes a tree structure overview of all generated files
* The sMSD analysis (if performed) provides statistics including mean, standard deviation, median, and the five highest diffusion coefficients