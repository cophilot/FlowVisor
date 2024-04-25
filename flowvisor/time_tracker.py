import time
from flowvisor.timer import Timer

class TimeTracker:

    TIMERS = []
    START_TIME = None
    END_TIME = None

    @staticmethod
    def stop():
        """
        Stops the time tracker.
        
        Returns:
            The end time.
        """
        # no code here!
        end = time.time()
        TimeTracker.END_TIME = end
        return end

    @staticmethod
    def apply(advanced = None):
        """
        Applies the time tracker.
        """
        if TimeTracker.START_TIME is None or TimeTracker.END_TIME is None:
            return

        interval_time = TimeTracker.END_TIME - TimeTracker.START_TIME

        if advanced is not None:
            # Substract the overhead time for each timestamp taken
            interval_time = interval_time - (advanced * 2)

        TimeTracker.add_time_to_all_timers(interval_time)
        TimeTracker.START_TIME = None
        TimeTracker.END_TIME = None

    @staticmethod
    def start(reduce_overhead: bool):
        """
        Starts the time tracker.
        
        Returns:
            The start time.
        """

        if reduce_overhead and TimeTracker.START_TIME is not None:
            print("[FlowVisor.INTERNAL] Time tracker is already running.")
            return TimeTracker.START_TIME

        TimeTracker.START_TIME = time.time()
        # no code here!
        return TimeTracker.START_TIME

    @staticmethod
    def add_time_to_all_timers(t: float):
        """
        Adds time to all timers.
        
        Args:
            time: The time to add.
        """
        for timer in TimeTracker.TIMERS:
            timer.add_time(t)

    @staticmethod
    def get_time_and_remove_timer(timer_id: str) -> float:
        """
        Removes a timer and returns the time.
        
        Args:
            timer_id: The id of the timer to remove.
            
        Returns:
            The time of the timer.
        """

        for index, timer in enumerate(TimeTracker.TIMERS):
            if timer.id == timer_id:
                TimeTracker.TIMERS.pop(index)
                return timer.time

        print("[FlowVisor.INTERNAL] Could not find timer with id: " + timer_id)
        return 0

    @staticmethod
    def register_new_timer() -> str:
        """
        Registers a new timer.
        
        Returns:
            The id of the timer.
        """
        timer = Timer()
        TimeTracker.TIMERS.append(timer)
        return timer.id

    @staticmethod
    def is_running() -> bool:
        """
        Checks if the time tracker is running.
        
        Returns:
            True if the time tracker is running, False otherwise.
        """
        return TimeTracker.START_TIME is not None
