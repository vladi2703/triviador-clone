"""A class representing the game board"""

import tkinter as tk
from itertools import cycle
from typing import NamedTuple, Tuple, List


class Player(NamedTuple):
    name: int
    color: str


class Turn(NamedTuple):
    row: int
    col: int
    color: str = "white"


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

    # TODO: Implement the of cases, when attaking for example

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


class BoardDisplay(tk.Tk):
    def __init__(self, board: Board):
        super().__init__()
        self.title("Epic battle arena")
        self.board = board
        self._cities = {}
        self._setup_display()
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
                cell = tk.Button(master=self.board_frame, text=" ", bg='white', width=10, height=8)
                self._cities[cell] = (row, col)  # store the cell position in a dictionary
                cell.grid(row=row, column=col, sticky="nsew")
                cell.bind("<Button-1>", self._play_turn)

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


if __name__ == "__main__":
    board = Board(players=(Player(1, "red"), Player(2, "blue"), Player(3, "green")))
    display = BoardDisplay(board)
    display.mainloop()
