"""A client that connects to a server and sends messages to it"""
import asyncio
import socket
import threading

from gameutils.question import Question
from messagingutils.messaging import Message, MessageTypes
from gameutils.playboard import QuestionDisplay, Board, BoardDisplay


class Client:
    """A client that connects to a server and sends messages to it"""

    def __init__(self, client_host: str, client_port: int):
        self.host = client_host
        self.port = client_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (self.host, self.port)
        self.sock.connect(addr)

        self.input_thread = None
        self.response_thread = None

        self.still_running = False

        self._board: Board | None = None
        self._display_board: BoardDisplay | None = None

    async def _process_server_message(self, message: Message):
        """Process a message from the server."""
        if message.header.message_type == MessageTypes.QUESTION:
            print("Question received from server")
            question = Question.from_json_for_client(message.body["question_data"])
            display_question = QuestionDisplay(question)
            answer = await display_question.prompt_question()
            print(answer)
            return Message(MessageTypes.ANSWER, {"answer": answer}).to_bytes()
        elif message.header.message_type == MessageTypes.CORRECT_ANSWER:
            print("Correct answer!")
        elif message.header.message_type == MessageTypes.INCORRECT_ANSWER:
            print("Unfortunately, your answer is incorrect. \
                    Correct answer is: " + message.body["correct_answer"])
        elif message.header.message_type == MessageTypes.ACTIVE_STATUS:
            print("You've been acknowledged as active by the server.")
        elif message.header.message_type == MessageTypes.BOARD:
            print("Board received from server")
            self._board = Board.deserialize(message.body["board"]) if message.body["board"] is not None else None
            if self._board is not None:
                if self._display_board is None:
                    self._display_board = BoardDisplay(self._board)
                else:
                    self._display_board.update_board(self._board)
                self._display_board.mainloop()

    async def receive_message(self):
        """Receive a message from the server and process it"""
        while self.still_running:
            print("Waiting for message from server")
            try:
                data = self.sock.recv(1024)
            except ConnectionResetError:
                print("Connection was reset by the server")
                self.still_running = False
                break
            if data:
                print(f"Received {data} from server")
                message = Message.from_bytes(data)
                print(f"Received {message} from server")
                response = await self._process_server_message(message)
                if response is not None:
                    self.sock.sendall(response)
            if not data:
                print("Closing connection")
                self.sock.close()
                self.still_running = False
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
            elif command == "question":
                message = Message(message_type=MessageTypes.GET_QUESTION)
                self.sock.sendall(message.to_bytes())
            elif command == "board":
                message = Message(message_type=MessageTypes.REQUEST_BOARD)
                self.sock.sendall(message.to_bytes())
            else:
                print("Unknown command")

    def _receive_message_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.receive_message())

    def run(self):
        """Start the client"""
        self.still_running = True
        self.input_thread = threading.Thread(target=self.repl)
        self.input_thread.start()

        self.response_thread = threading.Thread(target=self._receive_message_thread)
        self.response_thread.run()


if __name__ == "__main__":
    host, port = '127.0.0.1', 65432

    client = Client(host, port)
    client.run()
