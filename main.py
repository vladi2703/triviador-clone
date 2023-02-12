import os

from server import Server
from gameutils.game import Game

if __name__ == "__main__":
    os.remove("resources/players.txt")
    HOST = '127.0.0.1'
    PORT = 65432
    game = Game()

    server = Server(HOST, PORT, game)
    server.start()

