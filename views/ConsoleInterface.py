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

    def prompt_defender_action(self, defender, attacker, has_counter=False):
        print(f"\nPlayer {defender.id} is being attacked by Player {attacker.id}.")
        defender.show_hand()
        print("Choose an action:")
        if has_counter:
            print("1: Counterattack")
        print("2: Take Damage")
        while True:
            choice = input("Select an action number: ").strip()
            if has_counter and choice == '1':
                return 'counterattack'
            elif choice == '2':
                return 'take_damage'
            else:
                print("Invalid selection. Please select a valid action.")

    def __str__(self):
        return "Console Interface"