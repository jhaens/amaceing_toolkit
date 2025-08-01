#!/usr/bin/env python3
"""
Example script demonstrating how to use the Analyzer API from amaceing_toolkit.
This script adapts the functionality in the analyzer_test.sh example file to use available files.
"""
import os
import subprocess
import shutil
from amaceing_toolkit.workflow import analyzer_api

def main():
    # Downloading the example trajectories
    if not os.path.exists("koh1.xyz"):
        print("""Please download the following files to the current directory for the examples to work:
        - wget https://cloud.tu-ilmenau.de/s/wDRecAYSpPxXiZk/download/koh1.xyz
        - wget https://cloud.tu-ilmenau.de/s/wRCLg2pBwbCpN6p/download/koh2.xyz
        """) 
        exit(1)

    # Create a copy of the trajectory file to use for our example
    os.makedirs("ana_single", exist_ok=True)
    os.chdir("ana_single")
    
    # Create a copy of an existing trajectory file for analysis
    try:
        shutil.copy('../koh1.xyz', 'trajectory.xyz')
        # Create a sample PBC file if it doesn't exist
        with open('pbc_file', 'w') as f:
            f.write("14.20 0.0 0.0 0.0 14.20 0.0 0.0 0.0 14.20\n")  # Sample PBC values
    except:
        print("Failed to copy trajectory file. Make sure it exists.")
        return
    
    print("----------------------------")
    print("Running single trajectory analyzer example")
    # The analyzer API now returns True/False to indicate success
    analyzer_api(
        file="trajectory.xyz",
        pbc="pbc_file",
        timestep=50.0,
        visualize="y"
    )
    
    # Compile the LaTeX document if available
    try:
        subprocess.run(["pdflatex", "analysis.tex"], check=False)
        subprocess.run(["pdflatex", "analysis.tex"], check=False)  # Run twice for references
    except FileNotFoundError:
        print("pdflatex not found. Skipping PDF generation.")

    os.chdir("..")  # Go back to root directory
    
    # Create directory for multi-trajectory analysis
    os.makedirs("ana_multi", exist_ok=True)
    os.chdir("ana_multi")
    
    # Create copies of trajectory files for multi-trajectory analysis
    try:
        shutil.copy('../koh1.xyz', 'trajectory1.xyz')
        shutil.copy('../koh2.xyz', 'trajectory2.xyz')
        # Create sample PBC files
        with open('pbc_file1', 'w') as f:
            f.write("14.20 0.0 0.0 0.0 14.20 0.0 0.0 0.0 14.20\n")  # Sample PBC values
        with open('pbc_file2', 'w') as f:
            f.write("14.20 0.0 0.0 0.0 14.20 0.0 0.0 0.0 14.20\n")  # Different sample PBC values
    except:
        print("Failed to create trajectory files. Make sure source files exist.")
        return
    
    print("----------------------------")
    print("Running multi-trajectory analyzer example")
    analyzer_api(
        file="trajectory1.xyz,trajectory2.xyz",  # Comma-separated files
        pbc="pbc_file1,pbc_file2",              # Comma-separated pbc files
        timestep="50.0,50.0",                   # Comma-separated timesteps
        visualize="y"
    )
    
    # Compile the LaTeX document if available
    try:
        subprocess.run(["pdflatex", "analysis.tex"], check=False)
        subprocess.run(["pdflatex", "analysis.tex"], check=False)  # Run twice for references
    except FileNotFoundError:
        print("pdflatex not found. Skipping PDF generation.")
    
    os.chdir("..")  # Go back to root directory
    
    # Create directory for advanced analysis
    os.makedirs("ana_advanced", exist_ok=True)
    os.chdir("ana_advanced")
    
    # Create copies of trajectory files for advanced analysis
    try:
        shutil.copy('../koh1.xyz', 'trajectory.xyz')
        with open('pbc_file', 'w') as f:
            f.write("14.20 0.0 0.0 0.0 14.20 0.0 0.0 0.0 14.20\n")  # Sample PBC values
    except:
        print("Failed to create trajectory files. Make sure source files exist.")
        return
    
    print("----------------------------")
    print("Running advanced analysis with config dictionary")
    
    # Use a config dictionary with advanced options
    config = {
        'file': 'trajectory.xyz',
        'pbc': 'pbc_file',
        'timestep': 50.0,
        'visualize': 'y',
        'rdf_pairs': ['O-H', 'O-O'],
        'msd_list': ['H', 'O'],
        'smsd_list': ['H', 'O'],
        'autocorr_pairs': ['O-H', 'O-O'],
        'drift_corr': 'y',
        'fold_back': 'y',
        'h_bonds': 'y'
    }
    
    analyzer_api(config=config)
    
    # Compile the LaTeX document if available
    try:
        subprocess.run(["pdflatex", "analysis.tex"], check=False)
        subprocess.run(["pdflatex", "analysis.tex"], check=False)  # Run twice for references
    except FileNotFoundError:
        print("pdflatex not found. Skipping PDF generation.")
        
    os.chdir("..")  # Go back to root directory
    print("----------------------------")
    print("Analyzer API examples completed")

if __name__ == "__main__":
    main()