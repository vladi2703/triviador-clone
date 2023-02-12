from gameutils.playboard import Board, Player, Turn


# Testing player
def test_player_to_dict():
    # Arrange
    player = Player(1, "red")

    # Act
    player_dict = player.to_dict()

    # Assert
    assert player_dict == {"name": 1, "color": "red"}


def test_player_from_dict():
    # Arrange
    player_dict = {"name": 1, "color": "red"}

    # Act
    player = Player.from_dict(player_dict)

    # Assert
    assert player == Player(1, "red")


# Testing turn
def test_turn_to_dict():
    # Arrange
    turn = Turn(1, 2, "red")

    # Act
    turn_dict = turn.to_dict()

    # Assert
    assert turn_dict == {"row": 1, "col": 2, "color": "red"}


def test_turn_from_dict():
    # Arrange
    turn_dict = {"row": 1, "col": 2, "color": "red"}

    # Act
    turn = Turn.from_dict(turn_dict)

    # Assert
    assert turn == Turn(1, 2, "red")


# Testing the board
def test_board_process_turn():
    # Arrange

    players = (Player(1, "red"), Player(2, "blue"), Player(3, "green"))
    board = Board(players=players)

    turn = Turn(1, 2, "red")

    # Act
    board.process_turn(turn)

    # Assert
    assert board.board[1][2] == turn


def test_board_serialize():
    # Arrange
    players = (Player(1, "red"), Player(2, "blue"), Player(3, "green"))
    board = Board(players=players)
    board.board[1][2] = Turn(1, 2, "red")

    # Act
    board_dict = board.serialize()
    board_deserialized = Board.deserialize(board_dict)

    # Assert
    assert board_deserialized.board == board.board
    assert board_deserialized.players == board.players
    assert board_deserialized.current_player == board.current_player

# We won't test the display classes, as they are only used for the GUI and are just using tkinter
