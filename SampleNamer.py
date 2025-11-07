import os
import shutil
import re

# -----------------------------
# HELPER FUNCTIONS AND VARIABLES
# ----------------------------- 
# Define list of inputs that indicate "no" or "not applicable"
no = ["n/a", "n", "na", "none", "no", ""]
yes = ["y", "yes", "yeah", "yep", "go", "sure", "do it"]

def key_detection(userKey):

    # make lower case and remove spaces
    text = userKey.strip().lower().replace(" ", "")

    # Check if input is empty
    if not text or text in no:
        print("No key provided.")
        return ""
    
    # look for valid root notes
    if not text or text[0] not in "abcdefg":
        raise ValueError("Invalid root note. Must be A–G.")
    
    root_note = text[0].upper()
    text = text[1:]

    # look for accidentals
    accidental = ""

    if text.startswith(("sharp", "sh", "s", "#", "♯")):
        accidental = "#"
        text = re.sub(r"^(sharp|sh|s|#|♯)", "", text)
    elif text.startswith(("flat", "fl", "f", "b", "♭")):
        accidental = "b"
        text = re.sub(r"^(flat|fl|f|b|♭)", "", text)

    # check for major/minor
    if text.startswith(("major", "maj")):
        mode = "maj"
    elif text.startswith(("minor", "min", "m")):
        mode = "min"
    elif text == "":
        mode = ""
    else:
        raise ValueError("Please input a valid key (e.g., C, D#, Fmin, Gmaj).")
    
    return f"{root_note}{accidental}{mode}"

def camel_case(inputString):
    words = inputString.strip().split()
    words = [word.capitalize() for word in words]
    return "".join(words)

def spaces_to_underscores(inputString):
    return inputString.strip().replace(" ", "_")


# -----------------------------
# COLLECT DESTINATION PATH
# -----------------------------

# look for destination file and check if it exists
while True:
    destinationFolder = input("Enter the folder where you want to save your file: ")
    destinationFolder = destinationFolder.strip().strip('"').strip("'")
    if not os.path.isdir(destinationFolder):
        print("That folder doesn't exist. Please check the path and try again.")
    else:
        break

# -------------------------------------------------
# ----------------- MAIN LOOP ---------------------
# -------------------------------------------------

