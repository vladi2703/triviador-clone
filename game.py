"""Game logic for the client and server."""

from database import PlayerDatabase
from messaging import Message, MessageTypes
from question import Question


class Game:
    def __init__(self):
        self.player_database = PlayerDatabase('players.txt')
        self.currentQuestion = Question.get_one_question(difficulty="easy")

    def process_client_message(self, message: Message, player_database: PlayerDatabase) -> Message | None:
        """Process a message from a client and return a message to be sent back to the client. When client
        disconnects, return None. """

        if message.header.message_type == MessageTypes.GET_QUESTION.value:
            self.currentQuestion = Question.get_one_question(difficulty="easy")
            return Message(MessageTypes.QUESTION, {"question_data": self.currentQuestion.to_json_for_client()})
        elif message.header.message_type == MessageTypes.ANSWER.value:
            if message.body["answer"] == self.currentQuestion.correct_answer:
                player_database.add_points(message.body["player_name"], 1)
                return Message(MessageTypes.CORRECT_ANSWER)
            else:
                return Message(MessageTypes.INCORRECT_ANSWER, {"correct_answer": self.currentQuestion.correct_answer})
        elif message.header.message_type == MessageTypes.ACTIVE_STATUS:
            return Message(MessageTypes.ACTIVE_STATUS)
        elif message.header.message_type == MessageTypes.DISCONNECT.value:
            return None
        else:
            raise ValueError(f"Unknown message type: {message.header.message_type}")

    @staticmethod
    def process_server_message(message: Message):
        """Process a message from the server."""
        if message.header.message_type == MessageTypes.QUESTION.value:
            print("Question received from server")
            question = Question.from_json_for_client(message.body["question_data"])
            print(question)
        elif message.header.message_type == MessageTypes.CORRECT_ANSWER.value:
            print("Correct answer!")
        elif message.header.message_type == MessageTypes.INCORRECT_ANSWER.value:
            print("Unfortunately, your answer is incorrect. \
                Correct answer is: " + message.body["correct_answer"])
        elif message.header.message_type == MessageTypes.ACTIVE_STATUS.value:
            print("You've been acknowledged as active by the server.")
        