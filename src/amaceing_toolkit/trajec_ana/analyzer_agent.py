import os
import numpy as np
import datetime
import sys
import signal
import argparse, textwrap
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


from amaceing_toolkit.workflow.utils import print_logo
from amaceing_toolkit.workflow.utils import cite_amaceing_toolkit
from amaceing_toolkit.workflow.utils import ask_for_float_int
from amaceing_toolkit.workflow.utils import ask_for_non_cubic_pbc
from amaceing_toolkit.workflow.utils import ask_for_int
from amaceing_toolkit.workflow.utils import ask_for_yes_no
from amaceing_toolkit.workflow.utils import ask_for_yes_no_pbc
from amaceing_toolkit.workflow.utils import xyz_reader
from .default_analyzer import compute_analysis


def atk_analyzer():
    """"
    This function is used to analyze the trajectory of a molecular dynamics simulation."
    """

    print_logo()

    # Decide if the user want automatic terminal execution or Q&A session
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Analyze trajectory files with aMACEing toolkit: (1) Via a short Q&A: NO arguments needed! (2) Directly from the command line: FOUR arguments needed!")
        parser.add_argument("-f", "--file", type=str, help="[OPTIONAL] Path to the trajectory file. (multiple paths are possible: coord1.xyz, coord2.xyz, coord3.xyz)")
        parser.add_argument("-p", "--pbc", type=str, help="[OPTIONAL] Path to the PBC file. (multiple paths are possible: pbc1, pbc2, pbc3)")
        parser.add_argument("-t", "--timestep", type=str, help="[OPTIONAL] Timestep in fs. (multiple values are possible: 0.5, 1.0, 2.0)")
        parser.add_argument("-v", "--visualize", type=str, default="y", help="[OPTIONAL] Visualize the analysis, default is 'y'. (y/n)")
        args = parser.parse_args()

        coord_file = args.file
        pbc = args.pbc
        timestep = args.timestep
        visualize = args.visualize

        print("")
        print("You selected the following parameters for the analysis: " + str(coord_file) + ", " + str(pbc) + ", " + str(timestep) + ", " + str(visualize))


        # Determine if the user provided multiple files
        if ',' in coord_file:
            # Multiple file analysis
            coord_file = coord_file.split(",")
            pbc = pbc.split(",")
            timestep = timestep.split(",")
            for i in range(len(coord_file)):
                coord_file[i] = coord_file[i].strip()
                pbc[i] = pbc[i].strip()
                timestep[i] = float(timestep[i])
                assert os.path.isfile(coord_file[i]), f"Coordinate file {coord_file[i]} does not exist!"
                assert os.path.isfile(pbc[i]), f"PBC file {pbc[i]} does not exist!"
                if i == 0:
                    all_avail_atomtypes = available_atomtypes(coord_file[i])
                else:
                    avail_atomtypes = available_atomtypes(coord_file[i])
                    all_avail_atomtypes = list(set(all_avail_atomtypes) & set(avail_atomtypes))
        
        else:
            # Single file analysis
            if not os.path.isfile(coord_file):
                print(f"Error: The file {coord_file} does not exist.")
                sys.exit(1)
            if not os.path.isfile(pbc):
                print(f"Error: The PBC file {pbc} does not exist.")
                sys.exit(1)
            timestep = [float(timestep)]
            all_avail_atomtypes = available_atomtypes(coord_file)
            pbc = [pbc]
            coord_file = [coord_file]
        
        # Do smart proposal
        msd_list, rdf_pairs = smart_proposal(all_avail_atomtypes)
        print("")
        print("The analysis plan (based on smart_proposal) considering the available atom types in the coordinate file(s):")
        print(" ==> Radial distribution function of: " + str(rdf_pairs))
        print(" ==> Mean square displacement of: " + str(msd_list))
        print("")
        # Do not calculate smsd autocorrelation via the one-line teriminal command
        smsd_list = []
        autocorr_pairs = []

        # Name the analyses
        ana_names = []
        for i in range(len(coord_file)):
            name_tmp = coord_file[i].split("/")[-1]
            name_tmp = name_tmp.split(".")[0]
            ana_names.append(f"{name_tmp}_ana")

        
        # Calculate the analysis
        for i in range(len(coord_file)):
            # Save pbcs to a .txt file
            pbc_content = np.loadtxt(pbc[i])
            np.savetxt(f'pbc_{i}.txt', pbc_content)
            pbc[i] = f'pbc_{i}.txt' 
            analysis_folder(ana_names[i])
            coord_file[i] = path_checker(coord_file[i])
            pbc[i] = path_checker(pbc[i])
            print("")
            print("Starting analysis of " + str(coord_file[i]) + "...")
            start_time = datetime.datetime.now()
            print("Analysis started at: " + str(start_time.strftime("%H:%M:%S")))
            timestep[i] = float(timestep[i])  # Ensure timestep is explicitly cast to float
            compute_analysis(coord_file[i], pbc[i], timestep[i], rdf_pairs, msd_list, smsd_list, autocorr_pairs)
            end_time = datetime.datetime.now()
            duration = end_time - start_time
            print("Analysis finished at: " + str(end_time.strftime("%H:%M:%S")) + " (duration: " + str(duration.total_seconds()) + " s)")
            print("")
            # Move back to the main folder
            os.chdir("..")
        # Remove the pbc_*.txt files
        os.system("rm pbc_*.txt")

        # Calculate the diffusion coefficient for the MSD runs
        d_list = []
        if len(msd_list) != 0:
            #Set keyword for visualization (later)
            d_eval = True
            for i in range(len(coord_file)):
                os.chdir(str(ana_names[i]))
                for atom in msd_list:
                    # Read the MSD data
                    msd_data = np.loadtxt("msd_" + str(atom) + ".csv", delimiter=",", skiprows=1)
                    tau = msd_data[:, 0]
                    msd = msd_data[:, 1]

                    # Check if the data is empty
                    if msd.size == 0:
                        print("The MSD data is empty. Please check the file.")
                        exit()

                    # Calculate the diffusion coefficient
                    D = eval_diffusion_coefficient(tau, msd, atom)

                    d_coef = [str(ana_names[i]), str(atom), str(D)]
                    d_list.append(d_coef)
                os.chdir("..")
            np.savetxt("overview_diffcoeff.csv", d_list, delimiter=",", fmt="%s", header="#Analysis name, Atom type, Diffusion coefficient (A**2/ps)", comments="")
        else:
            d_eval = False

        if visualize == 'y':
            # Visualize the analysis
            plot_plan = {'rdf': rdf_pairs, 'msd': msd_list, 'smsd': smsd_list, 'autocorr': autocorr_pairs}
            # Create analyses dict
            analyses = {}
            for i in range(len(coord_file)):
                analyses[i] = [coord_file[i], pbc[i], timestep[i]]
            filenames = visualizer_multi(plot_plan, ana_names, analyses, d_eval)
            if len(msd_list) != 0:
                # Create the diffusion coefficient table
                try: 
                    dcoef_data_file = "overview_diffcoeff.csv"
                    msd_table = tab_writer(dcoef_data_file)
                except FileNotFoundError:
                    msd_table = ""
            else:
                msd_table = ""
            smsd_table = ""
            crt_manuscript(filenames, msd_table, smsd_table)


    else:
        ana_form()

    cite_amaceing_toolkit()

