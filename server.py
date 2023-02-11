import socket
import selectors

from gameutils.database import PlayerDatabase
from messagingutils.messaging import Message, MessageTypes
from gameutils.game import Game
from messagingutils.messageq import MessageQueue


class Server:
    def __init__(self, host: str, port: int, game: Game):
        if port < 1024:
            raise ValueError("Port must be greater than 1024")

        self.host = host
        self.port = port
        self.game = game
        self.sel = selectors.DefaultSelector()
        self.__output_buf = b''
        self.player_database = PlayerDatabase('players.txt')
        self.message_queue_dict: dict[int, MessageQueue] = {}

    def start(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse the same address
        lsock.bind((self.host, self.port))
        lsock.listen()
        print(f"Listening on {(self.host, self.port)}")
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)  # Register the socket to be monitored for read events

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()
        _, pesho = addr
        if not self.player_database.add_player(pesho):  # player name is the address
            pass  # TODO: Send message to client that the name is already taken
            # sock.close()
            # return
        print(f"Accepted connection from {addr}")
        self.message_queue_dict[sock.getsockname()[1]] = MessageQueue()
        conn.setblocking(False)
        message = Message(MessageTypes.ACTIVE_STATUS, None)
        # Register the socket to be monitored for read events
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=message)

    def read(self, message, sock):
        received_data = sock.recv(1024)  # TODO: Fix hard-coded buffer size
        if received_data:
            message = message.from_bytes(received_data)
            response = self.game.process_client_message(message, self.player_database)
            if response is not None:
                self.message_queue_dict[sock.getsockname()[1]].add_message(response)
            else:
                print("Closing connection")
                self.sel.unregister(sock)
                sock.close()
        else:
            print("Closing connection")
            self.sel.unregister(sock)
            sock.close()

    def service_connection(self, key, mask):
        sock = key.fileobj
        message = key.data
        if mask & selectors.EVENT_READ:
            self.read(message, sock)
        if mask & selectors.EVENT_WRITE:
            if self.message_queue_dict[sock.getsockname()[1]]:
                response = self.message_queue_dict[sock.getsockname()[1]].get_top_message()
                sock.send(response.to_bytes())