while True:
    # -----------------------------
    # COLLECT SOURCE PATH
    # -----------------------------

    # look for source file and check if it exists
    while True:
        sourcePath = input("Enter the source file path: ")
        sourcePath = sourcePath.strip().strip('"').strip("'")
        print(sourcePath)
        if not os.path.isfile(sourcePath):
            print("That file doesn't exist. Please check the path and try again.")
            print(f"Checked path: {sourcePath}")
        else:
            break

    FileExt = os.path.splitext(sourcePath)[1]

    # -----------------------------
    # GATHER USER INPUTS FOR NAMING AND ORGANISING
    # -----------------------------

    # sample pack name
    packName = camel_case(input("What sample pack does this sample belong to?"))

    # sample type
    while True:
        sampleType = input("Is this a loop or one-shot? (enter 'loop' or 'OS'): ").strip().lower()
        if sampleType in ("loop", "l"):
            sampleType = "loop"
            break
        if sampleType in ("os", "one-shot", "oneshot", "one shot", "one_shot"):
            sampleType = "OS"
            break
        print("Invalid response. Please enter 'loop' or 'OS'.")

    # sample tempo
    while True:
        tempo = input("What is the tempo of this sample?")
        tempo = tempo.lower().replace(" ", "")
        if tempo in no and sampleType == "OS":
            tempo = ""
            break
        elif tempo in no and sampleType == "loop":
            print("Tempo is required for loops. Please enter a tempo in BPM.")
            continue

        if tempo.endswith("bpm"):
            tempo = tempo[:-3]
        if not tempo.isdigit():
            print("Invalid tempo. Please enter a numeric value.")
            continue

        bpm = int(tempo)

        if bpm < 20 or bpm > 999:
            print("Tempo must be between 20 and 999 BPM. Please try again.")
            continue

        tempo = str(bpm)
        break

    # sample instrument
    while True:
        instrument = camel_case(input("What instrument is this sample?"))
        if not instrument:
            print("Instrument must have a name. Please try again.")
        else:
            break

    # sample name
    while True:
        sampleName = camel_case(input("What would you like to name this sample?"))
        if not sampleName:
            print("Sample must have a name. Please try again.")
        else:
            break

    # sample key
    while True:
        try:
            key = key_detection(input("What key is this sample in? (e.g., C, D#, Fmin, Gmaj, etc.): "))
            break
        except ValueError as e:
            print(f"Invaid input: {e}. \n Please try again.")


    # -----------------------------
    # CONSTRUCT NEW FILE NAME
    # -----------------------------

    # List of components for the filename
    components = []

    # Only add the component if it exists / is not empty
    if packName:
        components.append(packName)
    if tempo:
        components.append(tempo)
    if instrument:
        components.append(instrument)
    if sampleType:
        components.append(sampleType)
    if sampleName:
        components.append(sampleName)
    if key:
        components.append(key)

    # Join with underscores
    newName = "_".join(components) + FileExt


    # -----------------------------
    # LOCATE / CREATE FOLDERS
    # -----------------------------

    # -----------------------------
    # look for / create pack folder in destination folder
    # if pack has no name use "Uncategorised", if that doesnt exist then create it
    if packName.strip() == "":
        packFolder = os.path.join(destinationFolder, "Uncategorised")

        if not os.path.isdir(packFolder):
            os.makedirs(packFolder)
            print(f"No pack name provided. 'Uncategorised' folder created. Samples will be stored here.")
    
        else:
            print("No pack name provided. Samples will be stored in existing 'Uncategorised' folder.")

    # if pack has a name, check if a folder for it exists
    else:
        packFolder = os.path.join(destinationFolder, packName)

        while True:
            # check if the pack folder exists
            if not os.path.isdir(packFolder):
                response = input(f"There is no folder named '{packName}' in the destination. Create it? (y/n): ").strip().lower()
                
                # create the pack folder if it doesnt exist and the user agrees
                if response in yes:
                    os.makedirs(packFolder)
                    print(f"Folder '{packName}' created. Samples from this pack will be stored here.")
                    break
                
                # if user declines, use "Uncategorised" folder instead
                elif response in no:
                    packFolder = os.path.join(destinationFolder, "Uncategorised")
                    
                    # only create "Uncategorised" if it doesnt already exist
                    if not os.path.isdir(packFolder):
                        os.makedirs(packFolder)
                        print(f"Folder 'Uncategorised' created. Samples without a pack will be stored here.")
                    
                    else:
                        print("Samples will be stored in 'Uncategorised' folder.")
                
                    break
                
                # if user input is invalid, ask again
                else:
                    print("Please answer 'y' (yes) or 'n' (no).")
            
            # if the pack folder exists, use it and tell the user
            else:
                print(f"Sample will be stored in '{packName}' folder.")
                break

    # -----------------------------
    # look for / create instrument folder in pack folder
    instrumentFolder = os.path.join(packFolder, instrument) 

    # check if instrument folder exists
    if not os.path.isdir(instrumentFolder):

        while True:
            # ask user if they want to create the instrument folder
            response = input(f"The folder for instrument '{instrument}' does not exist. Create it? (y/n): ").strip().lower()
            
            # create the instrument folder if user agrees
            if response in yes:
                os.makedirs(instrumentFolder)
                print(f"Folder '{instrument}' created inside '{packFolder}'.")
                break

            # if user declines, use "Miscellaneous" folder instead
            elif response in no:
                instrumentFolder = os.path.join(packFolder, "Miscellaneous")
                
                # only create "Miscellaneous" if it doesnt already exist
                if not os.path.isdir(instrumentFolder):
                    os.makedirs(instrumentFolder)
                    print(f"'Miscellaneous' folder created inside '{packFolder}'.")
                
                # if it already exists, use it and inform the user
                else:
                    print(f"Samples will be stored in existing 'Miscellaneous' folder inside '{packFolder}'.")
                
                break
            
            # if user input is invalid, ask again
            else:
                print("Please answer 'y' (yes) or 'n' (no).")

    # -----------------------------
    # look for / create oneshot or loop folder in instrument folder
    sampleTypeFolder = os.path.join(instrumentFolder, sampleType) 

    # check if sample type folder exists
    if not os.path.isdir(sampleTypeFolder):
        # create the sample type folder if it doesn't exist
        os.makedirs(sampleTypeFolder)
        print(f"Folder '{sampleType}' created inside '{instrumentFolder}'.")

    else:
        # if it already exists, use it and inform the user
        print(f"Samples will be stored in existing '{sampleType}' folder inside '{instrumentFolder}'.")


    # -----------------------------
    # ASSIGN FINAL DESTINATION FOLDER
    # -----------------------------
    finalisedFolder = sampleTypeFolder
    print("Final storage folder:", finalisedFolder)
    
    # combine destination folder and new file name
    destinationPath = os.path.join(finalisedFolder, newName)


    # -----------------------------
    # COPY FILE TO DESTINATION AND CONFIRMATION
    # -----------------------------
    shutil.copy2(sourcePath, destinationPath)
    print(f"File copied successfully to {destinationPath}")