"""
Utility functions for the flowvisor package
"""

import json
import os
import pickle


def function_to_id(func):
    """
    Generate a unique id for a function

    Args:
        func: function to generate id for
    """
    return f"{func.__code__.co_filename}::{func.__name__}"


def get_time_as_string(t: float):
    """
    Get the time as a string

    Args:
        t: time in seconds
    """

    sign = ""
    if t < 0:
        sign = "-"
        t = -t

    seconds = int(t)
    if seconds > 0:
        return f"{sign}{seconds}s"

    milliseconds = int(t * 1000)
    if milliseconds > 0:
        return f"{sign}{milliseconds}ms"

    microseconds = int(t * 1000000)
    if microseconds > 0:
        return f"{sign}{microseconds}μs"

    nanoseconds = int(t * 1000000000)
    if nanoseconds > 0:
        return f"{sign}{nanoseconds}ns"

    return f"<1ns"


def value_to_hex_color(
    value, max_value, light_color=[0xA9, 0xF3, 0xF9], dark_color=[0x00, 0x1F, 0x3F]
):
    """
    Return a hexadecimal color code based on the value and max_value
    """
    # Ensure value is within range [0, max_value]
    value = max(0, min(value, max_value))

    # Calculate interpolation factors
    ratio = value / max_value
    inv_ratio = 1 - ratio

    # Interpolate RGB values
    interpolated_color = [
        int(light_color[i] * inv_ratio + dark_color[i] * ratio) for i in range(3)
    ]

    # Convert interpolated RGB values to hexadecimal color code
    hex_color = "#{:02X}{:02X}{:02X}".format(*interpolated_color)

    return hex_color


def value_to_hex_color_using_mean(
    value, mean_value, light_color=[0xA9, 0xF3, 0xF9], dark_color=[0x00, 0x1F, 0x3F]
):
    """
    Returns the color based on the value and the mean value
    """
    if value < 0:
        value = -value

    if mean_value < 0:
        mean_value = -mean_value

    if mean_value == 0:
        return "#fff"

    ratio = value / mean_value
    ratio = ratio / 2

    ratio = min(1, ratio)
    inv_ratio = 1 - ratio

    interpolated_color = [
        int(light_color[i] * inv_ratio + dark_color[i] * ratio) for i in range(3)
    ]

    hex_color = "#{:02X}{:02X}{:02X}".format(*interpolated_color)
    return hex_color


def get_sys_info():
    """
    Get system information
    """
    device_name = get_device_name()
    cpu_name = (
        os.popen("lscpu | grep 'Model name'").read().strip().split(":")[1].strip()
    )
    cpu_cores = (
        os.popen("lscpu | grep 'CPU(s)'")
        .read()
        .strip()
        .split(":")[1]
        .strip()
        .split("\n")[0]
        .strip()
    )
    cpu_freq = (
        os.popen("lscpu | grep 'CPU max MHz'").read().strip().split(":")[1].strip()
        + " MHz"
    )
    ram = os.popen("free -h | grep Mem").read().strip().split()[1]
    return {
        "Device": device_name,
        "CPU": cpu_name,
        "Cores": cpu_cores,
        "Frequency": cpu_freq,
        "RAM": ram,
    }


def get_device_name():
    """
    Get the device name
    """
    return os.popen("hostname").read().strip()


def apply_file_end(file_name, end):
    """
    Apply the end to the file name
    """
    if not file_name.endswith(end):
        file_name += end
    return file_name


def get_node_by_id(n_id, nodes):
    """
    Get a node by its id
    """
    for node in nodes:
        if node.id == n_id:
            return node
    return None


def get_data_from_file(file, parse_data=True):
    """
    Get data from a file.
    Parses the file as json or pickle based on the file extension
    Returns the data object if it exists
    """
    if file.endswith(".json"):
        with open(file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    else:
        with open(file, "rb") as f:
            raw_data = pickle.load(f)
    if "data" in raw_data and parse_data:
        return raw_data["data"]
    return raw_data
