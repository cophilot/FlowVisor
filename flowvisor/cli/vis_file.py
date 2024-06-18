import os
import sys

from flowvisor.flowvisor import FlowVisor


def generate_graph(file_path, verify=False, verify_file=None, config={}):
    FlowVisor.reset()
    FlowVisor.generate_graph(file_path, verify, verify_file, config=config)

    out_file = FlowVisor.CONFIG.output_file
    if not out_file.endswith(".png"):
        out_file += ".png"
    abs_path = os.path.abspath(out_file)
    print(f"Flow graph generated at {abs_path}")


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
    print("Usage: vis-file [options]")
    print("Options:")
    print(
        "\t-f, -file <file>: Path to the file that was exported by FlowVisor. If not provided, the default file path is 'flow.json'."
    )
    print(
        "\t-verify, -v <file>: Verify the flow graph using the provided verification file."
    )
    print(
        "\t-config, -c <config>: Configuration options for the flow graph using the format 'key1=value1,key2=value2'."
    )
    sys.exit(0)


def main():
    print(
        "This script will generate a flow graph from a file that was exported by FlowVisor."
    )
    print("Visit https://github.com/cophilot/FlowVisor#cli for more information.")
    print("Run 'vis-file --help' for help.")
    print()

    args = sys.argv

    verify = False
    verify_file = None
    config = ""
    file_path = None

    for index, arg in enumerate(args):
        if arg == "-verify" or arg == "-v":
            verify = True
            if len(args) > index + 1:
                verify_file = args[index + 1]
        if arg == "-config" or arg == "-c":
            if len(args) > index + 1:
                config = args[index + 1]
        if arg == "-file" or arg == "-f":
            if len(args) > index + 1:
                file_path = args[index + 1]
        if arg == "--help" or arg == "-h":
            print_help()

    if file_path is None:
        if os.path.exists("flow.json"):
            print("Using default file path: flow.json")
            file_path = "flow.json"
        else:
            print("Specify the file path with the -f flag!")
            sys.exit(1)

    if not os.path.exists(file_path):
        print("Invalid file path: ", file_path)
        sys.exit(1)

    config = parse_config_string(config)
    generate_graph(file_path, verify, verify_file, config)


if __name__ == "__main__":
    main()
