"""Game logic for the client and server."""

from gameutils.database import PlayerDatabase
from messagingutils.messaging import Message, MessageTypes
from gameutils.question import Question


class Game:
    def __init__(self):
        self.player_database = PlayerDatabase('resources/players.txt')
        self.currentQuestion = Question.get_one_question(difficulty="easy")

    def process_client_message(self, message: Message, player_database: PlayerDatabase, player_name) -> Message | None:
        """Process a message from a client and return a message to be sent back to the client. When client
        disconnects, return None. """

        if message.header.message_type == MessageTypes.GET_QUESTION:
            self.currentQuestion = Question.get_one_question(difficulty="easy")
            return Message(MessageTypes.QUESTION, {"question_data": self.currentQuestion.to_json_for_client()})
        elif message.header.message_type == MessageTypes.ANSWER:
            if message.body["answer"] == self.currentQuestion.correct_answer:
                player_database.add_points(player_name, 1)
                return Message(MessageTypes.CORRECT_ANSWER)
            else:
                return Message(MessageTypes.INCORRECT_ANSWER, {"correct_answer": self.currentQuestion.correct_answer})
        elif message.header.message_type == MessageTypes.ACTIVE_STATUS:
            return Message(MessageTypes.ACTIVE_STATUS)
        elif message.header.message_type == MessageTypes.DISCONNECT:
            return None
        else:
            raise ValueError(f"Unknown message type: {message.header.message_type}")

    @staticmethod
    # TODO: Remove this if not used at the end
    def process_server_message(message: Message):
        """Process a message from the server."""
        if message.header.message_type == MessageTypes.QUESTION:
            print("Question received from server")
            question = Question.from_json_for_client(message.body["question_data"])
            print(question)
        elif message.header.message_type == MessageTypes.CORRECT_ANSWER:
            print("Correct answer!")
        elif message.header.message_type == MessageTypes.INCORRECT_ANSWER:
            print("Unfortunately, your answer is incorrect. \
                Correct answer is: " + message.body["correct_answer"])
        elif message.header.message_type == MessageTypes.ACTIVE_STATUS:
            print("You've been acknowledged as active by the server.")
        