# main.py

import argparse
from game_engine import GameEngine
from server import GameServer
from client import GameClient

def main():
    parser = argparse.ArgumentParser(description="AGR Game")
    parser.add_argument("--mode", choices=["local", "server", "client"], default="local", help="Game mode")
    parser.add_argument("--host", default="localhost", help="Server host (for client mode)")
    parser.add_argument("--port", type=int, default=5000, help="Server port (for server and client mode)")
    parser.add_argument("--num_players", type=int, default=4, help="Number of players (for server mode)")
    args = parser.parse_args()

    if args.mode == "local":
        config = {
            'player': [
                {'pid': 1, 'character_type': 'BasePlayer', 'team': 'red'},
                {'pid': 2, 'character_type': 'BasePlayer', 'team': 'blue'},
                {'pid': 3, 'character_type': 'BasePlayer', 'team': 'red'},
                {'pid': 4, 'character_type': 'BasePlayer', 'team': 'blue'},
            ],
            'deck_path': "assets/cardDB.txt",
            'networked': False,
            'debug': True
        }
        game_engine = GameEngine(config)
        game_engine.start_game()
    elif args.mode == "server":
        server = GameServer(args.host, args.port, args.num_players)
        server.start()
    elif args.mode == "client":
        client = GameClient(args.host, args.port)
        client.connect()

if __name__ == "__main__":
    main()