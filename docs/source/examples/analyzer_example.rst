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

    amaceing_ana -f="trajectory.xyz" -p="pbc.dat" -t="0.5" -v="y" -r="O-H,O-O" -m="O,H"

Python API Example
``````````````````

.. code-block:: python

    from amaceing_toolkit.workflow import analyzer_api
    
    config = {
        'traj_file': 'trajectory.xyz',
        'pbc_file': 'pbc.dat',
        'timestep': 0.5,
        'analysis_types': ['rdf', 'msd'],
        'rdf_pairs': [['O', 'H'], ['O', 'O']],
        'msd_atoms': ['O', 'H'],
        'visualize': True
    }
    
    results = analyzer_api(config=config)

Generated Files
```````````````

For RDF analysis:

- ``rdf_O-H.csv``: Raw RDF data for O-H pairs
- ``rdf_O-O.csv``: Raw RDF data for O-O pairs
- ``rdf_O-H.png``: Plot of O-H RDF
- ``rdf_O-O.png``: Plot of O-O RDF

For MSD analysis:

- ``msd_O.csv``: Raw MSD data for oxygen atoms
- ``msd_H.csv``: Raw MSD data for hydrogen atoms
- ``msd.png``: Plot of MSD curves
- ``diffusion_coefficients.csv``: Calculated diffusion coefficients

Multiple Trajectory Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare properties across multiple trajectories.

Command Line Example
````````````````````

.. code-block:: bash

    amaceing_ana -f="traj1.xyz,traj2.xyz" -p="pbc1.dat,pbc2.dat" -t="0.5,0.5" -v="y" -r="O-H,O-O" -m="O,H"

Python API Example
``````````````````

.. code-block:: python

    from amaceing_toolkit.workflow import analyzer_api
    
    config = {
        'traj_files': ['traj1.xyz', 'traj2.xyz'],
        'pbc_files': ['pbc1.dat', 'pbc2.dat'],
        'timesteps': [0.5, 0.5],
        'analysis_types': ['rdf', 'msd'],
        'rdf_pairs': [['O', 'H'], ['O', 'O']],
        'msd_atoms': ['O', 'H'],
        'visualize': True,
        'labels': ['System 1', 'System 2']
    }
    
    results = analyzer_api(config=config)

Generated Files
```````````````

Similar to single trajectory analysis, but with comparative plots showing data from all trajectories on the same graphs.
