import collections
from collections import deque
import socket
from typing import Tuple


class MessageQueue:
    """A queue of messages to be sent to clients. Elements are tuples of (recipient, message)."""

    def __init__(self):
        self.queue: collections.deque[(socket, bytes)] = deque()

    def __bool__(self):
        """Return True if the queue is not empty."""
        return bool(self.queue)

    def add_message(self, recipient, message):
        self.queue.append((recipient, message))

    def get_top_message(self) -> Tuple[int, bytes]:
        """Get the top message from the queue. If the queue is empty, return None."""

        if self.queue:
            return self.queue.popleft()
