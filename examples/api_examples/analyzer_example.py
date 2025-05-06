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
    # Create a copy of the trajectory file to use for our example
    os.makedirs("ana_single", exist_ok=True)
    os.chdir("ana_single")
    
    # Create a copy of an existing trajectory file for analysis
    try:
        shutil.copy('../../../tutorials/data/traj.xyz', 'trajectory.xyz')
        # Create a sample PBC file if it doesn't exist
        with open('pbc_file', 'w') as f:
            f.write("10.0 10.0 10.0\n")  # Sample PBC values
    except:
        print("Failed to copy trajectory file. Make sure it exists.")
        return
    
    print("----------------------------")
    print("Running single trajectory analyzer example")
    # The analyzer API takes separate parameters instead of a config dict
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
        shutil.copy('../../../tutorials/data/traj.xyz', 'trajectory1.xyz')
        shutil.copy('../../../tutorials/data/traj.xyz', 'trajectory2.xyz')
        # Create sample PBC files
        with open('pbc_file1', 'w') as f:
            f.write("10.0 10.0 10.0\n")  # Sample PBC values
        with open('pbc_file2', 'w') as f:
            f.write("12.0 12.0 12.0\n")  # Different sample PBC values
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
    print("----------------------------")
    print("Analyzer API examples completed")

if __name__ == "__main__":
    main()