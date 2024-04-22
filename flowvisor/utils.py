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

def value_to_hex_color(value, max_value):
    # Ensure value is within range [0, max_value]
    value = max(0, min(value, max_value))
    
    # Interpolate between light blue (#a9f3f9) and dark blue (#00008B)
    light_blue = [0xA9, 0xF3, 0xF9]  # RGB values for light blue
    dark_blue = [0x00, 0x1F, 0x3F]    # RGB values for dark blue
    
    # Calculate interpolation factors
    ratio = value / max_value
    inv_ratio = 1 - ratio
    
    # Interpolate RGB values
    interpolated_color = [
        int(light_blue[i] * inv_ratio + dark_blue[i] * ratio)
        for i in range(3)
    ]
    
    # Convert interpolated RGB values to hexadecimal color code
    hex_color = '#{:02X}{:02X}{:02X}'.format(*interpolated_color)
    
    return hex_color

def font_color_to_hex_color(value, max_value):
    # Ensure value is within range [0, max_value]
    value = max(0, min(value, max_value))
    
    # Interpolate between light orange (#ffc082) and dark orange (#6b3500)
    light_orange = [0xFF, 0xFF, 0xFF]  # RGB values for light orange
    dark_orange = [0x6B, 0x35, 0x00]    # RGB values for dark orange
    light_orange = [0xFF, 0xC0, 0x82]  # RGB values for light orange
    dark_orange = [0x00, 0x00, 0x00]    # RGB values for dark orange
    
    # Calculate interpolation factors
    ratio = value / max_value
    inv_ratio = 1 - ratio
    
    # Interpolate RGB values
    interpolated_color = [
        int(dark_orange[i] * inv_ratio + light_orange[i] * ratio)
        for i in range(3)
    ]
    
    # Convert interpolated RGB values to hexadecimal color code
    hex_color = '#{:02X}{:02X}{:02X}'.format(*interpolated_color)
    
    return hex_color