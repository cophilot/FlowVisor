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


class FunctionNode:
    """
    A node in the function call graph
    """

    NODE_IMAGE_CACHE = "__flowvisor_node_image_cache__"
    NODE_IMAGE_SCALE = 300

    def __init__(self, func):
        self.id: str = utils.function_to_id(func)
        self.uuid = uuid.uuid4()
        self.name: str = func.__name__
        self.file_path: str = func.__code__.co_filename
        self.file_name: str = os.path.basename(self.file_path)
        self.children: List[FunctionNode] = []
        self.time: float = 0
        self.diagram_node = None
        self.called: int = 0

    def export_node_image(self, highest_time):
        """
        Generates the node image background.
        """
        dim = FunctionNode.NODE_IMAGE_SCALE
        image = Image.new('RGB', (dim, dim), 'white')
        draw = ImageDraw.Draw(image)

        color = utils.value_to_hex_color(self.time, highest_time)

        if self.time >= highest_time * 0.9:
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

    def get_as_diagram_node(self,highest_time: float, config: FlowVisorConfig):
        """
        Gets the node as a diagram node.
        """
        if self.diagram_node is None:
            self.generate_diagram_node(highest_time, config)
        return self.diagram_node

    def generate_diagram_node(self,highest_time: float, config: FlowVisorConfig):
        """
        Generates the diagram node.
        """
        circle_file = self.export_node_image(highest_time)

        size = self.time / highest_time
        if size < 0.1:
            size = 0.1

        size = 1
        size = size * config.node_scale

        title = self.get_node_title(config)

        font_color = config.static_font_color
        if font_color == "":
            font_color = utils.font_color_to_hex_color(self.time, highest_time)

        self.diagram_node = Custom(title, circle_file, 
                                   width=str(size), 
                                   height=str(size), 
                                   fontcolor=font_color)

    def get_node_title(self, config: FlowVisorConfig):
        """
        Returns the title of the node, that is displayed in the diagram.
        """
        title = self.name + "\n"

        if config.node_show_file:
            title += self.file_name + "\n"

        title += utils.get_time_as_string(self.time)

        if config.node_show_call_count:
            title += f" ({self.called})"

        title += "\n"

        if config.node_show_avg_time:
            title += f"avg {utils.get_time_as_string(self.time / self.called)}"

        for _ in range(int(config.node_scale)):
            title += "\n\n"
        return title

    def got_called(self,duration: float):
        """
        The function got called.
        
        Args:
            duration: The time it took to execute the function.
        """
        self.called += 1
        self.set_time(duration)

    def add_child(self, child): # type: ignore
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
        self.time += time

    def to_json(self, inline = 0):
        """
        Returns the node as a json string.
        
        Args:
            inline: The number of spaces to indent.
        """
        inline_str = "  " * inline
        result = f'"{self.file_function_name()}({self.time})"'
        if len(self.children) == 0:
            return inline_str + result
        result += ":["
        for index,child in enumerate(self.children):
            if index > 0:
                result += ","
            result += f"\n{child.to_json(inline + 1)}"
        result += f"\n{inline_str}]"
        result = inline_str + "{"+ result + "}"
        return result

    def file_function_name(self):
        """
        Returns the file name and function name.
        """
        return f"{self.file_name}::{self.name}"

    def __str__(self):
        return self.file_function_name()

    @staticmethod
    def make_node_image_cache():
        """
        Makes the node image cache.
        """
        os.makedirs(FunctionNode.NODE_IMAGE_CACHE, exist_ok=True)

    @staticmethod
    def clear_node_image_cache():
        """
        Clears the node image cache.
        """    
        for file in os.listdir(FunctionNode.NODE_IMAGE_CACHE):
            os.remove(f"{FunctionNode.NODE_IMAGE_CACHE}/{file}")
        os.rmdir(FunctionNode.NODE_IMAGE_CACHE)