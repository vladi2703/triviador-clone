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
        return cls(**json.loads(data.decode()))

    def __str__(self):
        return f"{self.message_type=} \n {self.body_len=}"


class MessageBody:
    def __init__(self, body: dict):
        self.body = body

    def to_bytes(self):
        return json.dumps(self.body).encode()

    @classmethod
    def from_bytes(cls, data):
        return cls(**json.loads(data.decode()))

    def __str__(self):
        return f"{self.body=}"


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


# TODO: Use this for testing
if __name__ == '__main__':
    # mes = Message(MessageTypes.DISCONNECT, {"test": "test", "pesho": "pesho"})
    # mes_bytes = mes.to_bytes()
    # from_bytes = Message.from_bytes(mes_bytes)
    # print(mes_bytes)
    # print(from_bytes)

    from gameutils.question import Question
    question = Question.get_one_question(difficulty="easy")
    mes = Message(MessageTypes.QUESTION, {"question_data": question.to_json_for_client()})
    mes_bytes = mes.to_bytes()
    from_bytes = Message.from_bytes(mes_bytes)
    print(mes_bytes)
    print(from_bytes)
    quest_new = Question.from_json_for_client(from_bytes.body["question_data"])
    print(quest_new)
