# import os

# from gameutils.database import PlayerDatabase
# from messagingutils.messaging import Message, MessageTypes
# from gameutils.question import Question
# from gameutils.playboard import Board, Player
# from gameutils.game import Game


# def test_process_client_message():
#     # Arrange
#     message_question = Message(MessageTypes.GET_QUESTION)
#     message_answer_false = Message(MessageTypes.ANSWER, {"answer": "incorrect_answer"})
#     message_answer_true = Message(MessageTypes.ANSWER, {"answer": "correct_answer"})

#     message_active_status = Message(MessageTypes.ACTIVE_STATUS)
#     message_request_board = Message(MessageTypes.REQUEST_BOARD)
#     message_disconnect = Message(MessageTypes.DISCONNECT)
#     game = Game()
#     question = Question(
#         "category",
#         "type",
#         "difficulty",
#         "question",
#         "correct_answer",
#         ["incorrect_answers"],
#     )
#     game.currentQuestion = question
#     players = (Player(1, "red"), Player(2, "blue"), Player(3, "green"))
#     board = Board(players=players)
#     if os.path.exists("../resources/players.txt"):
#         os.remove("../resources/players.txt")
#     game.player_database = PlayerDatabase("../resources/players.txt")
#     for i in range(3):
#         game.player_database.add_player(i + 1)

#     # Act
#     message_answer_response_incorrect = game.process_client_message(
#         message_answer_false, game.player_database, 1, board
#     )
#     message_answer_response_correct = game.process_client_message(
#         message_answer_true, game.player_database, 1, board
#     )
#     message_active_status_response = game.process_client_message(
#         message_active_status, game.player_database, 1, board
#     )
#     message_request_board_response = game.process_client_message(
#         message_request_board, game.player_database, 1, board
#     )
#     message_disconnect_response = game.process_client_message(
#         message_disconnect, game.player_database, 1, board
#     )
#     message_question_response = game.process_client_message(
#         message_question, game.player_database, 1, board
#     )

#     # Assert
#     assert message_question_response.header.message_type == MessageTypes.QUESTION
#     assert (
#         message_answer_response_incorrect.header.message_type
#         == MessageTypes.INCORRECT_ANSWER
#     )
#     assert (
#         message_answer_response_incorrect.body["correct_answer"]
#         == question.correct_answer
#     )
#     assert (
#         message_answer_response_correct.header.message_type
#         == MessageTypes.CORRECT_ANSWER
#     )
#     assert (
#         message_active_status_response.header.message_type == MessageTypes.ACTIVE_STATUS
#     )
#     assert message_request_board_response.header.message_type == MessageTypes.BOARD
#     assert message_request_board_response.body["board"] == board.serialize()
#     assert message_disconnect_response is None
