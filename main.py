# main.py

from game_engine.AgrGameEngine import AgrGameEngine

def main():
    # Configuration for the game
    config = {
        'num_players': 4,           # Total number of players
        'red_players': [1,3],         # Player IDs in the Red Team
        'blue_players': [2,4],        # Player IDs in the Blue Team
        'deck_path': "cardDB.txt",  # Path to the single shared deck
    }

    # Initialize and start the game engine
    game_engine = AgrGameEngine(config)
    game_engine.start_game()

if __name__ == "__main__":
    main()