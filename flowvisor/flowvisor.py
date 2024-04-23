"""
The FlowVisor is a package that visualizes the flow of functions in a codebase.
"""
import time
import json
from typing import List
from inspect import getmembers, isfunction, ismodule
import pickle
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
    def get_nodes_as_dict():
        """
        Returns the nodes as a dictionary.
        """
        return [node.to_dict() for node in FlowVisor.NODES]

    @staticmethod
    def save_flow(file: str, type = "pickle"):
        """
        Saves the flow to a file.
        """
        nodes_dict = FlowVisor.get_nodes_as_dict()
        if type == "json":
            if not file.endswith(".json"):
                file += ".json"
            with open(file, "w", encoding="utf-8") as f:
                json.dump(nodes_dict, f, indent=4)
        if type == "pickle":
            if not file.endswith(".pickle"):
                file += ".pickle"
            with open(file, "wb") as f:
                pickle.dump(nodes_dict, f)

    @staticmethod
    def generate_graph_from_file(file: str):
        """
        Generates the graph from a file.
        """
        mode = "pickle"
        if file.endswith(".json"):
            mode = "json"
        if mode == "json":
            with open(file, "r", encoding="utf-8") as f:
                raw_nodes = json.load(f)
        else:
            with open(file, "rb") as f:
                raw_nodes = pickle.load(f)
        
        for n in raw_nodes:
            node = FunctionNode.from_dict(n)
            FlowVisor.NODES.append(node)
        for node in FlowVisor.NODES:
            node.resolve_children_ids(FlowVisor.NODES)
        
        FlowVisor.generate_graph()

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
        FlowVisor.visualize_module_helper(module, [])
    
    @staticmethod
    def visualize_module_helper(module: object, added_modules):
        """
        Visualizes all the functions in a module.
        """
        print("This function is still buggy and will not work as expected. Workin on it!")
        for name, obj in getmembers(module, isfunction):
            setattr(module, name, vis(obj))

        # TODO
        # # add for all submodules
        #for name, sub_module in getmembers(module, ismodule):
        #    if sub_module.__name__ in added_modules:
        #        with open(f"log.txt", "a") as f:
        #            f.write(f"NOT Visualizing module: {sub_module.__name__}\n")
#
        #        continue
        #    added_modules.append(sub_module.__name__)
        #    print(f"Visualizing module: {sub_module.__name__}")
        #    # write to a file
        #    with open(f"log.txt", "a") as f:
        #        f.write(f"Visualizing module: {sub_module.__name__}\n")
        #    FlowVisor.visualize_module_helper(sub_module, added_modules)
