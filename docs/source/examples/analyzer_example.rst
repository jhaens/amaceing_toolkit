Analyzer Examples
=================

This section demonstrates how to use the Analyzer module for trajectory analysis. The Analyzer provides tools for computing physical properties from molecular dynamics trajectories and visualizing the results.

Basic Usage
-----------

Single Trajectory Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~

Analyze a single trajectory with RDF and MSD calculations.

Command Line Example
````````````````````

.. code-block:: bash

    amaceing_ana --file=../data/koh1.xyz --pbc=../data/pbc_koh1 --timestep=50.0 --visualize=y --rdf_pairs=O-O,O-H --msd_list=H

Python API Example
``````````````````

.. code-block:: python

    from amaceing_toolkit.workflow import analyzer_api
    
    config = {
        file="trajectory.xyz",
        pbc="pbc_file",
        timestep=50.0,
        visualize="y",
        rdf_pairs="O-H,O-O",
        msd_list="H"
    }
    
    analyzer_api(config=config)

Generated Files in /ana_koh
```````````````````````````

For RDF analysis:

- ``koh1_ana/rdf_OH.csv``: Raw RDF data for O-H pairs
- ``koh1_ana/rdf_OO.csv``: Raw RDF data for O-O pairs
- ``rdf_OH.png``: Plot of O-H RDF
- ``rdf_OO.png``: Plot of O-O RDF

For MSD analysis:

- ``koh1_ana/msd_H.csv``: Raw MSD data for hydrogen atoms
- ``koh1_ana/diff_coeff_H.csv``: Calculated diffusion coefficients for hydrogen atoms
- ``msd_H_plot.png``: Plot of MSD curves
- ``overview_diffcoeff.csv``: Calculated diffusion coefficients

General File:

- ``input_analysis.log``: aMACEing_toolkit analysis log file

Visualizing Results:

- ``analysis.tex``: LaTeX file for compiling the analysis report
- ``analysis.pdf``: Compiled PDF report of the analysis 
- ``/img_dir``: Directory containing all generated images


Multiple Trajectory Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare properties across multiple trajectories.

Command Line Example
````````````````````

.. code-block:: bash

    amaceing_ana --file=../data/koh1.xyz,../data/koh2.xyz --pbc=../data/pbc_koh1,../data/pbc_koh2 --timestep=50.0,50.0 --visualize=y

Python API Example
``````````````````

.. code-block:: python

    from amaceing_toolkit.workflow import analyzer_api
    
    config = {
        file="trajectory1.xyz,trajectory2.xyz",  # Comma-separated files
        pbc="pbc_file1,pbc_file2",               # Comma-separated pbc files
        timestep="50.0,50.0",                    # Comma-separated timesteps
        visualize="y"
    }
    
    analyzer_api(config=config)

Generated Files
```````````````

Similar to single trajectory analysis (additionally including MSD for oxygen atoms), but with comparative plots showing data from all trajectories on the same graphs.
