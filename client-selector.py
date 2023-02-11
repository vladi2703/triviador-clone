import socket
import selectors

from messagingutils.messaging import Message, MessageTypes
from gameutils.game import Game


class Client:
    def __init__(self, client_host: str, client_port: int, game: Game):
        self.host = client_host
        self.port = client_port
        self.sel = selectors.DefaultSelector()
        self.sock = None  # will be initialized in start connection
        self.start_connection()
        self.game = game

    def start_connection(self):
        addr = (self.host, self.port)
        print(f"Starting connection to {addr}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(addr)  # just connect will raise an exception if the connection fails
        # TODO: Handle the exception
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = Message(MessageTypes.GET_QUESTION, None)

        self.sel.register(self.sock, events, data=message)

    def read(self, message, sock):
        received_data = sock.recv(1024)  # TODO: Fix hard-coded buffer size
        if received_data:
            received_message = message.from_bytes(received_data)
            self.sel.modify(sock, selectors.EVENT_WRITE, send_message)
            print(f"Received {received_message} from server")
            response = self.game.process_server_message(received_message)
            if response is not None:
                self.write(sock, response)
            else:
                print("Closing connection")
                self.sel.unregister(sock)
                sock.close()
        if not received_data:
            print("Closing connection")
            self.sel.unregister(sock)  # Stop monitoring the socket
            sock.close()

    def write(self, sock, message: Message):
        if message is not None:
            sent_bytes = sock.send(send_buffer)
            send_buffer = message.to_bytes()

        if send_buffer:
            print(f"Sending {send_buffer} to server")
            send_buffer = send_buffer[sent_bytes:]

        # Register the socket for reading
        self.sel.modify(conn, selectors.EVENT_READ, self.process_server_message)

    def service_connection(self, key, mask):
        sock = key.fileobj
        message = key.data
        if mask & selectors.EVENT_READ:
            self.read(message, sock)
        if mask & selectors.EVENT_WRITE:
            self.write(sock)

    def run(self):
        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    self.service_connection(key, mask)
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()



if __name__ == "__main__":
    host, port = '127.0.0.1', 65432

    client = Client(host, port, Game())
    client.run()
