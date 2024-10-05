# server/game_server.py

import socket
import json
import threading
from game_engine.engine import GameEngine

class GameServer:
    def __init__(self, host, port, num_players):
        self.host = host
        self.port = port
        self.num_players = num_players
        self.game_engine = None
        self.clients = []
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.num_players)
        print(f"Server started on {self.host}:{self.port}")

        while len(self.clients) < self.num_players:
            client_socket, addr = self.server_socket.accept()
            print(f"New connection from {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

        self.start_game()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.process_client_message(client_socket, json.loads(data))
            except Exception as e:
                print(f"Error handling client: {e}")
                break
        client_socket.close()

    def process_client_message(self, client_socket, message):
        if message['type'] == 'action_selection':
            # Handle action selection
            pass
        elif message['type'] == 'yes_no_prompt':
            # Handle yes/no prompt
            pass
        # ... (handle other message types)

    def start_game(self):
        config = {
            'num_players': self.num_players,
            'red_players': [1, 3],
            'blue_players': [2, 4],
            'deck_path': "cardDB.txt",
            'networked': True,
            'game_server': self
        }
        self.game_engine = AgrGameEngine(config)
        self.game_engine.start_game()

    def broadcast(self, message):
        for client in self.clients:
            client.send(json.dumps(message).encode('utf-8'))

    def send_to_player(self, player_id, message):
        self.clients[player_id - 1].send(json.dumps(message).encode('utf-8'))

    def wait_for_response(self, player_id):
        # Implement logic to wait for a response from a specific player
        pass
