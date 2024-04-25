"""
Configuration class for FlowVisor
"""
class FlowVisorConfig:
    """
    Configuration class for FlowVisor
    """

    def __init__(self):
        self.show_graph: bool = True
        self.logo: str = ""
        self.output_file: str = "function_flow"
        self.graph_title: str = ""
        self.node_scale: float = 2.0
        self.node_show_file: bool = True
        self.node_show_call_count: bool = True
        self.node_show_avg_time: bool = True
        self.static_font_color: str = ""
        self.reduce_overhead: bool = True
        self.add_timestamp: bool = False
        self.advanced_overhead_reduction = None
        self.group_nodes: bool = False
        self.dev_mode: bool = False

    def get_node_scale(self):
        """
        Get the node scale as a string
        """
        return str(self.node_scale)