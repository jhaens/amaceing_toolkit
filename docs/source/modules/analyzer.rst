Analyzer Module
===============

The Analyzer module provides high-performance tools for molecular dynamics trajectory analysis. It combines Python interface logic with C++ computational backends to deliver efficient calculations of key physical properties from simulation trajectories.


Analysis Methods
----------------

Radial Distribution Function (RDF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The RDF (or pair correlation function) g(r) describes how the atomic density varies as a function of distance from a reference particle:

.. math::

   g_{ab}(r)= \dfrac{V}{N_{a} \cdot N_{b}} \displaystyle \sum_{i=1}^{N_{a}} \displaystyle \sum_{j=i+1}^{N_{b}} \langle \delta(r - \left\vert \vec{r}_{i}(t) - \vec{r}_{j}(t) \right\vert) \rangle _{t}

Where:
- ρ is the average number density
- n(r) is the number of atoms in a shell of width Δr at distance r

Implementation features:

* Bin-based histogram calculation with configurable resolution
* Automatic normalization for correct physical interpretation
* Support for arbitrary atom pairs
* Multiple RDFs can be calculated in a single analysis run
* Handles periodic boundary conditions correctly

Mean Square Displacement (MSD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The MSD measures how far atoms travel from their initial positions as a function of time:

.. math::

   \text{MSD}(t) = \left\langle |r_i(t+\tau) - r_i(t)|^2 \right\rangle_{t,i}

Where:
- r_i(t) is the position of atom i at time t
- The average is taken over all atoms of a given type

Implementation features:

* Automatic unwrapping of trajectories with periodic boundary conditions
* Calculation of diffusion coefficients using Einstein relation
* Supports multiple atom types in a single analysis run

Single-particle Mean Square Displacement (sMSD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sMSD tracks displacement for individual atoms rather than ensemble averages:

.. math::

   \text{sMSD}_i(t) = \left\langle |r_i(t+\tau) - r_i(t)|^2 \right\rangle_t

Implementation features:

* Statistical distribution of single-particle diffusion coefficients
* Identification of outlier particles with anomalous diffusion
* Supports multiple atom types in a single analysis run

Vector Autocorrelation Function (VACF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The VACF measures how a particle's velocity remains correlated with its initial velocity over time:

.. math::

   \text{VACF}(t) = \left\langle v_i(t) \cdot v_i(0) \right\rangle_i

Implementation features:

* Supports multiple atom pairs in a single analysis run


Usage
-----

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

**Interactive Q&A Mode**:

.. code-block:: bash

    amaceing_ana

This guides you through:

1. Selecting trajectory files (supports multiple files)
2. Defining periodic boundary conditions
3. Setting timestep values for each trajectory
4. Selecting which analyses to perform
5. Choosing atom types or pairs for each analysis
6. Configuring visualization options

**Direct Command Line Mode**:

.. code-block:: bash

    amaceing_ana -f="traj.xyz" -p="pbc.dat" -t="0.5" -v="y" -r="O-H,O-O" -m="O,H" -s="O" -a="O-H"

Parameters:

* ``-f, --file``: Path to trajectory file(s) (comma-separated for multiple)
* ``-p, --pbc``: Path to PBC file(s) (comma-separated for multiple)
* ``-t, --timestep``: Timestep in fs (comma-separated for multiple)
* ``-v, --visualize``: Whether to visualize (y/n)
* ``-r, --rdf_pairs``: Atom pairs for RDF analysis (comma-separated, format: atom1-atom2)
* ``-m, --msd_list``: Atoms for MSD analysis (comma-separated)
* ``-s, --smsd_list``: Atoms for single-particle MSD analysis (comma-separated)
* ``-a, --autocorr_pairs``: Pairs for vector autocorrelation (comma-separated, format: atom1-atom2)

Python API
~~~~~~~~~~

.. code-block:: python

    from amaceing_toolkit.workflow import analyzer_api
    
    # Configure the analysis
    config = {
        'traj_file': 'trajectory.xyz',
        'pbc_file': 'pbc.dat',
        'timestep': 0.5,
        'analysis_types': ['rdf', 'msd'],
        'rdf_pairs': [['O', 'H'], ['O', 'O']],
        'msd_atoms': ['O', 'H'],
        'visualize': True
    }
    
    # Run the analysis
    results = analyzer_api(config=config)

Input File Formats
------------------

**Trajectory Files**:

The analyzer accepts standard XYZ format trajectory files containing multiple frames:

.. code-block:: text

    N_atoms
    comment line
    atom_type_1 x1 y1 z1
    atom_type_2 x2 y2 z2
    ...
    N_atoms
    comment line
    atom_type_1 x1 y1 z1
    ...

**PBC Files**:

The PBC (periodic boundary condition) file format is a simple text file containing the simulation cell vectors:

.. code-block:: text

    A B C
    D E F
    G H I


Output and Visualization
------------------------

For each analysis type, the analyzer produces:

1. **Raw Data**:
   
   - CSV files containing the numerical results
   - Data is organized for easy import into other analysis tools

2. **Visualizations**:
   
   - Publication-quality plots generated using matplotlib
   - Automatic formatting and styling for clarity
   - PNG and PDF output formats

3. **Derived Quantities**:

   - Diffusion coefficients from MSD curves
   - Coordination numbers from RDF peaks
   - Correlation times from VACF decay

4. **LaTeX Report** (optional):

   - Comprehensive summary of all analyses
   - Tables of derived quantities
   - Embedded figures
   - Ready to compile for publication or presentations

* Diffusion coefficients are calculated by fitting the MSD curve in the time range 10-30 ps
* For sMSD analysis, statistics include mean, standard deviation, median, and the five highest diffusion coefficients
* The Analyzer automatically handles periodic boundary conditions
* Multiple trajectory analysis allows for direct comparison between different simulations
