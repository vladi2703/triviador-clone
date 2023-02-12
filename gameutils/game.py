"""Game logic for the client and server."""

from gameutils.database import PlayerDatabase
from gameutils.playboard import Board
from messagingutils.messaging import Message, MessageTypes
from gameutils.question import Question


class Game:
    def __init__(self):
        self.player_database = PlayerDatabase('resources/players.txt')
        self.currentQuestion = Question.get_one_question(difficulty="easy")

    def process_client_message(self, message: Message, player_database: PlayerDatabase, player_name, board: Board) \
            -> Message | None:
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
        elif message.header.message_type == MessageTypes.REQUEST_BOARD:
            if board is not None:
                return Message(MessageTypes.BOARD, {"board": board.serialize()})
            else:
                return Message(MessageTypes.BOARD, {"board": None})
        elif message.header.message_type == MessageTypes.DISCONNECT:
            return None
        else:
            raise ValueError(f"Unknown message type: {message.header.message_type}")
