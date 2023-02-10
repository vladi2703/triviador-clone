"""A client that connects to a server and sends messages to it"""
import socket
import threading


from messaging import Message
from game import Game


class Client:
    """A client that connects to a server and sends messages to it"""
    def __init__(self, client_host: str, client_port: int, game: Game):
        self.host = client_host
        self.port = client_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (self.host, self.port)
        self.sock.connect(addr)

        self.input_thread = None
        self.response_thread = None

        self.game = game
        self.still_running = False

    def receive_message(self):
        """Receive a message from the server and process it"""
        while self.still_running:
            data = self.sock.recv(1024)
            if data:
                message = Message.from_bytes(data)
                print(f"Received {message} from server")
                response = self.game.process_server_message(message)
                if response is not None:
                    self.sock.sendall(response)
                else:
                    print("Closing connection")
                    self.sock.close()
                    break
            if not data:
                print("Closing connection")
                self.sock.close()
                break
    def repl(self):
        """Read-eval-print loop"""
        print("Welcome!")
        while self.still_running:
            command = input("> ")
            command = command.lower()
            if command == "exit":
                print("Goodbye!")
                self.still_running = False
                self.sock.close()
                break

    def run(self):
        """Start the client"""
        self.still_running = True
        self.input_thread = threading.Thread(target=self.repl)
        self.input_thread.start()

        self.response_thread = threading.Thread(target=self.receive_message)
        self.response_thread.start()

if __name__ == "__main__":
    host, port = '127.0.0.1', 65432

    client = Client(host, port, Game())
    client.run()
