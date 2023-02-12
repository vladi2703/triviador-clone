import json
from enum import Enum


class MessageTypes(Enum):
    """Enum of message types."""
    DISCONNECT = 0
    GET_QUESTION = 1
    QUESTION = 2
    ANSWER = 3
    CORRECT_ANSWER = 4
    INCORRECT_ANSWER = 5
    REQUEST_ACTIVE_STATUS = 7
    ACTIVE_STATUS = 8
    LOBBY_ALREADY_FULL = 9
    REQUEST_BOARD = 10
    BOARD = 11
    REQUEST_MOVE_PLAYER = 12
    MOVE_PLAYER = 13

    def to_json(self):
        return self.value


class MessageHeader:
    """Message header class. Contains message type and body length."""

    def __init__(self, message_type: MessageTypes, body_len: int):
        self.message_type = message_type
        self.body_len = body_len

    def to_bytes(self):
        return json.dumps({"message_type": self.message_type.to_json(), "body_len": self.body_len}).encode()

    @classmethod
    def from_bytes(cls, data):
        print(json.loads(data.decode()))
        json_data = json.loads(data.decode())
        return cls(MessageTypes(json_data["message_type"]), json_data["body_len"])

    def __str__(self):
        return f"{self.message_type=} \n {self.body_len=}"


class Message:
    """Message class. Contains header and body. Body is a dict."""

    def __init__(self, message_type: MessageTypes, body: dict = None):
        len_body = len(json.dumps(body)) if body else 0
        self.header = MessageHeader(message_type, len_body)
        self.body = body or {}

    def to_bytes(self):
        header_bytes = self.header.to_bytes()
        header_len_bytes = len(header_bytes).to_bytes(4, byteorder='big')
        body_bytes = json.dumps(self.body).encode()
        return header_len_bytes + header_bytes + body_bytes

    @classmethod
    def from_bytes(cls, data):
        header_len = int.from_bytes(data[:4], byteorder='big')
        header = MessageHeader.from_bytes(data[4:4 + header_len])
        body = json.loads(data[4 + header_len:].decode())
        return cls(header.message_type, body)

    def __str__(self):
        return f"{self.header.__str__()=} \n {self.body=}"
