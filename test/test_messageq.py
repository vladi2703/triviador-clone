from messagingutils.messageq import MessageQueue
from messagingutils.messaging import Message, MessageTypes


def test_add_message():
    # Arrange
    message_queue = MessageQueue()
    # Act
    message = Message(MessageTypes.ACTIVE_STATUS, None)
    message_queue.add_message(message)
    # Assert
    assert message_queue
    assert message_queue.queue[0] == message


def test_get_top_message():
    # Arrange
    message_queue = MessageQueue()
    message1 = Message(MessageTypes.ACTIVE_STATUS, None)
    message2 = Message(MessageTypes.GET_QUESTION, None)
    message_queue.add_message(message1)
    message_queue.add_message(message2)
    # Act
    top_message1 = message_queue.get_top_message()
    top_message2 = message_queue.get_top_message()
    # Assert
    assert top_message1 == message1
    assert top_message2 == message2
    assert not message_queue
