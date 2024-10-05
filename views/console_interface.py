# views/console_interface.py
from abc import ABC, abstractmethod

class ConsoleInterface(ABC):
    def __init__(self, debug=False):
        self.debug = debug

    @abstractmethod
    def send_message(self, message, player_id=None, broadcast=False, debug=False):
        pass

    @abstractmethod
    def prompt_action_selection(self, actions, player_id=None):
        pass

    @abstractmethod
    def prompt_yes_no(self, message, player_id=None):
        pass

    @abstractmethod
    def prompt_multiple_action_selection(self, actions, num_selections, player_id=None):
        pass

class LocalConsoleInterface(ConsoleInterface):
    def __init__(self, debug=False):
        super().__init__(debug)

    def send_message(self, message, player_id=None, broadcast=False, debug=False):
        if not self.debug and debug:
            return
        if player_id is not None:
            print(f"Player {player_id}: {message}")
        elif broadcast:
            print(message)
        elif debug:
            print(message)
        else:
            raise ValueError("No player ID or broadcast flag provided.")

    def prompt_action_selection(self, actions, player_id):
        if not actions:
            raise ValueError("No available actions to select.")

        for idx, action in enumerate(actions):
            self.send_message(f"{idx}: {action}", player_id=player_id)
        while True:
            try:
                choice = int(input("Select an action number: "))
                if 0 <= choice < len(actions):
                    selected_action = actions[choice]
                    return selected_action
                else:
                    self.send_message("Invalid selection. Please select a valid action.", player_id=player_id)
            except ValueError:
                self.send_message("Invalid input. Please enter a number.", player_id=player_id)

    def prompt_yes_no(self, message, player_id=None):
        while True:
            choice = input(f"{message} [Y/N]: ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                self.send_message("Invalid input. Enter 'Y' or 'N'.", player_id=player_id)

    def prompt_multiple_action_selection(self, actions, min_selections, max_selections, player_id=None):
        if not actions:
            raise ValueError("No available actions to select.")
        if min_selections > max_selections:
            raise ValueError("Minimum selections cannot be greater than maximum selections.")
        if max_selections > len(actions):
            raise ValueError("Maximum selections cannot be greater than the number of available actions.")

        self.send_message(f"\nSelect between {min_selections} and {max_selections} action(s). Enter 'done' when finished:", player_id=player_id)
        for idx, action in enumerate(actions):
            self.send_message(f"{idx}: {action}", player_id=player_id)

        selected_actions = []
        while len(selected_actions) < max_selections:
            try:
                choice = input(f"Select action {len(selected_actions) + 1} (or 'done'): ")
                if choice.lower() == 'done':
                    if len(selected_actions) < min_selections:
                        self.send_message(f"You must select at least {min_selections} action(s).", player_id=player_id)
                    else:
                        break
                choice = int(choice)
                if 0 <= choice < len(actions):
                    selected_action = actions[choice]
                    if selected_action in selected_actions:
                        self.send_message("You've already selected this action. Please choose a different one.", player_id=player_id)
                    else:
                        selected_actions.append(selected_action)
                        self.send_message(f"You have selected: {selected_action}", player_id=player_id)
                        if len(selected_actions) == max_selections:
                            break
                else:
                    self.send_message("Invalid selection. Please select a valid action.", player_id=player_id)
            except ValueError:
                self.send_message("Invalid input. Please enter a number or 'done'.", player_id=player_id)

        return selected_actions

class NetworkedConsoleInterface(ConsoleInterface):
    def __init__(self, game_server, debug=False):
        super().__init__(debug)
        self.game_server = game_server

    def send_message(self, message, player_id=None, broadcast=False, debug=False):
        if broadcast:
            self.game_server.broadcast({"type": "message", "content": message, 'debug': debug})
        elif player_id is not None:
            self.game_server.send_to_player(player_id, {"type": "message", "content": message, 'debug': debug})
        else:
            raise ValueError("No player ID or broadcast flag provided.")

    def prompt_action_selection(self, actions, player_id):
        self.game_server.send_to_player(player_id, {
            "type": "action_selection",
            "actions": [str(action) for action in actions]
        })
        response = self.game_server.wait_for_response(player_id)
        return actions[response['selected_action']]

    def prompt_yes_no(self, message, player_id):
        self.game_server.send_to_player(player_id, {
            "type": "yes_no_prompt",
            "message": message
        })
        response = self.game_server.wait_for_response(player_id)
        return response['choice']

    def prompt_multiple_action_selection(self, actions, num_selections, player_id):
        self.game_server.send_to_player(player_id, {
            "type": "multiple_action_selection",
            "actions": [str(action) for action in actions],
            "num_selections": num_selections
        })
        response = self.game_server.wait_for_response(player_id)
        return [actions[idx] for idx in response['selected_actions']]


    def prompt_action_selection(self, actions):
        if not actions:
            print("\nNo available actions to select.")
            raise ValueError("No available actions to select.")

        print("\nAvailable Actions:")
        for idx, action in enumerate(actions):
            print(f"{idx}: {action}")
        while True:
            try:
                choice = int(input("Select an action number: "))
                if 0 <= choice < len(actions):
                    selected_action = actions[choice]
                    print(f"You have selected: {selected_action}")
                    return selected_action
                else:
                    print("Invalid selection. Please select a valid action.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def prompt_target_selection(self, targets):
        if not targets:
            print("\nNo available targets.")
            return None

        print("\nAvailable Targets:")
        for idx, target in enumerate(targets):
            print(f"{idx}: Player {target.id}")
        while True:
            try:
                choice = int(input("Select a target by number: "))
                if 0 <= choice < len(targets):
                    selected_target = targets[choice]
                    print(f"You have selected: Player {selected_target.id}")
                    return selected_target
                else:
                    print("Invalid selection. Please select a valid target.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def prompt_card_selection(self, cards):
        if not cards:
            print("\nNo available cards.")
            return None

        print("\nAvailable Cards:")
        for idx, card in enumerate(cards):
            print(f"{idx}: {card.name} ({card.element} {card.property})")
        while True:
            try:
                choice = int(input("Select a card by number: "))
                if 0 <= choice < len(cards):
                    selected_card = cards[choice]
                    print(f"You have selected: {selected_card.name}")
                    return selected_card
                else:
                    print("Invalid selection. Please select a valid card.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def prompt_yes_no(self, message):
        while True:
            choice = input(f"{message} [Y/N]: ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid input. Enter 'Y' or 'N'.")

    def prompt_defender_action(self, defender, attacker, valid_counter_actions):
        print(f"\nPlayer {defender.id} is being attacked by Player {attacker.id}.")
        defender.show_hand()
        print("\nAvailable Actions:")
        for idx, action in enumerate(valid_counter_actions):
            print(f"{idx}: {action}")
        while True:
            try:
                choice = int(input("Select an action number: "))
                if 0 <= choice < len(valid_counter_actions):
                    selected_action = valid_counter_actions[choice]
                    print(f"You have selected: {selected_action}")
                    return selected_action
                else:
                    print("Invalid selection. Please select a valid action.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def prompt_healing_amount(self, defender, healing_available):
        print(f"\nPlayer {defender.id} has {healing_available} healing available to use.")
        while True:
            try:
                choice = int(input("Enter the amount of healing to use: "))
                if 0 <= choice <= healing_available:
                    return choice
                else:
                    print("Invalid input. Please enter a valid amount of healing.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def __str__(self):
        return "Console Interface"