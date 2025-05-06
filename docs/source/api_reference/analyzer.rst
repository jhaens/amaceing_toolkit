Analyzer API
===========

The Analyzer API provides functions for analyzing trajectory data from molecular dynamics simulations.

Function Reference
-----------------

.. py:function:: amaceing_toolkit.analyzer_api(file=None, pbc=None, timestep=None, visualize=None)

   API function for trajectory analysis.
   
   :param file: Path to trajectory file(s), comma separated for multiple files
   :type file: str, optional
   :param pbc: Path to PBC file(s), comma separated for multiple files
   :type pbc: str, optional
   :param timestep: Timestep in fs
   :type timestep: float, optional
   :param visualize: Whether to generate visualization (\'y\' or \'n\')
   :type visualize: str, optional
   :returns: None - Creates analysis files and plots in the current directory
   
   **Examples**::
   
       from amaceing_toolkit import analyzer_api
       
       # Analyze a single trajectory
       analyzer_api(
           file='traj.xyz', 
           pbc='pbc_file', 
           timestep=0.5, 
           visualize='y'
       )
       
       # Analyze multiple trajectories
       analyzer_api(
           file='traj1.xyz,traj2.xyz,traj3.xyz', 
           pbc='pbc_file1,pbc_file2,pbc_file3', 
           timestep=0.5, 
           visualize='y'
       )

Analysis Features
----------------

The analyzer provides the following analysis features:

- Single Trajectory Analysis
- Multiple Trajectory Analysis
- Radial distribution function (RDF)
- Mean square displacement (MSD)
- Single particle mean square displacement (sMSD)
- Visualization of analysis results
