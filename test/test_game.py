from messagingutils.messaging import Message, MessageTypes


def test_process_client_message():
    # Arrange
    message = Message(MessageTypes.GET_QUESTION, None)
    # Act


def test_process_server_message():
    assert False
