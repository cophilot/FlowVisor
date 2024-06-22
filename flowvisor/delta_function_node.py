from flowvisor import utils
from flowvisor.flowvisor_config import FlowVisorConfig
from flowvisor.function_node import FunctionNode
from flowvisor.time_value import TimeValue


class DeltaFunctionNode(FunctionNode):
    """
    A specific node type for the delta graph.
    """

    def __init__(self, a: FunctionNode, b: FunctionNode):
        super().__init__(None)

        self.a = a
        self.b = b

        self.id = a.id
        self.name = a.name
        self.set_time(b.get_time(False) - a.get_time(False))
        self.file_path = a.file_path
        self.file_name = a.file_name
        self.children_ids = a.children_ids
        self.uuid = a.uuid
        self.called = a.called

    def get_node_title(self, time_value: TimeValue, config: FlowVisorConfig):
        """
        Returns the title of the node, that is displayed in the diagram.
        """
        title = self.name + "\n"

        if config.show_node_file:
            title += self.file_name + "\n"
        t_a = self.a.get_time(config.exclusive_time_mode)
        t_b = self.b.get_time(config.exclusive_time_mode)
        title += f"{utils.get_time_as_string(t_a)} / {utils.get_time_as_string(t_b)}\n"

        if config.show_node_call_count:
            title += f"({self.a.called} / {self.b.called})\n"

        if config.show_node_avg_time:
            title += f"avg {utils.get_time_as_string(self.a.get_avg_time(config.exclusive_time_mode))} / {utils.get_time_as_string(self.b.get_avg_time(config.exclusive_time_mode))}"

        title += "\n"

        if config.show_function_time_percantage:
            time_delta = t_b - t_a

            percentage = time_delta / t_a * 100
            title += f"{round(percentage, 2)}%"

        title += "\n"

        for _ in range(int(config.node_scale) - 1):
            title += "\n\n"
        return title

    def get_percentage(self, time_value: TimeValue, config: FlowVisorConfig):
        t_a = self.a.get_time(config.exclusive_time_mode)
        t_b = self.b.get_time(config.exclusive_time_mode)

        time_delta = t_b - t_a
        percentage = time_delta / t_a
        if percentage < 0:
            return percentage * -1
        return percentage

    def get_time(self, exclusive=True):
        t = self.b.get_time(exclusive) - self.a.get_time(exclusive)
        if t < 0:
            return t * -1
        return t
