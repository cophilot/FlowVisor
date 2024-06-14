"""
A node in the function call graph.
"""

import os
from typing import List
import uuid
from PIL import Image, ImageDraw
from diagrams.custom import Custom

from flowvisor import utils
from flowvisor.flowvisor_config import FlowVisorConfig
from flowvisor.time_value import TimeValue


class FunctionNode:
    """
    A node in the function call graph
    """

    NODE_IMAGE_CACHE = "__flowvisor_node_image_cache__"
    NODE_IMAGE_SCALE = 300

    def __init__(self, func):
        if func is not None:
            self.id: str = utils.function_to_id(func)
            self.uuid = str(uuid.uuid4())
            self.name: str = func.__name__
            self.file_path: str = func.__code__.co_filename
            self.file_name: str = os.path.basename(self.file_path)
        self.children: List[FunctionNode] = []
        self.children_ids: List[str] = []
        self.__time: float = 0
        self.diagram_node = None
        self.called: int = 0
        self.child_time: float = 0

    def export_node_image(self, time_value: TimeValue, config: FlowVisorConfig):
        """
        Generates the node image background.
        """
        dim = FunctionNode.NODE_IMAGE_SCALE
        image = Image.new("RGB", (dim, dim), "white")
        draw = ImageDraw.Draw(image)

        t = self.get_time(config.exclusive_time_mode)
        mean = time_value.mean_time
        max = time_value.max_time
        if config.use_avg_time:
            t = self.get_avg_time(config.exclusive_time_mode)
            mean = time_value.mean_avg_time
            max = time_value.max_avg_time

        color = utils.value_to_hex_color_using_mean(t, mean)

        if t >= max * (1 - config.outline_threshold):
            # draw outline
            draw.rectangle((0, 0, dim, dim), fill="#ff0000")
            ## draw inner
            draw.rectangle((10, 10, dim - 10, dim - 10), fill=color)
        else:
            draw.rectangle((0, 0, dim, dim), fill=color)

        os.makedirs(FunctionNode.NODE_IMAGE_CACHE, exist_ok=True)
        file_name = f"{FunctionNode.NODE_IMAGE_CACHE}/{self.uuid}.png"
        image.save(file_name)

        return file_name

    def get_as_diagram_node(self, time_value: TimeValue, config: FlowVisorConfig):
        """
        Gets the node as a diagram node.
        """
        if self.diagram_node is None:
            self.generate_diagram_node(time_value, config)
        return self.diagram_node

    def generate_diagram_node(self, time_value: TimeValue, config: FlowVisorConfig):
        """
        Generates the diagram node.
        """
        if self.get_percentage(time_value, config) < config.percantage_threshold:
            return

        node_image = self.export_node_image(time_value, config)

        size = config.node_scale

        title = self.get_node_title(time_value, config)

        font_color = config.static_font_color
        if font_color == "":
            t = self.get_time(config.exclusive_time_mode)
            m = time_value.mean_time
            if config.use_avg_time:
                t = self.get_avg_time(config.exclusive_time_mode)
                m = time_value.mean_avg_time
            font_color = utils.value_to_hex_color_using_mean(
                t,
                m,
                dark_color=[0xFF, 0xC0, 0x82],
                light_color=[0x00, 0x00, 0x00],
            )

        self.diagram_node = Custom(
            title, node_image, width=str(size), height=str(size), fontcolor=font_color
        )

    def get_node_title(self, time_value: TimeValue, config: FlowVisorConfig):
        """
        Returns the title of the node, that is displayed in the diagram.
        """
        title = self.name + "\n"

        if config.show_node_file:
            title += self.file_name + "\n"
        t = self.get_time(config.exclusive_time_mode)
        title += utils.get_time_as_string(t)

        if config.show_node_call_count:
            title += f" ({self.called})"

        title += "\n"

        if config.show_node_avg_time:
            title += f"avg {utils.get_time_as_string(self.get_avg_time(config.exclusive_time_mode))}"

        title += "\n"

        if config.show_function_time_percantage:
            percentage = self.get_percentage(time_value, config) * 100
            title += f"{round(percentage, 2)}%"

        title += "\n"

        for _ in range(int(config.node_scale) - 1):
            title += "\n\n"
        return title

    def get_percentage(self, time_value: TimeValue, config: FlowVisorConfig):
        t = self.get_time(config.exclusive_time_mode)
        return t / time_value.total_time

    def got_called(self, duration: float):
        """
        The function got called.

        Args:
            duration: The time it took to execute the function.
        """
        self.called += 1
        self.set_time(duration)

    def add_child(self, child):  # type: ignore
        """
        Adds a child node to the current node.

        Args:
            child (FunctionNode): The child node to add.
        """
        if self.id == child.id:
            return
        for node in self.children:
            if node.id == child.id:
                return
        self.children.append(child)

    def set_time(self, time: float):
        """
        Sets the time of the function.

        Args:
            time (float): The time it took to execute the function.
        """
        self.__time += time

    def file_function_name(self):
        """
        Returns the file name and function name.
        """
        return f"{self.file_name}::{self.name}"

    def __str__(self):
        return self.file_function_name()

    def to_dict(self, short=False):
        """
        Gets the node as a dictionary.

        Args:
            short: If the dictionary should be short.
        """

        if short:
            return {
                "id": self.id,
                "uuid": self.uuid,
                "name": self.name,
                "file_path": self.file_path,
                "file_name": self.file_name,
            }
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "children": [child.to_dict(True) for child in self.children],
            "exclusive_time": self.get_time(True),
            "inclusive_time": self.get_time(False),
            "called": self.called,
        }

    def resolve_children_ids(self, all_nodes):
        """
        Resolves the children ids.

        Args:
            all_nodes: All nodes in the graph.
        """
        self.children = []
        for child_id in self.children_ids:
            for node in all_nodes:
                if node.uuid == child_id:
                    self.add_child(node)

    def get_time(self, exclusive=True):
        """
        Gets the time of the node.

        Args:
            exclusive: If the time should be exclusive.
        """
        if exclusive:
            return self.__time - self.child_time
        return self.__time

    def get_avg_time(self, exclusive=True):
        """
        Gets the average time of the node.
        """
        return self.get_time(exclusive) / self.called

    @staticmethod
    def make_node_image_cache():
        """
        Makes the node image cache.

        Returns:
            The file name of the blank image.
        """
        os.makedirs(FunctionNode.NODE_IMAGE_CACHE, exist_ok=True)

        FunctionNode.NODE_IMAGE_CACHE = os.path.abspath(FunctionNode.NODE_IMAGE_CACHE)

        dim = FunctionNode.NODE_IMAGE_SCALE
        image = Image.new("RGB", (dim, dim), "white")

        file_name = f"{FunctionNode.NODE_IMAGE_CACHE}/_blank.png"
        image.save(file_name)
        return file_name

    @staticmethod
    def clear_node_image_cache():
        """
        Clears the node image cache.
        """
        for file in os.listdir(FunctionNode.NODE_IMAGE_CACHE):
            os.remove(f"{FunctionNode.NODE_IMAGE_CACHE}/{file}")
        os.rmdir(FunctionNode.NODE_IMAGE_CACHE)

    @staticmethod
    def from_dict(d):
        """
        Creates a FunctionNode from a dictionary.

        Args:
            dict: The dictionary to create the FunctionNode from.
        """
        node = FunctionNode(None)
        node.id = d["id"]
        node.uuid = d["uuid"]
        node.name = d["name"]
        node.file_path = d["file_path"]
        node.file_name = d["file_name"]
        node.called = d["called"]
        node.children_ids = [child["uuid"] for child in d["children"]]
        ex_time = d["exclusive_time"]
        in_time = d["inclusive_time"]
        node.set_time(in_time)
        node.child_time = in_time - ex_time
        return node
