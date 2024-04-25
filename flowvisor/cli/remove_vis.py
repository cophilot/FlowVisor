import os
import sys

IMPORT_STATEMENT = "from flowvisor import vis"
DECORATOR = "@vis"

def remove_decorator(dir_path="."):
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

    new_content = []

    for index, line in enumerate(lines):
        if line.strip() == DECORATOR:
            continue
        if line.strip() == IMPORT_STATEMENT:
            continue
        new_content.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_content)
    print(f"Removed vis from {file_path}")

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
    print("This script will remove the vis decorator from all python files in the provided directory.")
    print("Visit https://github.com/cophilot/FlowVisor#cli for more information.")
    # check if the path is provided as an argument
    args = sys.argv
    for index, arg in enumerate(args):
        if arg == "-path" or arg == "-p":
            dir_path = args[index + 1]
            if os.path.exists(dir_path):
                remove_decorator(dir_path)
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
    remove_decorator(dir_path)

if __name__ == "__main__":
    main()
