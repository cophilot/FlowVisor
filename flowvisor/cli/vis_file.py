import os
import sys

from flowvisor.flowvisor import FlowVisor

def generate_graph(file_path):
    FlowVisor.generate_graph(file_path)

def main():
    print("This script will generate a flow graph from a file that was exported by FlowVisor.")
    print("Visit https://github.com/cophilot/FlowVisor#cli for more information.")
    # check if the path is provided as an argument
    args = sys.argv
    for index, arg in enumerate(args):
        if arg == "-file" or arg == "-f":
            file_path = args[index + 1]
            if os.path.exists(file_path):
                generate_graph(file_path)
                return

    while True:
        file_path = input("Enter the file you want to generate the flow graph from: ")
        if not os.path.exists(file_path):
            print("Invalid file")
            continue
        break
    generate_graph(file_path)

if __name__ == "__main__":
    main()
