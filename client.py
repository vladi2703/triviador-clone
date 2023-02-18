"""A client that connects to a server and sends messages to it"""
import asyncio
import socket
import threading
from asyncio import sleep

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

        self.name: int = -1

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
            self.name = message.body["name"]
        elif message.header.message_type == MessageTypes.BOARD:
            print("Board received from server")
            self._board = Board.deserialize(message.body["board"]) if message.body["board"] is not None else None
            if self._board is not None:
                self._display_board = BoardDisplay(self._board, self.name)
                print('here')
                self._display_board.mainloop()
                try:
                    # Wait for a response with the specified timeout
                    response = await asyncio.wait_for(self._display_board.get_move(), 5)
                    if response is not None:
                        move = response
                    else:
                        move = None
                except asyncio.TimeoutError:
                    # Return None if the response is not received within the timeout
                    move = None
                if move is not None:
                    message = Message(message_type=MessageTypes.MOVE_PLAYER, body={"move": move.to_dict()})
                    self.sock.sendall(message.to_bytes())
                    await sleep(0.2)
                request_board = Message(message_type=MessageTypes.REQUEST_BOARD)
                self.sock.sendall(request_board.to_bytes())
                return None
        elif message.header.message_type == MessageTypes.REQUEST_MOVE_PLAYER:
            print("Requesting move player")

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
