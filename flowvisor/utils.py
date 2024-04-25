"""
Utility functions for the flowvisor package
"""

import os

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
    seconds = int(t)
    if seconds > 0:
        return f"{seconds}s"

    milliseconds = int(t * 1000)
    if milliseconds > 0:
        return f"{milliseconds}ms"

    microseconds = int(t * 1000000)
    if microseconds > 0:
        return f"{microseconds}μs"

    nanoseconds = int(t * 1000000000)
    if nanoseconds > 0:
        return f"{nanoseconds}ns"

    return "<1ns"

def value_to_hex_color(value, max_value, light_color = [0xA9, 0xF3, 0xF9], dark_color = [0x00, 0x1F, 0x3F]):
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
        int(light_color[i] * inv_ratio + dark_color[i] * ratio)
        for i in range(3)
    ]

    # Convert interpolated RGB values to hexadecimal color code
    hex_color = '#{:02X}{:02X}{:02X}'.format(*interpolated_color)

    return hex_color

def get_sys_info():
    """
    Get system information
    """
    device_name = os.popen("hostname").read().strip()
    cpu_name = os.popen("lscpu | grep 'Model name'").read().strip().split(":")[1].strip()
    cpu_cores = os.popen("lscpu | grep 'CPU(s)'").read().strip().split(":")[1].strip().split('\n')[0].strip()
    cpu_freq = os.popen("lscpu | grep 'CPU max MHz'").read().strip().split(":")[1].strip() + " MHz"
    ram = os.popen("free -h | grep Mem").read().strip().split()[1]
    return {
        "Device": device_name,
        "CPU": cpu_name,
        "Cores": cpu_cores,
        "Frequency": cpu_freq,
        "RAM": ram
    }