def ana_form():
    """
    This function does a Q&A session with the user to get the parameters for the analysis.
    """
    # Set the signal_handler to handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    print("Welcome to the aMACEing toolkit trajectory analyzer!")
    print("This tool will help you analyze your trajectory files.")
    print("Please answer the following questions to set up the analysis.")
    print("")

    # Ask for the trajectory file
    analyses = {}
    analyses_names = {}
    i = 0
    no_analyses = 1
    while i < no_analyses:
        coord_file = input("What is the name of the trajecory file? [coord.xyz]: ")
        if coord_file == '':
            coord_file = "coord.xyz"
        assert os.path.isfile(coord_file), "Coordinate file does not exist!"
    
        # Ask for the pbc file not to parse the actual number
        box_cubic = ask_for_yes_no_pbc("Is the box cubic? (y/n/pbc)", "pbc")
        if box_cubic == 'y':
            box_xyz = ask_for_float_int("What is the length of the box in Å?", str(10.0))
            box_xyz = float(box_xyz)
            np.savetxt(f'pbc_{i}.txt', np.array([[box_xyz, 0, 0], [0, box_xyz, 0], [0, 0, box_xyz]]))
            pbc = f'pbc_{i}.txt'  # Ensure the file name includes the extension
        elif box_cubic == 'n':
            pbc_mat = ask_for_non_cubic_pbc()
            np.savetxt(f'pbc_{i}.txt', pbc_mat)
            pbc = f'pbc_{i}.txt'  # Ensure the file name includes the extension
        else:
            pbc_file = np.loadtxt(box_cubic)
            assert pbc_file.shape == (3, 3), "PBC file is not in the right format!"
            np.savetxt(f'pbc_{i}.txt', pbc_file)
            pbc = f'pbc_{i}.txt'

        # Ask for the the timestep in fs
        timestep = ask_for_float_int("What is the timestep in fs?", str(0.5))
        timestep = float(timestep)
        assert  timestep > 0, "Timestep must be greater than 0!"

        if i == 0:
            no_analyses = ask_for_int("How many trajectories do you want to analyze (with the same setup)?", str(1))
            no_analyses = int(no_analyses)
            if no_analyses > 1:
                analyses_names[i] = input(f"What should be the key for this trajectory (aimd/mace/...)? [ana{i}]: ")
                if analyses_names[i] == '':
                    analyses_names[i] = f"ana{i}"
            else:
                no_analyses = 1
                analyses[i] = [coord_file, pbc, timestep]
                analyses_names[i] = "ana1"
                break
        else:
            analyses_names[i] = input("What should be the key for this trajectory (aimd/mace/...)? [ana" + str(i) + "]: ")
            if analyses_names[i] == '':
                analyses_names[i] = "ana" + str(i)

        analyses[i] = [coord_file, pbc, timestep]

        i += 1

    # Print the selected parameters
    print("")
    print("You selected the following parameters for the analysis:")
    for key in analyses.keys():
        print("Analysis " + str(key) + " aka " +  str(analyses_names[key]) + ": " + str(analyses[key][0]) + ", " + str(analyses[key][1]) + ", " + str(analyses[key][2]) + " fs/step")
    print("")
    
    # Setup the lists
    rdf_pairs = []
    msd_list = []
    smsd_list = []
    autocorr_pairs = []

    # Select the analysis type
    print("")
    print("The following analysis types are available:")
    print("1. Radial distribution function")
    print("2. Mean square displacement")
    print("3. Single particle mean square displacement")
    print("4. Vector-Autocorrelation function")
    print("")

    # Print the available atom types
    print("Searching for available atom types in the coordinate file...")
    all_avail_atomtypes = []
    for key in analyses.keys():
        avail_atomtypes = available_atomtypes(analyses[key][0])
        if key == 0:
            print("Available atom types: " + str(avail_atomtypes))
            all_avail_atomtypes = avail_atomtypes
        else:
            print(f"Available atom types ({analyses_names[key]}): " + str(avail_atomtypes))
            # all_avail_atomtypes includes the atom types which are in all analyses
            all_avail_atomtypes = list(set(all_avail_atomtypes) & set(avail_atomtypes))
    print("")
    
    # Print the smart proposal
    smart_msd_list, smart_rdf_pairs = smart_proposal(all_avail_atomtypes)
    print("")
    print("The smart proposal is based on the available atom types in the coordinate file.")
    print(" ==> The smart proposal for the radial distribution function is: " + str(smart_rdf_pairs))
    print(" ==> The smart proposal for the mean square displacement is: " + str(smart_msd_list))
    print("")

    # Ask for smart proposal
    classic_smart = ask_for_yes_no("Do you want to configure the whole analysis from scratch (y) or do you want to accept or refine the smart proposal (n) for the analysis?", "y")
    if classic_smart == "y":

        ana_dict = {"1": "rdf", "2": "msd", "3": "smsd", "4": "autocorr"}

        end_ana = False
        while end_ana == False:
            ana_type = ask_for_int("What type of analysis do you want to do? (1/2/3/4)", str(1))
            if ana_type in ana_dict.keys():
                ana_type = ana_dict[ana_type]
            else: 
                print("Invalid analysis type. ")
                exit()
            
            if ana_type == "rdf":
                print("You selected radial distribution function analysis.")
                
                # Ask for the pairs for the radial distribution function
                pair_str = input("What pairs do you want to analyze? (e.g. O-O, H-H, Si-H) [O-O]: ")
                if pair_str == '':
                    pair_str = "O-O"
                pair_list = pair_str.split(",")
                
                # Setup the right syntax for the cpp analyzer: O-O, H-H, Si-H
                for pair in pair_list:
                    pair = pair.strip()
                    if pair.split("-")[0] in avail_atomtypes and pair.split("-")[1] in avail_atomtypes:
                        if "-" in pair:
                            pair = pair.split("-")
                            pair[0] = pair[0].strip()
                            pair[1] = pair[1].strip()
                            rdf_pairs.append(pair)
                        else:
                            print(f"Invalid pair format for {pair}. Please use the format 'A-B'.")
                            exit()
                    elif "-" not in pair:
                        print(f"Invalid pair format for {pair}. Please use the format 'A-B'.")
                        exit()
                    else:
                        print(f"Invalid atom type {pair}. At least one of the atom types is not in the trajectory file.")
                print("You selected the following pairs for the radial distribution function analysis: " + str(rdf_pairs))

            elif ana_type == "msd":
                print("You selected mean square displacement analysis.")

                # Ask for the atom type for the mean square displacement

                atom_str = input("What atom type do you want to analyze? (e.g. O, H, Si) [O]: ")
                if atom_str == '':
                    atom_str = "O"
                atom_list = atom_str.split(",")

                # Setup the right syntax for the cpp analyzer: O, H, Sispo
                for atom in atom_list:
                    atom = atom.strip()
                    if atom not in avail_atomtypes:
                        print(f"Invalid atom type {atom}. Atom type is not in the trajectory file.")
                        exit()
                    else:
                        msd_list.append(atom)
                print("You selected the following atom types for the mean square displacement analysis: " + str(msd_list))

            elif ana_type == "smsd":
                print("You selected single particle mean square displacement analysis.")

                # Ask for the atom type for the single particle mean square displacement

                atom_str = input("What atom type do you want to analyze? (e.g. O, H, Si) [O]: ")
                if atom_str == '':
                    atom_str = "O"
                atom_list = atom_str.split(",")

                # Setup the right syntax for the cpp analyzer: O, H, Si
                for atom in atom_list:
                    atom = atom.strip()
                    if atom not in avail_atomtypes:
                        print(f"Invalid atom type {atom}. Atom type is not in the trajectory file.")
                        exit()
                    else:
                        smsd_list.append(atom)
                print("You selected the following atom types for the single particle mean square displacement analysis: " + str(smsd_list))

            elif ana_type == "autocorr":
                print("You selected vector autocorrelation function analysis.")

                # Ask for the pairs for the vector autocorrelation function
                pair_str = input("What pairs do you want to analyze? (e.g. O-O, H-H, Si-H) [O-O]: ")
                if pair_str == '':
                    pair_str = "O-O"
                pair_list = pair_str.split(",") 

                # Setup the right syntax for the cpp analyzer: O-O, H-H, Si-H
                for pair in pair_list:
                    pair = pair.strip()
                    if pair.split("-")[0] in avail_atomtypes and pair.split("-")[1] in avail_atomtypes:
                        if "-" in pair:
                            pair = pair.split("-")
                            pair[0] = pair[0].strip()
                            pair[1] = pair[1].strip()
                            autocorr_pairs.append(pair)
                        else:
                            print(f"Invalid pair format for {pair}. Please use the format 'A-B'.")
                            exit()
                    elif "-" not in pair:
                        print(f"Invalid pair format for {pair}. Please use the format 'A-B'.")
                        exit()
                    else:
                        print(f"Invalid atom type {pair}. At least one of the atom types is not in the trajectory file.")
                print("You selected the following pairs for the vector autocorrelation function analysis: " + str(autocorr_pairs))
            
            else:
                print("Invalid analysis type. ")
                exit()
            
            # Ask for another analysis type
            end_ana = ask_for_yes_no("Do you want to do another analysis? (y/n)", "n")
            if end_ana == "n": 
                end_ana = True
            else:
                end_ana = False
                print("You selected to do another analysis.")
                print("")
                print("The following analysis types are available:")
                print("1. Radial distribution function")
                print("2. Mean square displacement")
                print("3. Single particle mean square displacement")
                print("4. Vector-Autocorrelation function")
                print("")
        
    else:
        # Refine the smart proposal
        msd_list, rdf_pairs, smsd_list, autocorr_pairs = edit_smart_proposal(avail_atomtypes)

    # only one analysis:
    if len(analyses) == 1:
        coord_file, pbc, timestep = analyses[0]
        print("")
        start_time = datetime.datetime.now()
        print("Analysis started at: " + str(start_time.strftime("%H:%M:%S")))
        compute_analysis(coord_file, pbc, timestep, rdf_pairs, msd_list, smsd_list, autocorr_pairs)
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        print("Analysis finished at: " + str(end_time.strftime("%H:%M:%S")) + " (duration: " + str(duration.total_seconds()) + " s)")
        print("")
    # multiple analyses:
    else:
        for key in analyses.keys():
            # Prepare the folder
            analysis_folder(str(analyses_names[key]))
            coord_file, pbc, timestep = analyses[key]
            coord_file = path_checker(coord_file)
            pbc = path_checker(pbc)
            print("")
            print("Starting analysis of " + str(analyses_names[key]) + "...")
            start_time = datetime.datetime.now()
            print("Analysis started at: " + str(start_time.strftime("%H:%M:%S")))
            compute_analysis(coord_file, pbc, timestep, rdf_pairs, msd_list, smsd_list, autocorr_pairs)
            end_time = datetime.datetime.now()
            duration = end_time - start_time
            print("Analysis finished at: " + str(end_time.strftime("%H:%M:%S")) + " (duration: " + str(duration.total_seconds()) + " s) in folder " + str(analyses_names[key]))
            print("")
            # Move back to the main folder
            os.chdir("..")
    # After analysis remove all pbc_*.txt files
    os.system("rm pbc_*.txt")
            
    # Ask for Diffusion-Coefficient calculation for MSD runs 
    if len(msd_list) == 0:
        d_eval = "n"
    else:
        d_eval = ask_for_yes_no("Do you want to calculate the diffusion coefficient for the MSD runs? (y/n)", "y")
    if d_eval == "y":
        if len(analyses) == 1:
            d_list = []
            for atom in msd_list:
                # Read the MSD data
                msd_data = np.loadtxt("msd_" + str(atom) + ".csv", delimiter=",", skiprows=1)
                tau = msd_data[:, 0]
                msd = msd_data[:, 1]

                # Check if the data is empty
                if msd.size == 0:
                    print("The MSD data is empty. Please check the file.")
                    exit()

                # Calculate the diffusion coefficient
                D = eval_diffusion_coefficient(tau, msd, atom)

                d_coef = [str(atom), str(D)]
                d_list.append(d_coef)
            # Save the diffusion coefficients to a file
            np.savetxt("overview_diffcoeff.csv", d_list, delimiter=",", fmt="%s", header="#Atom type, Diffusion coefficient (A**2/ps)", comments="")
        else:
            d_list = []
            for key in analyses.keys():
                print("")
                os.chdir(str(analyses_names[key]))
                for atom in msd_list:
                    # Read the MSD data
                    msd_data = np.loadtxt("msd_" + str(atom) + ".csv", delimiter=",", skiprows=1)
                    tau = msd_data[:, 0]
                    msd = msd_data[:, 1]

                    # Check if the data is empty
                    if msd.size == 0:
                        print("The MSD data is empty. Please check the file.")
                        exit()

                    # Calculate the diffusion coefficient
                    print("Calculating the diffusion coefficient for " + str(analyses_names[key]) + "...")
                    D = eval_diffusion_coefficient(tau, msd, atom)
                    d_coef = [analyses_names[key], str(atom), str(D)]
                    d_list.append(d_coef)
                os.chdir("..")

            # Save the diffusion coefficients to a file
            np.savetxt("overview_diffcoeff.csv", d_list, delimiter=",", fmt="%s", header="#Analysis name, Atom type, Diffusion coefficient (A**2/ps)", comments="")

        print("The diffusion coefficients are saved in the file overview_diffcoeff.csv")
        print("")

    # Ask for automatic evaluation of the sMSD runs 
    if len(smsd_list) == 0:
        smsd_eval = "n"
    else:
        smsd_eval = ask_for_yes_no("Do you want to evaluate the sMSD runs? (y/n)", "y")
    if smsd_eval == "y":
        smsd_overview = []
        for atom_type in smsd_list:
            if len(analyses) == 1:
                # Read the sMSD data
                datax, datay = smsd_loader()

                # Check if the data is empty
                if len(datax) == 0:
                    print("The sMSD data is empty. Please check the file.")
                    exit()

                all_d, mean_d, std_dev, med, fastest = eval_smsd(datax[0][0], datay)

                print("")
                print("The mean diffusion coefficient for " + str(atom_type) + " is: " + str(mean_d) + " A**2/ps")
                print("The standard deviation for " + str(atom_type) + " is: " + str(std_dev) + " A**2/ps")
                print("The median for " + str(atom_type) + " is: " + str(med) + " A**2/ps")
                print("The 5 highest diffusion coefficients for invidual " + str(atom_type) + " atoms are: " + str(fastest[::-1]) + " A**2/ps")
                print("")

                # Save all the diffusion coefficients to a file
                np.savetxt("eval_smsd_" + str(atom_type) + ".csv", all_d, delimiter=",", header="#sMSD diffusion coefficients in A**2/ps", comments="")
                smsd_overview.append(["ana1" , str(atom_type), str(mean_d), str(std_dev), str(med), str(fastest[::-1])])

            else:
                for key in analyses.keys():
                    os.chdir(str(analyses_names[key]))
                    # Read the sMSD data
                    datax, datay = smsd_loader()

                    # Check if the data is empty
                    if len(datax) == 0:
                        print("The sMSD data is empty. Please check the file.")
                        exit()

                    all_d, mean_d, std_dev, med, fastest = eval_smsd(datax[0][0], datay)

                    print("")
                    print("The diffusion coefficient for " +  str(atom_type) + " atoms (" + str(analyses_names[key]) + ") is: " + str(mean_d) + " A**2/ps")
                    print("The standard deviation for " + str(atom_type) + " atoms (" + str(analyses_names[key]) + ") is: " + str(std_dev) + " A**2/ps")
                    print("The median for " + str(atom_type) +" atoms (" + str(analyses_names[key]) + ") is: " + str(med) + " A**2/ps")
                    print("The 5 highest diffusion coefficients for invidual " + str(atom_type) + " atoms (" + str(analyses_names[key]) + ") are: " + str(fastest[::-1]) + " A**2/ps")
                    print("")

                    # Save all the diffusion coefficients to a file
                    np.savetxt("eval_smsd_" + str(analyses_names[key]) + "_" + str(atom_type) + ".csv", all_d, delimiter=",", header="#sMSD diffusion coefficients in A**2/ps", comments="")
                    os.chdir("..")
                    smsd_overview.append([str(analyses_names[key]), str(atom_type), str(mean_d), str(std_dev), str(med), str(fastest[::-1])])
        
        # Save overview of the sMSD data to a file
        np.savetxt("overview_smsd.csv", smsd_overview, delimiter=",", fmt="%s", header="#Analysis name, Atom type, Mean diffusion coefficient (A**2/ps), Standard deviation (A**2/ps), Median (A**2/ps), 5 highest diffusion coefficients (A**2/ps)")

    # Ask for primitive visualization
    vis_ana = ask_for_yes_no("Do you want to visualize the analysis? (y/n)", "n")
    if vis_ana == "y":
        plot_plan = {'rdf': rdf_pairs, 'msd': msd_list, 'smsd': smsd_list, 'autocorr': autocorr_pairs}

        if len(analyses) == 1:
            filenames = visualizer(plot_plan, analyses_names, analyses, d_eval)
        else:
            filenames = visualizer_multi(plot_plan, analyses_names, analyses, d_eval)


        # Create the optional tables
        if len(msd_list) != 0:
            # Create the diffusion coefficient table if msd was evaluated
            try:    
                dcoef_data_file = "overview_diffcoeff.csv"
                msd_table = tab_writer(dcoef_data_file)
            except FileNotFoundError:
                msd_table = ""
        else:
            msd_table = ""

        if len(smsd_list) != 0:
            # Create the sMSD table if smsd was evaluated
            try: 
                smsd_data_file = "overview_smsd.csv"
                smsd_table = tab_writer(smsd_data_file)
            except FileNotFoundError:
                smsd_table = ""        
            
        else: 
            smsd_table = ""


        crt_manuscript(filenames, msd_table, smsd_table)

    


