import os
import sys

from flowvisor.flowvisor import FlowVisor


def generate_graph(file_path, verify=False, verify_file=None):
    FlowVisor.reset()
    if verify_file is not None:
        FlowVisor.generate_graph(file_path, verify, verify_file)
    else:
        FlowVisor.generate_graph(file_path, verify)

    out_file = FlowVisor.CONFIG.output_file
    print(f"Flow graph generated at {out_file}")


def main():
    print(
        "This script will generate a flow graph from a file that was exported by FlowVisor."
    )
    print("Visit https://github.com/cophilot/FlowVisor#cli for more information.")
    # check if the path is provided as an argument
    args = sys.argv

    if len(args) < 2:
        print("No file path provided!")

    file_path = args[1]

    if not os.path.exists(file_path):
        print("Invalid file path!")
        sys.exit(1)

    verify = False
    verify_file = None

    for index, arg in enumerate(args):
        if arg == "-verify" or arg == "-v":
            verify = True
            if len(args) > index + 1:
                verify_file = args[index + 1]

    generate_graph(file_path, verify, verify_file)


if __name__ == "__main__":
    main()
