import collections
from collections import deque
from messagingutils.messaging import Message


class MessageQueue:
    """A queue of messages to be sent to clients. Elements are messages."""

    def __init__(self):
        self.queue: collections.deque[Message] = deque()

    def __bool__(self):
        """Return True if the queue is not empty."""
        return bool(self.queue)

    def add_message(self, message: Message):
        self.queue.append(message)

    def get_top_message(self) -> Message:
        """Get the top message from the queue. If the queue is empty, return None."""
        if self.queue:
            return self.queue.popleft()
