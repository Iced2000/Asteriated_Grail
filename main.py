# main.py

import argparse
from game_engine.AgrGameEngine import AgrGameEngine
from server.game_server import GameServer
from client.game_client import GameClient

def main():
    parser = argparse.ArgumentParser(description="AGR Game")
    parser.add_argument("--mode", choices=["local", "server", "client"], default="local", help="Game mode")
    parser.add_argument("--host", default="localhost", help="Server host (for client mode)")
    parser.add_argument("--port", type=int, default=5000, help="Server port (for server and client mode)")
    parser.add_argument("--num_players", type=int, default=4, help="Number of players (for server mode)")
    args = parser.parse_args()

    if args.mode == "local":
        config = {
            'num_players': 4,
            'red_players': [1,3],
            'blue_players': [2,4],
            'deck_path': "cardDB.txt",
            'networked': False,
            'debug': True
        }
        game_engine = AgrGameEngine(config)
        game_engine.start_game()
    elif args.mode == "server":
        server = GameServer(args.host, args.port, args.num_players)
        server.start()
    elif args.mode == "client":
        client = GameClient(args.host, args.port)
        client.connect()

if __name__ == "__main__":
    main()