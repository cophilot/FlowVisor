"""
Configuration class for FlowVisor
"""

from flowvisor import utils


class FlowVisorConfig:
    """
    Configuration class for FlowVisor
    """

    def __init__(self):
        # View options
        self.show_graph: bool = True
        self.logo: str = ""
        self.graph_title: str = ""
        self.node_scale: float = 2.0
        self.show_node_file: bool = True
        self.show_node_call_count: bool = True
        self.show_function_time_percantage: bool = False
        self.show_node_avg_time: bool = True
        self.static_font_color: str = ""
        self.show_timestamp: bool = False
        self.show_system_info: bool = False
        self.show_flowvisor_settings: bool = False
        self.group_nodes: bool = False
        self.outline_threshold: float = 0.1

        # File settings
        self.output_file: str = "function_flow"

        # Functional settings
        self.reduce_overhead: bool = True
        self.exclusive_time_mode: bool = True
        self.advanced_overhead_reduction = None
        self.use_avg_time: bool = False

        # Verifier settings
        self.verify_threshold: float = 0.2

        # Other
        self.dev_mode: bool = False

    def get_node_scale(self):
        """
        Get the node scale as a string
        """
        return str(self.node_scale)

    def get_functional_settings_string(self):
        """
        Returns a string with the functional settings
        """
        s = "Reduce Overhead: " + str(self.reduce_overhead) + "\n"
        if self.reduce_overhead and self.advanced_overhead_reduction is not None:
            s += (
                "Advanced Overhead reduction: "
                + utils.get_time_as_string(self.advanced_overhead_reduction)
                + "\n"
            )
        s += "Exclusive Time Mode: " + str(self.exclusive_time_mode) + "\n"
        s += "Use Average Time: " + str(self.use_avg_time) + "\n"
        return s

    def to_dict(self):
        """
        Convert the FlowVisorConfig object to a dictionary
        """
        return self.__dict__

    @staticmethod
    def from_dict(config_dict: dict):
        """
        Create a FlowVisorConfig object from a dictionary
        """
        config = FlowVisorConfig()
        for key in config_dict:
            setattr(config, key, config_dict[key])
        return config
