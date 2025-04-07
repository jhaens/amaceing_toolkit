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

    print("This run was logged with run_logger1 and the metadata is stored in the run_logger.log file in the installation directory of the aMACEing_toolkit.")
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
        print("run_hash:: date:: run_type:: location::")

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
                print(line)
            
        # Print the number of runs
        print(f"\nYou have run the aMACEing_toolkit {no_runs} times.")
        # Print the location of the log file
        print(f"The log file is located in the installation directory of the aMACEing_toolkit: {script_directory}/run_logger.log")
        print("====================================")
        print("")
                
                
    except FileNotFoundError:
        print("The model file run_logger.log does not exist in the installation directory of the aMACEing_toolkit: You did not save any runs yet.")
    return None