import os
import datetime
from amaceing_toolkit.workflow.utils import ask_for_yes_no

# Model logger 
def model_logger(model_loc, project_name, foundation_model, model_size, lr, no_question=False):
    """
    Log the model
    """
    folder_loc = os.path.dirname(model_loc)
    name = os.path.basename(model_loc)

    # Location of this script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Save the model in the finetuned_models.log file
    if no_question == False:
        save_status = ask_for_yes_no("Do you want to save the model in the finetuned_models.log file (for easier usage)? (y/n): ", "n")
    else:
        save_status = 'y'
    if save_status == 'n':
        return None
    else:
        # Get the note of the model
        if no_question == False:
            note = input("Please enter a note for this model (e.g. 'Model trained with 1000 epochs'): ")
            if note == '':
                note = 'No note provided'
        else:
            note = 'No note provided'
        # Get the current date and time
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")

        # Get the enumeration of the model
        if os.path.isfile(os.path.join(script_directory, 'finetuned_models.log')):
            with open(os.path.join(script_directory, 'finetuned_models.log'), 'r') as f:
                enumeration = len(f.readlines()) #no +1 because the first line is the header
        else:
            enumeration = 1

        # Logging info
        log_info = f"{enumeration}:: {date}:: {name}:: {note}:: {folder_loc}:: {foundation_model}:: {model_size}:: {lr}"

        try:

            if not os.path.isfile(os.path.join(script_directory, 'finetuned_models.log')):
                print("First model finetuned while using the aMACEing_toolkit... Congrats & Thank you for using the aMACEing_toolkit!")
                with open(os.path.join(script_directory, 'finetuned_models.log'), 'w') as f:
                    f.write("#no_model:: date:: name:: note:: location:: foundation_model:: model_size:: learning_rate \n")
                    f.write(log_info + '\n')
            else: 
                # Attach the log_info line to the log file
                with open(os.path.join(script_directory, 'finetuned_models.log'), 'a') as f:
                    f.write(log_info + '\n')

            

        except FileNotFoundError:
            print("The model file finetuned_models.log does not exist in the installation directory of the aMACEing_toolkit.")

        print("The infos of this model was saved into the finetuned_models.log for later use. The finetuned_models.log file is located in the installation directory of aMACEing_toolkit.")
        return None

def show_models():
    """
    Show the models that are saved in the finetuned_models.log file
    """
    try:
        # Get the path of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Read the finetuned_models.log file
        with open(os.path.join(script_directory, 'finetuned_models.log'), 'r') as f:
            for line in f:
                print(line)
    except FileNotFoundError:
        print("The model file finetuned_models.log does not exist in the installation directory of the aMACEing_toolkit: You did not save any models yet.")
    return None

def get_model(no_model):
    """
    Get the model that is saved in the finetuned_models.log file
    """
    no_model = int(no_model)
    try:
        # Get the path of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Read the finetuned_models.log file
        with open(os.path.join(script_directory, 'finetuned_models.log'), 'r') as f:
            for i, line in enumerate(f):
                # Convert i to int
                i = int(i)
                if i == no_model:
                    folder = line.split('::')[4]
                    name = line.split('::')[2]
                    path_to_model = os.path.join(folder, name)
                    break
                elif i > no_model:
                    print("The model number you entered does not exist in the finetuned_models.log file.")
                    break
    except FileNotFoundError:
        print("The model file finetuned_models.log does not exist in the installation directory of the aMACEing_toolkit: You did not save any models yet.")
    return path_to_model