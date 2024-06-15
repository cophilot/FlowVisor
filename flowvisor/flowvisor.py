"""
The FlowVisor is a package that visualizes the flow of functions in a codebase.
"""

import datetime
import json
import os
import timeit
from typing import List
import pickle
from diagrams import Diagram, Cluster
from diagrams.custom import Custom
from flowvisor import utils
from flowvisor.logger import Logger
from flowvisor.flowvisor_config import FlowVisorConfig
from flowvisor.flowvisor_verifier import FlowVisorVerifier, c_vis_verifier, vis_verifier
from flowvisor.function_node import FunctionNode
from flowvisor.sankey import make_sankey_diagram
from flowvisor.time_tracker import TimeTracker
from flowvisor.time_value import TimeValue
from flowvisor.utils import function_to_id


def vis(func):
    """
    The vis decorator
    """

    def wrapper(*args, **kwargs):
        return FlowVisor.VIS_FUNCTION(func)(*args, **kwargs)

    return wrapper


def vis_impl(func):
    """
    Decorator that visualizes the function.
    """

    def wrapper(*args, **kwargs):
        TimeTracker.stop()

        reduce_overhead = FlowVisor.CONFIG.reduce_overhead
        if reduce_overhead:
            TimeTracker.apply(advanced=FlowVisor.get_advanced_overhead_reduction())
            timer_id = TimeTracker.register_new_timer()

        FlowVisor.function_called(func)

        start = TimeTracker.start(reduce_overhead)
        result = func(*args, **kwargs)
        end = TimeTracker.stop()

        duration = end - start
        if reduce_overhead:
            TimeTracker.apply(advanced=FlowVisor.get_advanced_overhead_reduction())
            duration = TimeTracker.get_time_and_remove_timer(timer_id)

        FlowVisor.function_returned(func, duration)

        TimeTracker.start(reduce_overhead)
        return result

    return wrapper


