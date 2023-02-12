from messagingutils.messaging import Message, MessageTypes, MessageHeader


# Test MessageTypes class
def test_to_json_types():
    """Test to_json method for MessageTypes."""
    assert MessageTypes.DISCONNECT.to_json() == MessageTypes.DISCONNECT.value
    assert MessageTypes.GET_QUESTION.to_json() == MessageTypes.GET_QUESTION.value
    assert MessageTypes.QUESTION.to_json() == MessageTypes.QUESTION.value
    assert MessageTypes.ANSWER.to_json() == MessageTypes.ANSWER.value
    assert MessageTypes.CORRECT_ANSWER.to_json() == MessageTypes.CORRECT_ANSWER.value
    assert MessageTypes.INCORRECT_ANSWER.to_json() == MessageTypes.INCORRECT_ANSWER.value
    assert MessageTypes.REQUEST_ACTIVE_STATUS.to_json() == MessageTypes.REQUEST_ACTIVE_STATUS.value
    assert MessageTypes.ACTIVE_STATUS.to_json() == MessageTypes.ACTIVE_STATUS.value
    assert MessageTypes.LOBBY_ALREADY_FULL.to_json() == MessageTypes.LOBBY_ALREADY_FULL.value


# Test MessageHeader class

def test_to_bytes_header():
    """Test to_bytes method for MessageHeader."""
    header = MessageHeader(MessageTypes.DISCONNECT, 0)
    assert header.to_bytes() == b'{"message_type": 0, "body_len": 0}'


def test_from_bytes_header():
    """Test from_bytes method for MessageHeader."""
    header = MessageHeader(MessageTypes.DISCONNECT, 0)
    from_bytes = MessageHeader.from_bytes(header.to_bytes())
    assert from_bytes.message_type == header.message_type
    assert from_bytes.body_len == header.body_len


# Test Message class

def test_to_and_from_bytes_message():
    """Test to_bytes method for Message."""
    message = Message(MessageTypes.DISCONNECT, {"test": "test"})
    from_bytes = Message.from_bytes(message.to_bytes())
    assert from_bytes.header.message_type == message.header.message_type
    assert from_bytes.header.body_len == message.header.body_len
    assert from_bytes.body == message.body


