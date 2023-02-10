import socket
import selectors
import threading

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        # Start the receive thread
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        # Start the send thread
        send_thread = threading.Thread(target=self.send)
        send_thread.start()

    def receive(self):
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, self.handle_read)

        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def handle_read(self, sock, mask):
        data = sock.recv(1024)
        if data:
            # Handle the incoming message
            print("Received:", data.decode())

    def send(self):
        while True:
            message = input("Enter your message: ")
            self.sock.sendall(message.encode())

if __name__ == "__main__":
    client = Client("localhost", 9000)
    client.start()