def do_nothing(func):
    """
    Decorator that does nothing.
    """

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class FlowVisor:
    """
    The FlowVisor class is responsible for managing the flow of the functions
    and generating the graph.
    """

    VIS_FUNCTION = vis_impl
    VIS_FUNCTION_CACHE = vis_impl

    NODES: List[FunctionNode] = []
    ROOTS: List[FunctionNode] = []
    STACK: List[FunctionNode] = []
    CONFIG = FlowVisorConfig()

    EXCLUDE_FUNCTIONS = []
    VERIFIER_MODE = False
    DISABLED = False

    SYS_INFO = None

    @staticmethod
    def reset():
        """
        Resets FlowVisor.
        """
        FlowVisor.VIS_FUNCTION = vis_impl
        FlowVisor.VIS_FUNCTION_CACHE = vis_impl
        FlowVisor.NODES = []
        FlowVisor.ROOTS = []
        FlowVisor.STACK = []
        FlowVisor.CONFIG = FlowVisorConfig()
        FlowVisor.EXCLUDE_FUNCTIONS = []
        FlowVisor.VERIFIER_MODE = False
        FlowVisor.DISABLED = False
        FlowVisor.SYS_INFO = None

    @staticmethod
    def disable():
        """
        Disables the flowvisor.
        """
        FlowVisor.VIS_FUNCTION = do_nothing
        FlowVisor.DISABLED = True

    @staticmethod
    def enable():
        """
        Enables the flowvisor.
        """
        FlowVisor.VIS_FUNCTION = FlowVisor.VIS_FUNCTION_CACHE
        FlowVisor.DISABLED = False

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
    def add_root_node(node):
        """
        Adds a root node.
        """
        for root in FlowVisor.ROOTS:
            if root.id == node.id:
                return
        FlowVisor.ROOTS.append(node)

    @staticmethod
    def function_called(func):
        """
        Called when a function is called.
        """
        if FlowVisor.is_function_excluded(func):
            return

        node = FlowVisor.add_function_node(func)

        if len(FlowVisor.STACK) == 0:
            FlowVisor.add_root_node(node)
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

        if len(FlowVisor.STACK) > 0:
            parent = FlowVisor.STACK[-1]
            parent.child_time += duration

        node.got_called(duration)

    @staticmethod
    def get_called_nodes_only():
        """
        Returns only the nodes that have been called.
        """
        return [node for node in FlowVisor.NODES if node.called > 0]

    @staticmethod
    def graph(verify=False, verify_file_name="flowvisor_verifier.json"):
        """
        Generates the graph.
        """
        if FlowVisor.DISABLED:
            Logger.log("Can not generate graph when disabled!")
            return
        if FlowVisor.VERIFIER_MODE:
            Logger.log("Can not generate graph in verifier mode!")
            return

        verify_text = None
        if verify:
            if FlowVisor.verify(verify_file_name):
                verify_text = "Verified ✅"
            else:
                verify_text = "Not Verified ❌"

        try:
            with Diagram(
                FlowVisor.CONFIG.graph_title,
                show=FlowVisor.CONFIG.show_graph,
                filename=FlowVisor.CONFIG.output_file,
                direction="LR",
            ):

                blank_image = FunctionNode.make_node_image_cache()

                FlowVisor.draw_meta_data(blank_image, verify_text)

                if FlowVisor.CONFIG.logo != "":
                    Custom(
                        "",
                        FlowVisor.CONFIG.logo,
                        width=FlowVisor.CONFIG.get_node_scale(),
                        height=FlowVisor.CONFIG.get_node_scale(),
                    )

                called_nodes = FlowVisor.get_called_nodes_only()

                # Draw nodes
                if FlowVisor.CONFIG.group_nodes:
                    FlowVisor.draw_nodes_with_cluster(called_nodes)
                else:
                    for n in called_nodes:
                        FlowVisor.draw_function_node(n)

        finally:
            # Make sure to clear the cache always
            FunctionNode.clear_node_image_cache()

    @staticmethod
    def sankey_diagram():
        """
        Generates the sankey diagram.
        """
        make_sankey_diagram(FlowVisor.ROOTS, FlowVisor.NODES)

    @staticmethod
    def draw_meta_data(blank_image, verify_text):
        """
        Draws some metadata on the graph.
        """
        with Cluster("Metadata", graph_attr={"bgcolor": "#FFFFFF"}):
            if verify_text is not None:
                Custom(verify_text, blank_image, width="2", height="0.1")
            if FlowVisor.CONFIG.show_system_info:
                sys_info = FlowVisor.SYS_INFO
                if sys_info is None:
                    sys_info = utils.get_sys_info()
                text = ""
                for key, value in sys_info.items():
                    text += f"{key}: {value}\n"
                Custom(text, blank_image, width="6", height="1")
            if FlowVisor.CONFIG.show_timestamp:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                Custom(str(timestamp), blank_image, width="3", height="0.2")
            if FlowVisor.CONFIG.show_flowvisor_settings:
                s = FlowVisor.CONFIG.get_functional_settings_string()
                Custom(str(s), blank_image, width="4", height="0.2")

    @staticmethod
    def draw_nodes_with_cluster(nodes: List[FunctionNode]):
        """
        Draws the nodes with cluster.
        """
        sorted_nodes = FlowVisor.get_node_sorted_by_filename(nodes)
        total_times = [sum([n.get_time() for n in row]) for row in sorted_nodes]
        highest_time_file_time = max(total_times)
        for index, row in enumerate(sorted_nodes):
            cluster_title = (
                f"{row[0].file_name} ({utils.get_time_as_string(total_times[index])})"
            )
            bg_color = utils.value_to_hex_color(
                total_times[index],
                highest_time_file_time,
                light_color=[0xFF, 0xFF, 0xFF],
                dark_color=[0xAA, 0xAA, 0xAA],
            )
            font_color = utils.value_to_hex_color(
                total_times[index],
                highest_time_file_time,
                light_color=[0x00, 0x00, 0x00],
                dark_color=[0xFF, 0xFF, 0xFF],
            )
            with Cluster(
                cluster_title, graph_attr={"bgcolor": bg_color, "fontcolor": font_color}
            ):
                for n in row:
                    FlowVisor.draw_function_node(n)

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
    def export(file: str, export_type="pickle"):
        """
        Saves the flow to a file.
        """
        if FlowVisor.DISABLED:
            Logger.log("Can not export when disabled!")
            return
        if FlowVisor.VERIFIER_MODE:
            Logger.log("Can not export in verifier mode!")
            return

        nodes_dict = FlowVisor.get_nodes_as_dict()
        settings = FlowVisor.CONFIG.to_dict()
        sys_info = utils.get_sys_info()

        data = {"data": nodes_dict, "settings": settings, "sys-info": sys_info}

        if export_type == "json":
            if not file.endswith(".json"):
                file += ".json"
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        if export_type == "pickle":
            if not file.endswith(".pickle"):
                file += ".pickle"
            with open(file, "wb") as f:
                pickle.dump(data, f)

    @staticmethod
    def generate_graph(
        file: str = "",
        verify=False,
        verify_file_name="flowvisor_verifier.json",
        use_verifier_time_as_inclusive_time=False,
        config: dict = None,
    ):
        """
        Generates the graph from a file.
        """
        if not os.path.exists(file):
            Logger.log(f"File {file} does not exist!")
            return
        mode = "pickle"
        if file.endswith(".json"):
            mode = "json"

        if mode == "json":
            with open(file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        else:
            with open(file, "rb") as f:
                raw_data = pickle.load(f)

        if "data" in raw_data:
            raw_nodes = raw_data["data"]
        else:
            raw_nodes = raw_data

        if use_verifier_time_as_inclusive_time:
            if not os.path.exists(verify_file_name):
                Logger.log(f"File {verify_file_name} does not exist!")
            else:
                with open(verify_file_name, "r", encoding="utf-8") as f:
                    verifier_data = json.load(f)["data"]

                if "data" in verifier_data:
                    verifier_data = verifier_data["data"]

                for node in raw_nodes:
                    for verifier_node in verifier_data:
                        if node["id"] == verifier_node["id"]:
                            node["inclusive_time"] = verifier_node["time"]

        if "settings" in raw_data:
            FlowVisor.CONFIG = FlowVisorConfig.from_dict(raw_data["settings"])

        if config is not None:
            for key, value in config.items():
                setattr(FlowVisor.CONFIG, key, value)

        if "sys-info" in raw_data:
            FlowVisor.SYS_INFO = raw_data["sys-info"]

        for n in raw_nodes:
            node = FunctionNode.from_dict(n)
            FlowVisor.NODES.append(node)
        for node in FlowVisor.NODES:
            node.resolve_children_ids(FlowVisor.NODES)

        FlowVisor.graph(verify, verify_file_name)

    @staticmethod
    def draw_function_node(func_node: FunctionNode):
        """
        Draws the function node.
        """
        time_value = TimeValue(FlowVisor.NODES, FlowVisor.CONFIG)

        node = func_node.get_as_diagram_node(time_value, FlowVisor.CONFIG)
        if node is None:
            return
        for child in func_node.children:
            child_node = child.get_as_diagram_node(time_value, FlowVisor.CONFIG)
            if child_node is not None:
                _ = node >> child_node

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
        Logger.log(f"Mean time for time.time() is: {utils.get_time_as_string(mean)}")
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
    def conf(config: dict):
        """
        Sets the configuration.
        """
        FlowVisor.set_config(config)

    @staticmethod
    def set_config(config: dict):
        """
        Sets the configuration.
        """

        FlowVisor.CONFIG = FlowVisorConfig.from_dict(config)

    @staticmethod
    def auto_verifier_mode(
        verifier_limit=10, file_name="flowvisor_verifier.json", use_c_profile=False
    ):
        """
        Automatically enables the verifier mode.
        """
        count = FlowVisorVerifier.get_count_of_file(file_name)
        if count < verifier_limit:
            FlowVisor.enable_verifier_mode(use_c_profile=use_c_profile)
            return
        Logger.log(
            f"Verifier mode not enabled. Count of calls is {count} and the limit is {verifier_limit}"
        )

    @staticmethod
    def enable_verifier_mode(force=False, use_c_profile=False):
        """
        Enables the verifier mode.

        :param force: If True, the verifier mode will be enabled even if the FlowVisor is disabled.
        """
        if FlowVisor.DISABLED and not force:
            Logger.log("Can not enable verifier mode when disabled!")
            return
        FlowVisor.VERIFIER_MODE = True
        FlowVisor.VIS_FUNCTION = vis_verifier
        FlowVisor.VIS_FUNCTION_CACHE = vis_verifier
        if use_c_profile:
            FlowVisor.VIS_FUNCTION = c_vis_verifier
            FlowVisor.VIS_FUNCTION_CACHE = c_vis_verifier
            Logger.log("*** Running FlowVisor in verify mode with cProfile ***")
        else:
            Logger.log("*** Running FlowVisor in verify mode ***")

    @staticmethod
    def verify_export(file_name="flowvisor_verifier.json"):
        """
        Exports the verifier.
        """
        if FlowVisor.DISABLED:
            Logger.log("Can not export verify when disabled!")
            return
        if not FlowVisor.VERIFIER_MODE:
            Logger.log("Can not export verify in non-verifier mode!")
            return
        FlowVisorVerifier.export(file_name)

    @staticmethod
    def verify(verify_file_name="flowvisor_verifier.json"):
        """
        Checks the result against the verifier.
        """
        if FlowVisor.DISABLED:
            Logger.log("Can not verify when disabled!")
            return False
        if FlowVisor.VERIFIER_MODE:
            Logger.log("Can not verify in verifier mode!")
            return False
        return FlowVisorVerifier.verify(
            FlowVisor.NODES, verify_file_name, FlowVisor.CONFIG.verify_threshold
        )

    @staticmethod
    def set_log_file(file_name: str = "flowvisor.log"):
        """
        Sets the log file.
        """
        Logger.LOG_FILE = file_name

    @staticmethod
    def disable_console_logging():
        """
        Disables console logging.
        """
        Logger.LOG_TO_CONSOLE = False