def available_atomtypes(coord):
    """
    This function returns the available atom types in the coordinate file.
    """
    atomtypes = []
    atoms = xyz_reader(coord, only_atoms=True)[0]

    for atom in atoms:
        if atom not in atomtypes:
            atomtypes.append(atom)
    return atomtypes

def diff_coef(t, D, n):
    """
    This function is used to fit the diffusion coefficient.
    """
    return 6 * D * t + n

def eval_diffusion_coefficient(tau, msd, atom):
    """
    This function calculates the diffusion coefficient from the MSD data.
    """

    # Mask: 10ps < tau < 30ps
    mask = (tau >= 10) & (tau <= 30)

    tau = tau[mask]
    msd = msd[mask]

    popt, pcov = curve_fit(diff_coef, tau, msd)
    D = popt[0] # in A**2/ps

    print("The diffusion coefficient for " + str(atom) + " is: " + str(D) + " A**2/ps")

    np.savetxt("diff_coeff_" + str(atom) + ".csv", [popt])

    return D

def eval_smsd(datax, datay):
    """
    This function evaluates the sMSD data.
    """
    # Check how many particles were analyzed
    no_particles = len(datay)

    # Define one mask for all datay (all datax are the same)
    mask_dfit = (datax >= 10) & (datax <= 30)
    datax_fit = datax[mask_dfit]

    d_arr = np.zeros((no_particles, 1))

    for i in range(no_particles):
        # Mask the data
        datay[i][0] = datay[i][0][mask_dfit]

        # Fit the data
        popt, pcov = curve_fit(diff_coef, datax_fit, datay[i][0])

        d_arr[i] = popt[0]

    # Calculate the diffusion coefficient
    mean_d = np.mean(d_arr)
    std_dev = np.std(d_arr)
    med = np.median(d_arr)

    # Find the fastest diffusion coefficients
    fastest = np.sort(np.partition(d_arr.flatten(), -5)[-5:])  # Ensure the fastest values are sorted

    return d_arr, mean_d, std_dev, med, fastest

