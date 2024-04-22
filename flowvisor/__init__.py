"""
The FlowVisor is a package that visualizes the flow of functions in a codebase.
"""
import time
import os
from typing import List
from inspect import getmembers, isfunction, ismodule
from diagrams import Diagram
from diagrams.custom import Custom
from flowvisor.flowvisor_config import FlowVisorConfig
from flowvisor.function_node import FunctionNode
from flowvisor.utils import function_to_id

def vis(func):
    """
    Decorator that visualizes the function.
    """
    def wrapper(*args, **kwargs):
        FlowVisor.function_called(func)
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        FlowVisor.function_returned(func, duration=end - start)
        return result
    return wrapper

class FlowVisor:
    """
    The FlowVisor class is responsible for managing the flow of the functions 
    and generating the graph.
    """

    NODES: List[FunctionNode] = []
    ROOTS: List[FunctionNode] = []
    STACK: List[FunctionNode] = []
    CONFIG = FlowVisorConfig()

    EXCLUDE_FUNCTIONS = []

    @staticmethod
    def add_function_node(func):
        """
        Adds a function node to the list of nodes if it does not exist.
        """
        func_id = function_to_id(func)
        for node in FlowVisor.NODES:
            if node.id == func_id:
                return node
        node = FunctionNode(func)
        FlowVisor.NODES.append(node)
        return node

    @staticmethod
    def function_called(func):
        """
        Called when a function is called.
        """
        if FlowVisor.is_function_excluded(func):
            return

        node =FlowVisor.add_function_node(func)
        if len(FlowVisor.STACK) == 0:
            FlowVisor.ROOTS.append(node)
        else:
            parent = FlowVisor.STACK[-1]
            parent.add_child(node)

        FlowVisor.STACK.append(node)

    @staticmethod
    def function_returned(func, duration):
        """
        Calls when a function is returned.
        """
        if len(FlowVisor.STACK) == 0:
            return

        if FlowVisor.is_function_excluded(func):
            return

        node = FlowVisor.STACK.pop()
        node.got_called(duration)

    @staticmethod
    def get_called_nodes_only():
        """
        Returns only the nodes that have been called.
        """
        return [node for node in FlowVisor.NODES if node.called > 0]

    @staticmethod
    def generate_graph():
        """
        Generates the graph.
        """
        highest_time = 0
        called_nodes = FlowVisor.get_called_nodes_only()
        for node in called_nodes:
            if node.time > highest_time:
                highest_time = node.time

        try:
            FunctionNode.make_node_image_cache()
            with Diagram(FlowVisor.CONFIG.graph_title,
                         show=FlowVisor.CONFIG.show_graph,
                         filename=FlowVisor.CONFIG.output_file,
                         direction="LR"):
                # Add logo
                if FlowVisor.CONFIG.logo != "":
                    Custom("", FlowVisor.CONFIG.logo,
                           width=FlowVisor.CONFIG.get_node_scale(),
                           height=FlowVisor.CONFIG.get_node_scale())

                # Draw nodes
                for r in called_nodes:
                    FlowVisor.draw_function_node(r, highest_time)
        finally:
            FunctionNode.clear_node_image_cache()

    @staticmethod
    def draw_function_node(func_node: FunctionNode, highest_time):
        """
        Draws the function node.
        """
        node = func_node.get_as_diagram_node(highest_time, FlowVisor.CONFIG)
        for child in func_node.children:
            _ = node >> child.get_as_diagram_node(highest_time, FlowVisor.CONFIG)

    @staticmethod
    def is_function_excluded(func):
        """
        Checks if a function is excluded.
        """
        func_id = function_to_id(func)
        for exclude_func in FlowVisor.EXCLUDE_FUNCTIONS:
            # check if exclude_func is a substring of func_id
            if exclude_func in func_id:
                return True
        return False

    @staticmethod
    def exclude_function(func_id: str):
        """
        Excludes a function from the graph.
        """
        FlowVisor.EXCLUDE_FUNCTIONS.append(func_id)

    @staticmethod
    def set_exclude_functions(exclude_functions: List[str]):
        """
        Sets the exclude functions.
        """
        FlowVisor.EXCLUDE_FUNCTIONS = exclude_functions

    @staticmethod
    def visualize_all():
        """
        Visualizes all the functions in this project.
        """
        FlowVisor.visualize_module_by_name("__main__")

    @staticmethod
    def visualize_module_by_name(module_name: str):
        """
        Visualizes all the functions in a module.
        """
        module = __import__(module_name)

        FlowVisor.visualize_module(module)

    @staticmethod
    def visualize_module(module: object):
        """
        Visualizes all the functions in a module.
        """
        for name, obj in getmembers(module, isfunction):
            setattr(module, name, vis(obj))

         # add for all submodules
        for name, sub_module in getmembers(module, ismodule):
            FlowVisor.visualize_module(sub_module)
