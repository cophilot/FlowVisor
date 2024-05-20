"""
The TimeValue class is a data structure to store the time values of a flowvisor.
"""

from typing import List
from flowvisor.flowvisor_config import FlowVisorConfig


class TimeValue:
    """
    A data structure to store the time values of a flowvisor
    """

    def __init__(
        self,
        nodes: List[any],
        config: FlowVisorConfig,
    ):
        self.max_time = TimeValue.get_max_time(nodes, config)
        self.max_avg_time = TimeValue.get_avg_max_time(nodes, config)
        self.total_time = TimeValue.get_total_time(nodes)
        self.mean_time = TimeValue.get_mean_time(nodes, config)
        self.mean_avg_time = TimeValue.get_mean_avg_time(nodes, config)

    @staticmethod
    def get_max_time(nodes: List[any], config: FlowVisorConfig):
        """
        Returns the highest time.
        """
        highest_time = -1
        for node in nodes:
            node_time = node.get_time(config.exclusive_time_mode)
            if node_time > highest_time:
                highest_time = node_time
        return highest_time

    @staticmethod
    def get_avg_max_time(nodes: List[any], config: FlowVisorConfig):
        """
        Returns the highest average time.
        """
        highest_time = -1
        for node in nodes:
            node_time = node.get_avg_time(config.exclusive_time_mode)
            if node_time > highest_time:
                highest_time = node_time
        return highest_time

    @staticmethod
    def get_total_time(nodes: List[any]):
        """
        Returns the total time.
        """
        total_time = 0
        for node in nodes:
            total_time += node.get_time(True)

        return total_time

    @staticmethod
    def get_mean_time(nodes: List[any], config: FlowVisorConfig):
        """
        Returns the mean time.
        """
        sum_time = 0
        for node in nodes:
            sum_time += node.get_time(config.exclusive_time_mode)

        return sum_time / len(nodes)

    @staticmethod
    def get_mean_avg_time(nodes: List[any], config: FlowVisorConfig):
        """
        Returns the mean average time.
        """
        sum_time = 0
        for node in nodes:
            sum_time += node.get_avg_time(config.exclusive_time_mode)

        return sum_time / len(nodes)