def analysis_folder(analysis_name):
    """
    This function creates a folder for the analysis and moves the files to the folder.
    """
    if not os.path.exists(analysis_name):
        os.makedirs(analysis_name)
    else:
        print("The folder " + str(analysis_name) + " already exists. Please choose a different name or delete the existing folder.")
        exit()
    # Move to the folder
    os.chdir(analysis_name)

def visualizer(plot_plan, analyses_names, analyses, d_eval=False):
    """
    This function is used to prepare the visualization of the analysis.
    """
    filenames = []

    for ana_type, atom in plot_plan.items():
        if ana_type == "rdf":
            for pair in atom:
                data = np.loadtxt(f"rdf_{pair[0]}{pair[1]}.csv", delimiter=",", skiprows=1)
                datax = data[:, 0]
                datay = data[:, 1]
                plotter1(ana_type, f"{pair[0]}{pair[1]}", datax, datay, analyses_names[0])
                filenames.append(f"rdf_{pair[0]}{pair[1]}_plot.pdf")
        elif ana_type == "msd":
            for atom_type in atom:
                data = np.loadtxt("msd_" + str(atom_type) + ".csv", delimiter=",", skiprows=1)
                if d_eval:
                    dcoef = np.loadtxt("diff_coeff_" + str(atom_type) + ".csv", delimiter=" ")
                    dcoeff_fit = [dcoef[0], dcoef[1]]
                datax = data[:, 0]
                datay = data[:, 1]
                plotter1(ana_type, atom_type, datax, datay, analyses_names[0], dcoeff_fit)
                filenames.append("msd_" + str(atom_type) + "_plot.pdf")
        elif ana_type == "smsd":
            for atom_type in atom:
                # Read the sMSD data
                datax, datay = smsd_loader()
                plotter_multi(ana_type, atom_type, datax, datay, "")
                filenames.append("smsd_" + str(atom_type) + "__plot.pdf") # Double underscore because of nameing convention: smsd_H_ana1_plot.pdf, but for one analysis ana1 = ""
        elif ana_type == "autocorr":
            for pair in atom:
                data = np.loadtxt(f"autocorr_{pair[0]}{pair[1]}.csv", delimiter=",", skiprows=1)
                datax = data[:, 0]
                datay = data[:, 1]
                plotter1(ana_type, f"{pair[0]}{pair[1]}", datax, datay, analyses_names[0])
                filenames.append(f"autocorr_{pair[0]}{pair[1]}_plot.pdf")
        else:
            print("Invalid analysis type.")
            exit()
    return filenames


