import cProfile
import json
import os
import pstats
import time
from typing import List

from flowvisor import logger, utils
from flowvisor.function_node import FunctionNode


def vis_verifier(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        FlowVisorVerifier.add_entry(func, time.time() - start)
        return res

    return wrapper


def vis_verifier2(func):
    def wrapper(*args, **kwargs):

        pr = cProfile.Profile()  # create new Profiler object
        pr.enable()  # start recording of time for Profiler
        res = func(*args, **kwargs)
        pr.disable()  # stop recording of time for Profiler
        # get the time that the function took

        p = pstats.Stats(pr)
        total_time = p.total_tt
        FlowVisorVerifier.add_entry(func, total_time)
        time_str = utils.get_time_as_string(total_time)
        print(f"Function {func.__name__} took {time_str} seconds")
        return res

    return wrapper


class FlowVisorVerifier:

    ENTRIES = []

    @staticmethod
    def add_entry(func, time: float):
        FlowVisorVerifier.ENTRIES.append(
            {"id": utils.function_to_id(func), "time": time}
        )

    @staticmethod
    def summaries_entries(entries):
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
        file_name = utils.apply_file_end(file_name, "json")
        new_entries = FlowVisorVerifier.summaries_entries(FlowVisorVerifier.ENTRIES)
        device_name = utils.get_device_name()
        meta = {"device_name": device_name, "count": 0}
        old_data = None

        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                existing_content = json.load(f)
            meta = existing_content["meta"]
            old_data = existing_content["data"]
            new_entries = FlowVisorVerifier.avarage_entries(
                old_data, new_entries, meta["count"]
            )

        new_entries = FlowVisorVerifier.set_min_max(old_data, new_entries)

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
    def avarage_entries(old_data, new_data, count):
        for entry in new_data:
            id_exists = False
            for old_entry in old_data:
                if old_entry["id"] == entry["id"]:
                    old_entry["time"] = (old_entry["time"] * count + entry["time"]) / (
                        count + 1
                    )
                    id_exists = True
                    break
            if not id_exists:
                old_data.append(entry)

        return old_data

    @staticmethod
    def set_min_max(old_data, new_data):
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
    def verify(nodes: List[FunctionNode], verify_file_name: str, threshold: float):
        verify_file_name = utils.apply_file_end(verify_file_name, "json")

        if not os.path.exists(verify_file_name):
            logger.log(f"Verify file {verify_file_name} not found...")
            return

        with open(verify_file_name, "r", encoding="utf-8") as f:
            content = json.load(f)

        is_verified = True
        device_name = content["meta"]["device_name"]
        if device_name != utils.get_device_name():
            logger.log(
                f"🚨 WARNING 🚨 Verifier file is not clean: Wrong device {device_name}"
            )
            is_verified = False

        for entry in content["data"]:
            node = utils.get_node_by_id(entry["id"], nodes)
            if node is None:
                logger.log(f"Function with id {entry['id']} not found")
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
            if time_delta < 0:
                time_delta *= -1
                time_delta_direction = "less"

            logger.log(
                f"Function '{node.name}' took {utils.get_time_as_string(time_delta)} {time_delta_direction} than expected ({time_delta_percentage * 100}%) {'🚨' if print_warning else ''}"
            )

        if is_verified:
            logger.log("All functions are verified! ✅")
        else:
            logger.log("Some functions are not verified! ❌")
        return is_verified

    @staticmethod
    def is_function_verified(entry, node_time, threshold):
        mean_time = entry["time"]
        interval = entry["max"] - entry["min"]
        offset = max(interval, mean_time * threshold)

        return mean_time - offset <= node_time and node_time <= mean_time + offset
