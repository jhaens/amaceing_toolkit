import os
import datetime

# Run logger (version 1: no monitoring backend/frontend build yet)
def run_logger1(run_type, folder_loc):
    """
    Log the run
    """

    # Get unique run hash
    run_hash = os.urandom(8).hex()
    
    # Get the current date and time
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")

    # Logging info
    log_info = f"{run_hash}:: {date}:: {run_type}:: {folder_loc}"

    # Get the path of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    try:
        
        if not os.path.isfile(os.path.join(script_directory, 'run_logger.log')):
                print("First run ever with the aMACEing_toolkit... Happy to have you on board!")
                with open(os.path.join(script_directory, 'run_logger.log'), 'w') as f:
                    f.write("#run_hash:: date:: run_type:: location::\n")
                    f.write(log_info + '\n')
        else:
            # Attach the log_info line to the log file
            with open(os.path.join(script_directory, 'run_logger.log'), 'a') as f:
                f.write(log_info + '\n')

            
    
    except FileNotFoundError:
        print("The log file run_logger.log does not exist in the installation directory of aMACEing_toolkit.")

    print("This run was logged with run_logger and the metadata is stored in the run_logger.log file in the installation directory of the aMACEing_toolkit.")
    return None

def show_runs():
    """
    Show the last 10 runs of the aMACEing_toolkit and give some miscellaneous information
    """
    try:
        # Get the path of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Print header
        print("")
        print("aMACEing_toolkit run logger")
        print("====================================")
        print("Last 10 runs of the aMACEing_toolkit:")
        print("run_hash        :: date               :: run_type:: status:: location")
        # Read the finetuned_models.log file
        with open(os.path.join(script_directory, 'run_logger.log'), 'r') as f:
            # Read the last 10 lines of the file
            lines = f.readlines()
            no_runs = len(lines) - 1
            # Check if the file has more than 10 lines
            if len(lines) > 10:
                lines = lines[-10:]
            # Print the last 10 lines of the file
            for line in lines:
                line = line.split('::')
                line = [x.strip() for x in line]
                print(f"{line[0]}:: {line[1]}:: {line[2]}:: {status_checker(line[3])}:: {line[3]}")

        # Print the number of runs
        print(f"\nYou have run the aMACEing_toolkit {no_runs} times.")
        # Print the location of the log file
        print(f"The log file is located in the installation directory of the aMACEing_toolkit: {script_directory}/run_logger.log")
        print("====================================")
        print("")
                
                
    except FileNotFoundError:
        print("The model file run_logger.log does not exist in the installation directory of the aMACEing_toolkit: You did not save any runs yet.")
    return None

def status_checker(path):
    """
    Check the status of the run (only via the time of the last modified file in the directory)
    """

    if not os.path.exists(path) or not os.path.isdir(path) or not os.listdir(path):
        return "ERR"
    else:
        # Check if any file in the directory was modified in the last 1 hour
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not files:
            return "ERR"
        newest_file = ''
        for f in files:
            file_path = os.path.join(path, f)
            if os.path.getmtime(file_path) > os.path.getmtime(os.path.join(path, newest_file)):
                newest_file = f
        last_modified = os.path.getmtime(os.path.join(path, newest_file))
        # Get the current time
        current_time = os.path.getmtime(path)
        # Check if the file was modified in the last 1 hour
        if current_time - last_modified < 3600:
            return "RUN"
        else:
            return "END"

def export_run_logs():
    """
    Export the content of the run logger to a tex file
    """
    # General Setup of tex file

    tex_file = r"""
\documentclass{article}
\usepackage{graphicx}
\usepackage{caption}
\usepackage{geometry}
\usepackage{fancyvrb}
\usepackage[utf8]{inputenc}
\usepackage{pmboxdraw}
\begin{document}

\title{Recent runs of the aMACEing toolkit}
\author{aMACEing toolkit}
\maketitle

This document contains all runs performed with the aMACEing toolkit. The original log file is located in the installation directory of the aMACEing toolkit: \\
\mbox{\texttt{/path/to/aMACEing\_toolkit/src/amaceing\_toolkit/runs/run\_logger.log}}

"""
    # Build the table
    file_name = os.path.join(os.path.dirname(__file__), 'run_logger.log')
    table_text = tab_writer(file_name)
    # Add the table to the tex file
    tex_file += table_text
    # Add the end of the tex file
    tex_file += r"""
\end{document}
    """
    # Write the tex file temporarily in the current directory
    with open('tmp_run_logger.tex', 'w') as f:
        f.write(tex_file)

    # Compile the tex file to pdf
    try:
        os.system('pdflatex tmp_run_logger.tex')
        os.system('rm tmp_run_logger.tex')
        os.system('rm tmp_run_logger.aux')
        os.system('rm tmp_run_logger.log')
        os.system('mv tmp_run_logger.pdf run_logger.pdf')
    except:
        os.system('mv tmp_run_logger.tex output_run_logger.tex')
        print("WARNING: The tex file was not compiled to pdf.")
        print("Error: pdflatex is not installed or not in the PATH. Please compile output_run_logger.tex yourself.")
    

def tab_writer(file):
    """
    This function is used to write rows in the tex table.
    """
 
    table_text = r"""
\begin{table}[h]
    \centering 
    \resizebox{\textwidth}{!}{
    \begin{tabular}{c c c c c}
        \hline
        \textbf{Run Hash} & \textbf{Date} & \textbf{Run Type} & \textbf{Status} & \textbf{Location} \\
        \hline
    """

    # Read the file
    with open(file, "r") as f:
        lines = f.readlines()
        # If more than 50 lines, take the last 50 lines
        if len(lines) > 50:
            lines = lines[-50:]
        for line in lines:
            line = line.split('::')
            line = [x.strip() for x in line]
            
            try:
                table_text += r"\texttt{"+f"{str(line[0])}"+r"}"+f" & {str(line[1])} & "+ str(line[2].replace(r"_", r"\_"))+f" & {str(status_checker(line[3]))} & "+r"\texttt{"+str(line[3].replace(r"_", r"\_"))+r"""} \\ 
                """
            except:
                continue

    table_text += r"""
        \hline
    \end{tabular}
    }
\end{table}
    """
    return table_text