def visualizer_multi(plot_plan, analyses_names, analyses, d_eval=False):
    """
    This function is used to prepare the visualization of multiple analyses.
    """
    filenames = []

    for ana_type, atom in plot_plan.items():
        if ana_type == "rdf":
            for pair in atom:
                datax_list = []
                datay_list = []
                text_list = []
                for noa in analyses.keys():
                    os.chdir(str(analyses_names[noa]))
                    data = np.loadtxt(f"rdf_{pair[0]}{pair[1]}.csv", delimiter=",", skiprows=1)
                    os.chdir("..")
                    datax = data[:, 0]
                    datay = data[:, 1]
                    datax_list.append(datax)
                    datay_list.append(datay)
                    text_list.append(f"{analyses_names[noa]} ({pair[0]}{pair[1]})")
                plotter_multi(ana_type, f"{pair[0]}{pair[1]}", datax_list, datay_list, text_list)
                filenames.append(f"rdf_{pair[0]}{pair[1]}_plot.pdf")
        elif ana_type == "msd":
            for atom_type in atom:
                datax_list = []
                datay_list = []
                dcoef_list = []
                text_list = []
                for noa in analyses.keys():
                    os.chdir(str(analyses_names[noa]))
                    data = np.loadtxt("msd_" + str(atom_type) + ".csv", delimiter=",", skiprows=1)
                    if d_eval:
                        dcoef = np.loadtxt("diff_coeff_" + str(atom_type) + ".csv", delimiter=" ")
                        dcoef_list.append(dcoef)
                    os.chdir("..")
                    datax = data[:, 0]
                    datay = data[:, 1]
                    datax_list.append(datax)
                    datay_list.append(datay)
                    text_list.append(f"{analyses_names[noa]} ({atom_type})")
                plotter_multi(ana_type, atom_type, datax_list, datay_list, text_list, dcoef_list)
                filenames.append("msd_" + str(atom_type) + "_plot.pdf")
        elif ana_type == "smsd":
            for atom_type in atom:
                # There are so many lines in one smsd plot do not plot multiple analyses in one plot
                for noa in analyses.keys():
                    os.chdir(str(analyses_names[noa]))
                    datax, datay = smsd_loader()
                    os.chdir("..")
                    plotter_multi(ana_type, atom_type, datax, datay, str(analyses_names[noa]))
                    filenames.append("smsd_" + str(atom_type) + "_" + str(analyses_names[noa]) + "_plot.pdf")
        elif ana_type == "autocorr":
            for pair in atom:
                datax_list = []
                datay_list = []
                text_list = []
                for noa in analyses.keys():
                    os.chdir(str(analyses_names[noa]))
                    data = np.loadtxt(f"autocorr_{pair[0]}{pair[1]}.csv", delimiter=",", skiprows=1)
                    os.chdir("..")
                    datax = data[:, 0]
                    datay = data[:, 1]
                    datax_list.append(datax)
                    datay_list.append(datay)
                    text_list.append(f"{analyses_names[noa]} ({pair[0]}{pair[1]})")
                plotter_multi(ana_type, f"{pair[0]}{pair[1]}", datax_list, datay_list, text_list)
                filenames.append(f"autocorr_{pair[0]}{pair[1]}_plot.pdf")
        else:
            print("Invalid analysis type.")
            exit()

    return filenames

def smsd_loader():
    """
    This function is used to load the smsd data.
    """

    datax_arr = []
    datay_arr = []
    for file in os.listdir():
        if file.startswith("smsd_") and file.endswith(".csv"):
            data = np.loadtxt(file, delimiter=",", skiprows=1)
            datax = data[:, 0]
            datay = data[:, 1]
            datax_arr.append([datax])
            datay_arr.append([datay])
    return datax_arr, datay_arr


