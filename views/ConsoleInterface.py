# views/ConsoleInterface.py

class ConsoleInterface:
    def prompt_action_selection(self, actions):
        if not actions:
            print("\nNo available actions to select.")
            return None

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