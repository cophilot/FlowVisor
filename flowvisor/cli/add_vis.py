import os
import sys

IMPORT_STATEMENT = "from flowvisor import vis"
DECORATOR = "@vis"

def add_decorator(dir_path="."):
    for root, dirs, files in os.walk(dir_path):
        if ignore_dir(os.path.basename(root)):
            continue

        for file in files:
            if not file.endswith(".py"):
                continue
            handle_file(root, file)
    print("Done")

def handle_file(root, file):
    # read contents of the file
    file_path = os.path.join(root, file)
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    found_function = False
    found_import = False
    for line in lines:
        if is_function(line):
            found_function = True
        if IMPORT_STATEMENT in line:
            found_import = True
    
    if not found_function:
        print(f"No function found in {file_path}")
        return
    
    new_content = []

    # iterate in reverse
    adding_existing_decorator = False
    spacing = ""
    for index, line in enumerate(lines[::-1]):
        if adding_existing_decorator:
            new_content.append(line)
            if not lines[-index - 1].strip().startswith("@"):
                adding_existing_decorator = False
                new_content.append(f"{spacing}{DECORATOR}\n")
        elif is_function(line):
            new_content.append(line)
            spacing = line.split("def")[0]
            if lines[-index - 1].strip().startswith("@"):
                adding_existing_decorator = True
            else:
                new_content.append(f"{spacing}{DECORATOR}\n")
        else:
            new_content.append(line)

    if not found_import:
        new_content.append(f"{IMPORT_STATEMENT}\n")

    new_content.reverse()

    with open(file_path, "w") as f:
        f.writelines(new_content)
    print(f"Added vis to {file_path}")

def ignore_dir(dir_name):
    if dir_name.endswith("__pycache__"):
        return True
    if dir_name.endswith("venv"):
        return True
    if dir_name.endswith(".git"):
        return True
    if dir_name.endswith(".vscode"):
        return True
    if dir_name.startswith(".") and dir_name != ".": # ignore hidden directories
        return True
    return False

def is_function(line):
    return line.strip().startswith("def ") and line.strip().endswith(":")

def main():
    print("This script will add the vis decorator to all python files in the provided directory.")
    print("Visit https://github.com/cophilot/FlowVisor#cli for more information.")
    # check if the path is provided as an argument
    args = sys.argv
    for index, arg in enumerate(args):
        if arg == "-path" or arg == "-p":
            dir_path = args[index + 1]
            if os.path.exists(dir_path):
                add_decorator(dir_path)
                return

    while True:
        dir_path = input("Enter the directory path where you want to add the decorator (default: current directory): ")
        if dir_path == "":
            dir_path = "."

        # check if the path is valid
        if not os.path.exists(dir_path):
            print("Invalid path")
            continue
        break
    add_decorator(dir_path)

if __name__ == "__main__":
    main()