def plotter1(ana_type, atomtype, datax, datay, text, dcoeff_fit=[]):
    """
    This function is used to plot one analysis.
    """
    plot_defaultsettings()
    label = plot_labels(ana_type)
    plt.figure()
    plt.plot(datax, datay, label=text)
    if dcoeff_fit != []:
        plt.plot(datax, diff_coef(datax, dcoeff_fit[0], dcoeff_fit[1]), label="D coef. fit", linestyle=':')
    plt.xlabel(label[0])
    plt.ylabel(label[1])
    plt.title(f"{label[2]} of {atomtype}")
    plt.grid(alpha=0.2)
    plt.legend()
    plt.savefig(f"{ana_type}_{atomtype}_plot.pdf", bbox_inches='tight')


def plotter_multi(ana_type, atomtype, datax, datay, text, dcoeff_fit=[]):
    """
    This function is used to plot multiple analyses.
    """
    plot_defaultsettings()
    label = plot_labels(ana_type)

    no_datasets = len(datax)

    plt.figure()
    for i in range(no_datasets):
        if ana_type == "smsd":
            # Color gradient for smsd
            colors = color_grad_smsd(no_datasets)
            # only each 20 th line
            plt.plot(datax[i][0][::20], datay[i][0][::20], color=colors[i], linestyle='-', label="-")
        else:
            plt.plot(datax[i], datay[i], label=text[i])
        if dcoeff_fit != []:
            plt.plot(datax[i], diff_coef(datax[i], dcoeff_fit[i][0], dcoeff_fit[i][1]), label=f"D coef. fit ({text[i]})", linestyle=':')
    plt.xlabel(label[0])
    plt.ylabel(label[1])
    plt.title(f"{label[2]} of {atomtype}")
    plt.grid(alpha=0.2)
    if ana_type != "smsd": #no legend for smsd
        plt.legend() 
        plt.savefig(f"{ana_type}_{atomtype}_plot.pdf", bbox_inches='tight')
    else:
        plt.savefig(f"{ana_type}_{atomtype}_{text}_plot.pdf", bbox_inches='tight')


def plot_labels(analysis):
    """
    This function is used to set the labels for the plot.
    """
    if analysis == "rdf":
        return "r [$\mathrm{\AA}$]", "g(r)", "Radial Distribution Function (rdf)"
    elif analysis == "msd":
        return "$\\tau$ [ps]", "MSD [$\mathrm{\AA}^2$]", "Mean Square Displacement (msd)"
    elif analysis == "smsd":
        return "$\\tau$ [ps]", "MSD [$\mathrm{\AA}^2$]", "Single Particle Mean Square Displacement (single-msd)"
    elif analysis == "autocorr":
        return "$\\tau$ [ps]", "ACF", "Vector Autocorrelation Function (autocorr)"
    else:
        print("Invalid analysis type.")
        exit()
    
def plot_defaultsettings():
    """
    This function is used to set the default settings for the plot.
    """
    plt.rcParams.update({'figure.figsize': (18, 12),
                        'figure.dpi': 200,
                        'font.size': 30,
                        'font.family': 'serif',
                        'legend.fontsize': 25,
                        'lines.markersize': 3,
                        'lines.linewidth': 3,
                        'axes.titlesize': 35,
                        'axes.titlepad': 30,
                        'axes.labelsize': 35,
                        'axes.linewidth': 3,
                        'axes.xmargin': 0,
                        'xtick.direction': 'in',
                        'ytick.direction': 'in',
                        'xtick.major.size': 10,
                        'ytick.major.size': 10,
                        'xtick.major.width': 3,
                        'ytick.major.width': 3,
                        'xtick.labelsize': 27,
                        'ytick.labelsize': 27,
                        'legend.frameon': False
    })
    plt.rcParams.update({"text.usetex": True, "font.family": "cmr"})

    # Set the color, marker and linestype cycle
    from cycler import cycler
    color_list = ["#26547c", "#ef476f", "#f78c6b", "#ffd166", "#f4d3d3", "#c4bde6", "#98a6d4", "#a6bcb9", "#26547c", "#ef476f", "#f78c6b", "#ffd166", "#f4d3d3", "#c4bde6", "#98a6d4", "#a6bcb9"]
    #marker_list = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h", "H", "+", "x", "|", "_", "o"]
    marker_list = [",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ","]
    linestyle_list = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':']
    plt.rc('axes', prop_cycle=(plt.cycler('color', color_list) + plt.cycler('marker', marker_list) + plt.cycler('linestyle', linestyle_list)))


def color_grad_smsd(no_particles):
    """
    This function is used to set the color gradient for the smsd plot.
    """
    # Define a color gradient from blue to red
    colors = plt.cm.plasma(np.linspace(0, 1, no_particles))
    return colors


def crt_manuscript(filenames, table_msd="", table_smsd=""):
    """
    This function is used to create a latex manuscript for the analysis.
    """
    # grab all files (also from the subdirectories) which have the names noted in filenames and move them to the img_dir
    output_dir = os.path.join(os.getcwd(), "img_dir")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        print("The folder " + str(output_dir) + " already exists. Please choose a different name or delete the existing folder.")
        exit()
    for file in filenames:
        # get the name of the file without the path
        file_name = os.path.basename(file)
        # search the file in the subdirectories and copy it to the output_dir/img_dir
        for root, dirs, files in os.walk(os.getcwd()):
            if file_name in files:
                file = os.path.join(root, file_name)
                # prevent to copy the file to the output_dir/img_dir if it is already there
                if os.path.isfile(os.path.join(output_dir, file_name)):
                    continue
                else:
                    # copy the file to the output_dir/img_dir
                    os.system(f"cp {file} {output_dir}/{file_name}")
    
    # check if the file already exists than set the name to analysis1.tex and so on
    latex_file_name = "analysis.tex"
    i = 1
    while os.path.isfile(latex_file_name):
        latex_file_name = f"analysis{i}.tex"
        i += 1

    # print a tree on the first page 
    os.system("tree --prune -I 'smsd*' > tree.txt")
    tree_doc = open("tree.txt", "r")
    tree_text = tree_doc.read()
    tree_doc.close()
    os.remove("tree.txt")

    # get path of the current location
    curr_path = os.getcwd()
    escaped_curr_path = curr_path.replace("_", r"\_")

    latex_cont = r"""
% written by the aMACEing toolkit (Jonas Hänseroth, www.github.com/jhaens)
\documentclass{article}
\usepackage{graphicx}
\usepackage{caption}
\usepackage{geometry}
\usepackage{fancyvrb}
\usepackage[utf8]{inputenc}
\usepackage{pmboxdraw}
\geometry{a4paper, margin=1in}
\begin{document}

\title{Analysis Results}
\author{aMACEing toolkit}
\maketitle
\tableofcontents
\section{Analysis Details}
\begin{itemize}
\item Analysis done on \today
\item Analysis path: """ + escaped_curr_path + r"""
\item Analysis done by: """ + str(os.getlogin()) + r"""
\end{itemize}
\section{Analysis Tree}
\begin{Verbatim}
"""
    for line in tree_text.splitlines():
        latex_cont += f"""{line}
"""
    latex_cont += r"""
\end{Verbatim}
\newpage
"""
    # Add tables if they are not empty
    if table_msd != "" or table_smsd != "":
        latex_cont += r"""
\section{Diffusion Coefficients Overview}

""" 
        # Insert the table of diffusion coefficients
        if table_msd != "":
            latex_cont += table_msd
        if table_smsd != "":
            latex_cont += table_smsd
        latex_cont += r"""
\newpage
"""

    latex_cont += r"""
\section{Analysis Results}
"""
    # Dynamically add subsections for each analysis result
    for file in filenames:
        if os.path.exists(os.path.join(output_dir, file)):
            latex_cont += r"""
\subsection{""" + file.replace("_", r"\_").split(".")[0] + r"""}
\begin{figure}[h]
    \centering
    \includegraphics[width=.8\textwidth]{""" + f'{output_dir}/{file}' + r"""}
    \caption{Plot of """ + file.replace("_", r"\_") + r"""}
\end{figure}
\newpage
"""
    # End the LaTeX document
    latex_cont += r"\end{document}"

    # Write the LaTeX file
    with open(latex_file_name, "w") as f:
        f.write(latex_cont)
    print(f"LaTeX file {latex_file_name} created.")
    print(f"You can compile it the {latex_file_name} with the following command:")
    print(f"pdflatex {latex_file_name}")
    print("(To get the table of contents on the first page, run pdflatex twice.)")
    #print(f"texi2pdf {latex_file_name}")

