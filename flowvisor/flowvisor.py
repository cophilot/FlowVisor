"""
The FlowVisor is a package that visualizes the flow of functions in a codebase.
"""
import datetime
import json
import timeit
from typing import List
#from inspect import getmembers, isfunction, ismodule
import pickle
from diagrams import Diagram, Cluster
from diagrams.custom import Custom
from flowvisor import utils
from flowvisor.flowvisor_config import FlowVisorConfig
from flowvisor.function_node import FunctionNode
from flowvisor.time_tracker import TimeTracker
from flowvisor.utils import function_to_id

def vis(func):
    """
    Decorator that visualizes the function.
    """
    def wrapper(*args, **kwargs):
        TimeTracker.stop()
        if FlowVisor.CONFIG.reduce_overhead:
            TimeTracker.apply(advanced=FlowVisor.get_advanced_overhead_reduction())
            timer_id = TimeTracker.register_new_timer()

        FlowVisor.function_called(func)

        start = TimeTracker.start()
        result = func(*args, **kwargs)
        end = TimeTracker.stop()

        duration = end - start
        if FlowVisor.CONFIG.reduce_overhead:
            TimeTracker.apply(advanced=FlowVisor.get_advanced_overhead_reduction())
            duration = TimeTracker.get_time_and_remove_timer(timer_id)

        FlowVisor.function_returned(func, duration)
        
        TimeTracker.start()
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
    def graph():
        """
        Generates the graph.
        """
        highest_time = -1
        called_nodes = FlowVisor.get_called_nodes_only()
        for node in called_nodes:
            if node.time > highest_time:
                highest_time = node.time

        try:
            with Diagram(FlowVisor.CONFIG.graph_title,
                         show=FlowVisor.CONFIG.show_graph,
                         filename=FlowVisor.CONFIG.output_file,
                         direction="LR"):

                FunctionNode.make_node_image_cache()

                if FlowVisor.CONFIG.add_timestamp:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    Custom(str(timestamp), "", width="0.001", height="0.001")

                if FlowVisor.CONFIG.logo != "":
                    Custom("", FlowVisor.CONFIG.logo,
                           width=FlowVisor.CONFIG.get_node_scale(),
                           height=FlowVisor.CONFIG.get_node_scale())

                # Draw nodes
                if FlowVisor.CONFIG.group_nodes:
                    FlowVisor.draw_nodes_with_cluster(called_nodes, highest_time)
                else:
                    for n in called_nodes:
                        FlowVisor.draw_function_node(n, highest_time)

        finally:
            # Make sure to clear the cache always
            FunctionNode.clear_node_image_cache()

    @staticmethod
    def draw_nodes_with_cluster(nodes: List[FunctionNode], highest_time: float):
        """
        Draws the nodes with cluster.
        """
        sorted_nodes = FlowVisor.get_node_sorted_by_filename(nodes)
        total_times = [sum([n.time for n in row]) for row in sorted_nodes]
        highest_time_file_time = max(total_times)
        for index, row in enumerate(sorted_nodes):
            cluster_title = f"{row[0].file_name} ({utils.get_time_as_string(total_times[index])})"
            bg_color = utils.value_to_hex_color(total_times[index], highest_time_file_time,
                                                light_color=[0xFF, 0xFF, 0xFF],
                                                dark_color=[0xAA, 0xAA, 0xAA])
            font_color = utils.value_to_hex_color(total_times[index], highest_time_file_time,
                                                light_color=[0x00, 0x00, 0x00],
                                                dark_color=[0xFF, 0xFF, 0xFF])
            with Cluster(cluster_title, graph_attr={"bgcolor": bg_color, "fontcolor": font_color}):
                for n in row:
                    FlowVisor.draw_function_node(n, highest_time)

    @staticmethod
    def get_node_sorted_by_filename(nodes: List[FunctionNode]):
        """
        Returns the nodes sorted by filename.
        """
        file_names = []
        for node in nodes:
            if node.file_path not in file_names:
                file_names.append(node.file_path)

        result = []
        for file_name in file_names:
            row = []
            for node in nodes:
                if node.file_path == file_name:
                    row.append(node)
            result.append(row)
        return result

    @staticmethod
    def get_nodes_as_dict():
        """
        Returns the nodes as a dictionary.
        """
        return [node.to_dict() for node in FlowVisor.NODES]

    @staticmethod
    def export(file: str, export_type = "pickle"):
        """
        Saves the flow to a file.
        """
        nodes_dict = FlowVisor.get_nodes_as_dict()
        if export_type == "json":
            if not file.endswith(".json"):
                file += ".json"
            with open(file, "w", encoding="utf-8") as f:
                json.dump(nodes_dict, f, indent=4)
        if export_type == "pickle":
            if not file.endswith(".pickle"):
                file += ".pickle"
            with open(file, "wb") as f:
                pickle.dump(nodes_dict, f)

    @staticmethod
    def generate_graph(file: str = ""):
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

        FlowVisor.graph()

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
    def is_stack_empty():
        """
        Checks if the stack is empty.
        """
        return len(FlowVisor.STACK) == 0

    @staticmethod
    def enable_advanced_overhead_reduction():
        """
        Enables advanced overhead reduction.
        """
        n = 50000
        t = timeit.timeit(setup="import time", stmt="time.time()", number=n)
        mean = t / n
        print(f"Mean time for time.time() is: {utils.get_time_as_string(mean)}")
        FlowVisor.CONFIG.advanced_overhead_reduction = mean

    @staticmethod
    def disable_advanced_overhead_reduction():
        """
        Disables advanced overhead reduction.
        """
        FlowVisor.CONFIG.advanced_overhead_reduction = None

    @staticmethod
    def get_advanced_overhead_reduction():
        """
        Gets the advanced overhead reduction.
        """
        return FlowVisor.CONFIG.advanced_overhead_reduction

    @staticmethod
    def enable_dev_mode():
        """
        Enables the dev mode.
        """
        FlowVisor.CONFIG.dev_mode = True

    @staticmethod
    def set_config(config: FlowVisorConfig):
        """
        Sets the configuration.
        """
        FlowVisor.CONFIG = config

    '''
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
    '''
