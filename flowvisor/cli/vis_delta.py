import os
import sys

from flowvisor.flowvisor import FlowVisor


def generate_delta_graph(file_a, file_b, config={}):
    FlowVisor.reset()
    FlowVisor.generate_delta_graph(file_a, file_b, config)

    out_file = FlowVisor.CONFIG.output_file
    if not out_file.endswith(".png"):
        out_file += ".png"
    abs_path = os.path.abspath(out_file)
    print(f"Delta flow graph generated at {abs_path}")


def parse_config_string(config):
    if config is None or config == "":
        return {}

    config_obj = {}
    config_arr = config.split(",")
    for item in config_arr:
        key, value = item.split("=")
        if value == "True":
            value = True
        elif value == "False":
            value = False

        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass

        config_obj[key] = value
    return config_obj


def print_help():
    print("Usage: vis-delta <file-a> <file-b> [options]")
    print(
        "Where file-a and file-b are the paths to the files that were exported by FlowVisor."
    )
    print("Example: vis-delta old.json new.json")
    print()
    print("Options:")
    print(
        "\t-f, -file <file>: Path to the file that was exported by FlowVisor. If not provided, the default file path is 'flow.json'."
    )
    print(
        "\t-config, -c <config>: Configuration options for the flow graph using the format 'key1=value1,key2=value2'."
    )
    sys.exit(0)


def main():
    print(
        "This script will generate a delta flow graph from a two files that was exported by FlowVisor. [b - a]"
    )
    print("Visit https://github.com/cophilot/FlowVisor#cli for more information.")
    print("Run 'vis-delta --help' for help.")
    print()

    args = sys.argv

    if len(args) < 3:
        print("Error: Invalid number of arguments!")
        print_help()
        sys.exit(1)

    file_a = args[1]
    if not os.path.exists(file_a):
        print("Error: Invalid file path: ", file_a)
        sys.exit(1)

    file_b = args[2]
    if not os.path.exists(file_b):
        print("Error: Invalid file path: ", file_b)
        sys.exit(1)

    config = ""

    for index, arg in enumerate(args):
        if arg == "-config" or arg == "-c":
            if len(args) > index + 1:
                config = args[index + 1]
        if arg == "--help" or arg == "-h":
            print_help()

    config = parse_config_string(config)
    generate_delta_graph(file_a, file_b, config)


if __name__ == "__main__":
    main()