def pse_only_labels():
    """
    This function is used to return the labels of the elements in the periodic table.
    """
    return  ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
            "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
            "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe",
            "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se",
            "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo",
            "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
            "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce",
            "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
            "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W",
            "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb",
            "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
            "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf",
            "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg",
            "Bh", "Hf", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv"]

def smart_proposal(atom_types):
    """
    This function is used to propose a smart analysis for the given system.
    """
    # Check if the atom types are valid
    avail_atomtypes = atom_types
    avail_analyses = ["rdf", "msd"]

    pse_label = pse_only_labels()

    # Set up a mask for the elements heavier than Xe
    pos_of_Ar = pse_label.index("Ar")
    heavier_than_Ar = pse_label[pos_of_Ar:]

    # Some predefined rules for the analysis
    no_gos = {'rdf': [['H','H']], 'msd': ['C', 'P', 'S', 'N']}
    for atom in avail_atomtypes:
        # No rdf of X1-X1 for all atoms, allowed only for O-O
        if atom in pse_label:
            if atom != "O":
                no_gos['rdf'].append([atom, atom])
        # No rdf of X1-X2 if X1 or/and X2 is heavier than Xe
        if atom in heavier_than_Ar:
            no_gos['msd'].append(atom)
            for other_atom in avail_atomtypes:
                no_gos['rdf'].append([atom, other_atom])
                no_gos['rdf'].append([other_atom, atom])
                no_gos['rdf'].append([atom, atom])
    

    # Build the msd_list and rdf_pairs
    msd_list = []
    rdf_pairs = []
    for atom in avail_atomtypes:
        if atom not in no_gos['msd']:
            msd_list.append(atom)
        for other_atom in avail_atomtypes:
            if [atom, other_atom] not in no_gos['rdf'] and [other_atom, atom] not in no_gos['rdf']:
                rdf_pairs.append([atom, other_atom])
                # Append the reverse pair to the no_gos list (to prevent duplicates)
                no_gos['rdf'].append([other_atom, atom])
    return msd_list, rdf_pairs


def edit_smart_proposal(atom_types):
    """
    This function is used to edit the smart proposal for the analysis runs for the given system.
    """
    
    msd_list, rdf_pairs = smart_proposal(atom_types)
    smsd_list = []
    autocorr_pairs = []

    # ask for refinement
    print("The following analyses are proposed:")
    print("Mean square displacement (msd) of the following atoms: " + str(msd_list))
    print("Radial distribution function (rdf) of the following pairs: " + str(rdf_pairs))
    refinement = ask_for_yes_no("Do you want to refine the analysis? (y/n)", "n")
    if refinement == "y":
        delete_rdf = ask_for_yes_no("Do you want to delete specific rdf pairs? (y/n)", "n")
        if delete_rdf == "y":
            delete_pairs = input(f"Please enter the pairs you want to delete (e.g. O-O, H-H, Si-H): ")
            delete_pairs = delete_pairs.split(",")
            for pair in delete_pairs:
                pair = pair.strip()
                pair = pair.split("-")
                pair[0] = pair[0].strip()
                pair[1] = pair[1].strip()
                if pair not in rdf_pairs:
                    print("Pair " + str(pair) + " is not in the proposed pairs.")
                else:
                    rdf_pairs.remove(pair)
                    print("Pair " + str(pair) + " removed from the proposed pairs.")
        else:
            print("No pairs removed from the proposed pairs.")
        add_rdf = ask_for_yes_no("Do you want to add specific rdf pairs? (y/n)", "n")
        if add_rdf == "y":
            add_pairs = input("Please enter the pairs you want to add (e.g. O-O, H-H, Si-H): ")
            add_pairs = add_pairs.split(",")
            for pair in add_pairs:
                pair = pair.strip()
                pair = pair.split("-")
                pair[0] = pair[0].strip()
                pair[1] = pair[1].strip()
                if pair in rdf_pairs:
                    print("Pair " + str(pair) + " is already in the proposed pairs.")
                else:
                    rdf_pairs.append(pair)
                    print("Pair " + str(pair) + " added to the proposed pairs.")
        else:
            print("No pairs added to the proposed pairs.")
        delete_msd = ask_for_yes_no("Do you want to delete specific msd atoms? (y/n)", "n")
        if delete_msd == "y":
            delete_atoms = input(f"Please enter the atoms you want to delete (e.g. O, H, Si): ")
            delete_atoms = delete_atoms.split(",")
            for atom in delete_atoms:
                atom = atom.strip()
                if atom not in msd_list:
                    print("Atom " + str(atom) + " is not in the proposed atoms.")
                else:
                    msd_list.remove(atom)
                    print("Atom " + str(atom) + " removed from the proposed atoms.")
        else:
            print("No atoms removed from the proposed atoms.")
        add_msd = ask_for_yes_no("Do you want to add specific msd atoms? (y/n)", "n")
        if add_msd == "y":
            add_atoms = input("Please enter the atoms you want to add (e.g. O, H, Si): ")
            add_atoms = add_atoms.split(",")
            for atom in add_atoms:
                atom = atom.strip()
                if atom in msd_list:
                    print("Atom " + str(atom) + " is already in the proposed atoms.")
                else:
                    msd_list.append(atom)
                    print("Atom " + str(atom) + " added to the proposed atoms.")
        else:
            print("No atoms added to the proposed atoms.")
        add_smsd = ask_for_yes_no("Do you want to add specific smsd atoms? (y/n)", "n")
        if add_smsd == "y":
            add_atoms = input("Please enter the atoms you want to add (e.g. O, H, Si): ")
            add_atoms = add_atoms.split(",")
            for atom in add_atoms:
                atom = atom.strip()
                if atom in smsd_list:
                    print("Atom " + str(atom) + " is already in the proposed atoms.")
                else:
                    smsd_list.append(atom)
                    print("Atom " + str(atom) + " added to the proposed atoms.")
        else:
            print("No atoms added to the proposed atoms.")
        add_autocorr = ask_for_yes_no("Do you want to add specific autocorr pairs? (y/n)", "n")
        if add_autocorr == "y":
            add_pairs = input("Please enter the pairs you want to add (e.g. O-O, H-H, Si-H): ")
            add_pairs = add_pairs.split(",")
            for pair in add_pairs:
                pair = pair.strip()
                pair = pair.split("-")
                pair[0] = pair[0].strip()
                pair[1] = pair[1].strip()
                if pair in autocorr_pairs:
                    print("Pair " + str(pair) + " is already in the proposed pairs.")
                else:
                    autocorr_pairs.append(pair)
                    print("Pair " + str(pair) + " added to the proposed pairs.")
    else:
        print("No refinement done.")


    print("The following analyses are proposed:")
    print("Mean square displacement (msd) of the following atoms: " + str(msd_list))
    print("Radial distribution function (rdf) of the following pairs: " + str(rdf_pairs))
    print("Single particle mean square displacement (smsd) of the following atoms: " + str(smsd_list))
    print("Autocorrelation function (autocorr) of the following pairs: " + str(autocorr_pairs))
    print("")
    return msd_list, rdf_pairs, smsd_list, autocorr_pairs

