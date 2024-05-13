import os
import time


class Logger:

    LOG_FILE = None
    LOG_TO_CONSOLE = True

    @staticmethod
    def log(ms: str):
        Logger.log_to_console(ms)
        Logger.log_to_file(ms)

    @staticmethod
    def log_to_file(ms: str):
        if Logger.LOG_FILE is None:
            return
        time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ms = f"[{time_stamp}] {ms}"
        with open(Logger.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{ms}\n")

    @staticmethod
    def log_to_console(ms: str):
        if not Logger.LOG_TO_CONSOLE:
            return
        ms = f"[FlowVisor] {ms}"
        print(ms)

    @staticmethod
    def set_log_file(file: str):
        Logger.LOG_FILE = file
        if not os.path.exists(Logger.LOG_FILE):
            with open(Logger.LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")
