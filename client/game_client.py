# client/game_client.py

import socket
import json
import threading

class GameClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.player_id = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.process_server_message(json.loads(data))
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        self.socket.close()

    def process_server_message(self, message):
        # Process messages from the server and update local game state
        pass

    def send_message(self, message):
        self.socket.send(json.dumps(message).encode('utf-8'))
