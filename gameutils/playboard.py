"""A class representing the game board"""
import json
import pickle
import threading
import tkinter as tk
from functools import partial
from itertools import cycle
from typing import NamedTuple, Tuple, List
from gameutils.question import Question


class Player(NamedTuple):
    name: int
    color: str

    def to_dict(self):
        return {"name": self.name, "color": self.color}

    @classmethod
    def from_dict(cls, data):
        return Player(data["name"], data["color"])


class Turn(NamedTuple):
    row: int
    col: int
    color: str = "white"

    def to_dict(self):
        return {"row": self.row, "col": self.col, "color": self.color}

    @classmethod
    def from_dict(cls, data):
        return Turn(data["row"], data["col"], data["color"])


DEFAULT_BOARD_SIZE = 3


class Board:
    def __init__(self, board_size=DEFAULT_BOARD_SIZE, players=None):
        self.board_size = board_size
        self.board: List[List[Turn]] = []  # 2D array of turns
        self.players: Tuple[Player, Player, Player] = players
        self.players_cycle = cycle(self.players)  # to iterate over players in turns
        self.current_player = next(self.players_cycle)
        self._current_turns = []
        self._has_winner = False
        self._setup_board()

    def _setup_board(self):
        self.board = [[Turn(row, col) for col in range(self.board_size)] for row in
                      range(self.board_size)]  # 2D array of turns

    @property
    def has_winner(self):
        return self._has_winner

    def next_turn(self):
        """Switch to the next player"""
        self.current_player = next(self.players_cycle)

    def is_valid_move(self, move):
        """Check if the move is valid"""
        return self.board[move.row][move.col].color == "white"

    # TODO: Implement the of cases, when attacking for example

    def process_turn(self, turn: Turn):
        """Process a turn"""
        print(f"Processing turn: {turn.row}, {turn.col}, {turn.color}")
        self.board[turn.row][turn.col] = turn
        self._current_turns.append(turn)
        self._has_winner = self._check_winner(turn)
        self.next_turn()

    def _check_winner(self, turn: Turn):
        """Check if the current player has won.
         Player wins if he has all the cells of the board filled with his color"""
        for row in self.board:
            if not all(turn.color == cell.color for cell in row):
                return False
        return True

    def serialize(self) -> str:
        """Serialize the board"""
        board = [[cell.to_dict() for cell in row] for row in self.board]
        players = [player.to_dict() for player in self.players]
        return json.dumps({
            'board_size': self.board_size,
            'board': board,
            'players': players,
            'current_player': self.current_player.to_dict(),
            'current_turns': [turn.to_dict() for turn in self._current_turns],
            'has_winner': self._has_winner
        })

    @classmethod
    def deserialize(cls, json_string: str):
        """Deserialize the board"""
        data = json.loads(json_string)
        board_size = data['board_size']
        players = [Player(**player) for player in data['players']]
        new_board = cls(board_size, players)
        new_board.board = [[Turn(**cell) for cell in row] for row in data['board']]
        new_board.current_player = Player(**data['current_player'])
        new_board._current_turns = [Turn(**turn) for turn in data['current_turns']]
        new_board._has_winner = data['has_winner']
        return new_board


class BoardDisplay(tk.Tk):
    def __init__(self, board: Board):
        super().__init__()
        self.title("Epic battle arena")
        self.board = board
        self._cities = {}
        self._setup_display()
        self._widgets: List[List[tk.Button | None]] = [[None for _ in range(self.board.board_size)]
                                                       for _ in range(self.board.board_size)]
        self._create_widgets()

    def _setup_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(master=display_frame, text="Welcome to the game!")
        self.display.pack()

    def _create_widgets(self):
        self.board_frame = tk.Frame(master=self)
        self.board_frame.pack()
        for row in range(self.board.board_size):
            self.rowconfigure(row, weight=1, minsize=75)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self.board.board_size):
                self._widgets[row][col] = tk.Button(master=self.board_frame, text=" ", bg='white', width=10, height=8)
                self._cities[self._widgets[row][col]] = (row, col)  # store the cell position in a dictionary
                self._widgets[row][col].grid(row=row, column=col, sticky="nsew")
                self._widgets[row][col].bind("<Button-1>", partial(self._play_turn))

    def _play_turn(self, event):
        """Play a turn"""
        clicked_cell = event.widget
        row, col = self._cities[clicked_cell]
        turn = Turn(row, col, self.board.current_player.color)
        if self.board.is_valid_move(turn):
            self.board.process_turn(turn)
            clicked_cell.config(bg=self.board.current_player.color)
            self.display.config(text=f"{self.board.current_player.name} turn")
            if self.board.has_winner:
                self.display.config(text=f"{self.board.current_player.name} won!")
            else:
                self.board.next_turn()
                self.display.config(text=f"{self.board.current_player.name} turn")

    def update_board(self, board: Board):
        """Update the board"""
        self.board = board
        for row in range(self.board.board_size):
            for col in range(self.board.board_size):
                self._widgets[row][col].config(bg=self.board.board[row][col].color)


class QuestionDisplay:
    """A class representing the question display"""

    def __init__(self, question_to_display: Question, time_for_answer=10):
        self.question = question_to_display
        self.root = tk.Tk()
        self.root.title("Question")
        self.root.geometry("600x600")
        self.question_label = tk.Label(self.root, text=self.question.question,
                                       font=("Arial", 20), wraplength=500, justify=tk.CENTER)
        self.question_label.pack(pady=20)

        self._buttons = []
        # add buttons for possible answers
        for i, answer in enumerate(self.question.possible_answers):
            self._buttons.append(
                tk.Button(self.root, text=answer, font=("Arial", 15),
                          command=partial(self._check_answer, answer))
            )
            self._buttons[i].pack(pady=10)

        self._answer: str = ""
        self._answer_event = threading.Event()
        self._time_for_answer = time_for_answer

    def _check_answer(self, answer):
        """Return answer to client. Give feedback to user. Wait 2-3 seconds and then close window."""
        if self._answer != "":
            return
        label = tk.Label(self.root, text=f"answer given: {answer}",
                         font=("Arial", 15), wraplength=500, justify=tk.CENTER)
        label.pack()
        self._answer = answer
        self.root.update()
        self._answer_event.set()
        # Todo: send message to server. Give feedback to user. Wait 2-3 seconds and then close window.

    async def close_app_timer(self):
        """Close the app after a given time"""
        self._answer_event.wait(4)
        self.root.destroy()

    async def prompt_question(self) -> str or None:
        """Prompt the question to the user and return the answer. If no answer is given, return None"""
        # TODO: ANSWER comes only when the user closes the window. Implement a timer to close the window

        self.root.mainloop()
        # self.root.after(1000, self.root.destroy)
        self._answer_event.wait(self._time_for_answer)
        self.root.update()
        if self._answer == "":
            return None
        else:
            return self._answer


if __name__ == "__main__":
    board_1 = Board(players=(Player(1, "red"), Player(2, "blue"), Player(3, "green")))
    ser = board_1.serialize()
    board = Board.deserialize(ser)
    display = BoardDisplay(board)
    display.mainloop()
    # question = Question.get_one_question(difficulty='easy')
    # display = QuestionDisplay(question)
    # display.prompt_question()
