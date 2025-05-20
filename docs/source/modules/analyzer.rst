Analyzer Module
===============

Overview
--------

The Analyzer module is a powerful component of the aMACEing toolkit designed to analyze molecular dynamics trajectories. It provides tools for calculating fundamental physical properties and visualizing the results.

Analysis Capabilities
---------------------

The Analyzer supports the following types of analyses:

Radial Distribution Function (RDF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Calculates the probability of finding particles at a specific distance from a reference particle
* Helps identify structural organization in systems
* Automatically proposes relevant atom pairs based on system composition

Mean Square Displacement (MSD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Measures how far atoms move from their initial positions
* Used to calculate diffusion coefficients
* Identifies atomic mobility in the system

Single-particle Mean Square Displacement (sMSD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Tracks individual particle displacement rather than ensemble averages
* Identifies heterogeneous dynamics in the system
* Calculates diffusion coefficients for individual particles


Vector Autocorrelation Function (VACF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Measures the correlation of a particle's velocity over time
* Provides insights into the dynamics of the system

Usage
-----

The Analyzer can be used in two ways:

Q&A Session
~~~~~~~~~~~

Start an interactive Q&A session with:

.. code-block:: bash

    amaceing_ana

This guides you through:

1. Selecting trajectory files for analysis
2. Specifying periodic boundary conditions
3. Setting the timestep
4. Choosing which analyses to perform
5. Generating visualizations and reports

The Analyzer offers a "smart proposal" feature that automatically recommends analyses based on the atom types in your system.

Command-line Usage
~~~~~~~~~~~~~~~~~~

Analyze files directly with a single command:

.. code-block:: bash

    amaceing_ana -f="coord.xyz" -p="pbc.txt" -t="0.5" -v="y"

Parameters:

* ``-f, --file``: Path to the trajectory file(s) (comma-separated for multiple)
* ``-p, --pbc``: Path to the PBC file(s) (comma-separated for multiple)
* ``-t, --timestep``: Timestep in fs (comma-separated for multiple)
* ``-v, --visualize``: Whether to visualize results (y/n, default is y)

For multiple trajectory analysis:

.. code-block:: bash

    amaceing_ana -f="traj1.xyz,traj2.xyz" -p="pbc1.txt,pbc2.txt" -t="0.5,1.0" -v="y"

Output and Visualization
------------------------

The Analyzer produces:

* CSV files with numerical results
* Publication-quality plots for each analysis
* Automatic calculation of diffusion coefficients from MSD data
* Statistical analysis of sMSD results
* A comprehensive LaTeX report summarizing all results

Technical Details
-----------------

* Diffusion coefficients are calculated by fitting the MSD curve in the time range 10-30 ps
* For sMSD analysis, statistics include mean, standard deviation, median, and the five highest diffusion coefficients
* The Analyzer automatically handles periodic boundary conditions
* Multiple trajectory analysis allows for direct comparison between different simulations
