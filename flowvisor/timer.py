import uuid


class Timer:

    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.time: float = 0

    def add_time(self, time: float):
        """
        Adds time to the timer.

        Args:
            time (float): The time to add.
        """
        self.time += time
