import cProfile
import json
import os
import pstats
import time
from typing import List

from flowvisor import utils
from flowvisor.logger import Logger
from flowvisor.function_node import FunctionNode


def vis_verifier(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        FlowVisorVerifier.add_entry(func, time.time() - start)
        return res

    return wrapper


def c_vis_verifier(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        res = func(*args, **kwargs)
        profiler.disable()
        stats = pstats.Stats(profiler)
        time_value = stats.total_tt
        FlowVisorVerifier.add_entry(func, time_value)
        return res

    return wrapper


class FlowVisorVerifier:
    """
    FlowVisor verifier class
    """

    ENTRIES = []

    @staticmethod
    def add_entry(func, time_value: float):
        """
        Add an entry to the verifier
        """
        FlowVisorVerifier.ENTRIES.append(
            {"id": utils.function_to_id(func), "time": time_value}
        )

    @staticmethod
    def summaries_entries(entries):
        """
        Summarize the entries by adding the time of the same id
        """
        new_entries = []
        for entry in entries:
            id_exists = False
            for new_entry in new_entries:
                if new_entry["id"] == entry["id"]:
                    new_entry["time"] += entry["time"]
                    id_exists = True
                    break
            if not id_exists:
                new_entries.append(entry)
        return new_entries

    @staticmethod
    def export(file_name: str):
        """
        Export the verifier entries to a file
        """
        new_entries = FlowVisorVerifier.summaries_entries(FlowVisorVerifier.ENTRIES)

        device_name = utils.get_device_name()
        meta = {"device_name": device_name, "count": 0}
        old_data = None

        existing_content = FlowVisorVerifier.read_existing_file(file_name)

        if existing_content is not None:
            meta = existing_content["meta"]
            old_data = existing_content["data"]

        new_entries = FlowVisorVerifier.add_trace(old_data, new_entries)
        new_entries = FlowVisorVerifier.set_min_max(old_data, new_entries)
        new_entries = FlowVisorVerifier.avarage_entries(new_entries)

        # parse meta data
        meta["count"] += 1
        ex_device_name = meta["device_name"]
        if device_name not in ex_device_name:
            meta["device_name"] = f"{ex_device_name};;{device_name}"
        content = {
            "meta": meta,
            "data": new_entries,
        }

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4)

    @staticmethod
    def avarage_entries(entries):
        """
        Avergae the entries
        """
        for entry in entries:
            entry["time"] = sum(entry["trace"]) / len(entry["trace"])
        return entries

    @staticmethod
    def set_min_max(old_data, new_data):
        """
        Sets the min and max values for the entries

        Args:
            old_data (dict): The old data
            new_data (dict): The new data

        Returns:
            dict: The new data with min and max values
        """
        if old_data is None:
            for entry in new_data:
                entry["min"] = entry["time"]
                entry["max"] = entry["time"]
            return new_data

        for entry in new_data:
            for old_entry in old_data:
                if old_entry["id"] == entry["id"]:
                    entry["min"] = min(old_entry["min"], entry["time"])
                    entry["max"] = max(old_entry["max"], entry["time"])
                    break
        return new_data

    @staticmethod
    def add_trace(old_data, new_data):
        """
        Add the time trace to the data
        """
        if old_data is None:
            for entry in new_data:
                entry["trace"] = [entry["time"]]
            return new_data

        for entry in new_data:
            for old_entry in old_data:
                if old_entry["id"] == entry["id"]:
                    entry["trace"] = old_entry["trace"]
                    entry["trace"].append(entry["time"])
                    break
        return new_data

    @staticmethod
    def verify(nodes: List[FunctionNode], verify_file_name: str, threshold: float):
        verify_file_name = utils.apply_file_end(verify_file_name, "json")

        if not os.path.exists(verify_file_name):
            Logger.log(f"Verify file {verify_file_name} not found...")
            return

        content = FlowVisorVerifier.read_existing_file(verify_file_name)

        is_verified = True
        device_name = content["meta"]["device_name"]
        if device_name != utils.get_device_name():
            Logger.log(
                f"🚨 WARNING 🚨 Verifier file is not clean: Wrong device {device_name}"
            )
            is_verified = False

        Logger.log("Verifying functions...")
        for entry in content["data"]:
            node = utils.get_node_by_id(entry["id"], nodes)
            if node is None:
                Logger.log(f"Function with id {entry['id']} not found")
                continue

            node_time = node.get_time(exclusive=False)
            verify_time = entry["time"]
            time_delta = node_time - verify_time

            # get how many percent the node time is off
            time_delta_percentage = time_delta / verify_time
            print_warning = False

            if not FlowVisorVerifier.is_function_verified(entry, node_time, threshold):
                is_verified = False
                print_warning = True

            time_delta_direction = "more"
            time_delta_direction_arrow = "🔼"
            if time_delta < 0:
                time_delta *= -1
                time_delta_direction = "less"
                time_delta_direction_arrow = "🔽"

            Logger.log(
                f"  Function '{node.file_function_name()}' took {utils.get_time_as_string(time_delta)} {time_delta_direction} than expected ({time_delta_percentage * 100}%) {time_delta_direction_arrow}{'🚨' if print_warning else ''}"
            )

        if is_verified:
            Logger.log("All functions are verified! ✅")
        else:
            Logger.log("Some functions are not verified! ❌")
        return is_verified

    @staticmethod
    def is_function_verified(entry, node_time, threshold):
        max_value = entry["max"]
        min_value = entry["min"]
        mean_time = entry["time"]

        if min_value <= node_time and node_time <= max_value:
            return True

        offset = mean_time * threshold
        return mean_time - offset <= node_time and node_time <= mean_time + offset

    @staticmethod
    def read_existing_file(file_name: str):
        """
        Read the existing verifier file

        Args:
            file_name (str): The file name

        Returns:
            dict: The content of the file or None if the file does not exist
        """
        file_name = utils.apply_file_end(file_name, "json")
        if not os.path.exists(file_name):
            return None
        with open(file_name, "r", encoding="utf-8") as f:
            content = json.load(f)
        return content

    @staticmethod
    def get_count_of_file(file_name: str):
        """
        Get the calls of a file

        Args:
            file_name (str): The file name

        Returns:
            int: The number of calls
        """
        content = FlowVisorVerifier.read_existing_file(file_name)
        if content is None:
            return 0
        return content["meta"]["count"]