def path_checker(path):
    """
    This function checks if the path is absolute or relative and if its relative it adds a .. to the path.
    """
    if os.path.isabs(path):
        return path
    else:
        return os.path.join("..", path)


def signal_handler(sig, frame):
    """
    This function is used to handle the signal when the script is interrupted: It removes all pbc_*.txt files and exits the script.
    """
    print(' ')
    print(' ')
    print('You pressed Ctrl+C! Exiting the script and cleaning up tmp files...')
    print(' ')
    # check if the pbc_*.txt files exist and remove them
    for file in os.listdir():
        if file.startswith("pbc_") and file.endswith(".txt"):
            os.remove(file)
    exit(0)

def tab_writer(file):
    """
    This function is used to write a row in the table.
    """
    table_content = []

    # Read the file
    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("#"):
                continue
            else:
                # Split the line into columns
                columns = line.strip().split(",")
                # Append the columns to the table content
                table_content.append(columns)


    table_text = r"""\begin{table}[h]
    \centering """

    if len(table_content) == 0:
        print("The table content is empty. Please check the file.")
        return ""
    
    # MSD: Diffusion coefficients (one trajectory analysis)
    elif len(table_content[0]) == 2:
        # atom type, diffusion coefficient
        table_text += r"""\caption{Diffusion coefficients of MSD (file: """ + str(file.replace("_", r"\_").split(".")[0]) + r""") in A**2/ps.}
    \begin{tabular}{c c}
    \hline
    \textbf{Atom type} & \textbf{D [\r{A}$^2$/ps]} \\
    \hline
    """
        # Insert the values
        for i in range(len(table_content)):
            diff_val = float(table_content[i][1])
            diff_val = f"{diff_val:.3f}"
            table_text += f"""{str(table_content[i][0])} & {diff_val} """+r"""\\
            """

    # MSD: Diffusion coefficients (multiple trajectory analysis)   
    elif len(table_content[0]) == 3:
        # analysis name, atom type, diffusion coefficient
        table_text += r"""\caption{Diffusion coefficients of MSD (file: """ + str(file.replace("_", r"\_").split(".")[0]) + r""") in A**2/ps.}
    \begin{tabular}{c c c}
    \hline
    \textbf{Analysis name} & \textbf{Atom type} & \textbf{D [\r{A}$^2$/ps]} \\
    \hline
    """
        
        # Insert the values
        for i in range(len(table_content)):
            diff_val = float(table_content[i][2])
            diff_val = f"{diff_val:.3f}"
            table_text += f"""{str(table_content[i][0])} & {str(table_content[i][1])} & {diff_val} """+r"""\\
            """

    elif len(table_content[0]) == 6:
        # analysis name, atom type, mean diffusion coefficient, median, 5 highest diffusion coefficients
        # MSD: mean diffusion coefficient, median, 5 fastest diffusion coefficients
        table_text += r"""\caption{Diffusion coefficients of single-particle MSD (file: """ + str(file.replace("_", r"\_").split(".")[0]) + r""") in A**2/ps.}
    \begin{tabular}{c c c c c}
    \hline
    \textbf{Analysis} & \textbf{Atom} & \textbf{mean D} & \textbf{median D} & \textbf{5 highest D} \\
    \textbf{name} & \textbf{type} & \textbf{[\r{A}$^2$/ps]} & \textbf{[\r{A}$^2$/ps]} & \textbf{[\r{A}$^2$/ps]} \\
    \hline
    """
        
        # Insert the values
        for i in range(len(table_content)):
            mean_d = float(table_content[i][2])
            mean_d = f"{mean_d:.3f}"
            std_dev = float(table_content[i][3])
            std_dev = f"{std_dev:.3f}"
            med = float(table_content[i][4])
            med = f"{med:.3f}"
            fastest = table_content[i][5].replace("[", "").replace("]", "").replace(" ", ",")
            fastest = fastest.split(",")
            # delete empty strings ""
            fastest = [x for x in fastest if x != ""]
            fastest = f"{float(fastest[0]):.3f}, {float(fastest[1]):.3f}, {float(fastest[2]):.3f}, {float(fastest[3]):.3f}, {float(fastest[4]):.3f}"
            table_text += f"""{str(table_content[i][0])} & {str(table_content[i][1])} & {mean_d} $\pm$ {std_dev} & {med} & {fastest} """+r"""\\
            """
    table_text += r"""
    \hline
    \end{tabular}
    \end{table}

    
    """
    return table_text