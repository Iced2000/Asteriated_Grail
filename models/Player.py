# models/Player.py

from .Jewel import AgrJewel
from .Action import (
    AttackAction, MagicAction, SynthesisAction,
    PurchaseAction, RefineAction,
    AttackCardAction, MagicCardAction,
)
from .Effect import HealingEffect
class Player:
    def __init__(self, player_id, team, deck, interface):
        self.id = player_id
        self.team = team
        self.health = 0
        self.deck = deck
        self.interface = interface
        self.hand = []
        self.jewels = AgrJewel(maxJewel=3)  # Player's jewel capacity is 3
        self.max_hand_size = 6  # Define maximum hand size as per rules
        self.effects = {}  # Dictionary to hold active effects
        self.can_be_attacked = True
        self.action_points = {
            "general": 1,
            "attack": 0,
            "magic": 0,
            "special": 0
        }
        self.all_actions = [SynthesisAction(), PurchaseAction(), RefineAction()]
            

    def draw_initial_hand(self):
        self.hand = self.deck.deal(3)
        print(f"Player {self.id} drew initial hand: {[card.name for card in self.hand]}")


    def round_start(self):
        """
        Method to handle the start of a player's turn.
        This can include processing ongoing effects, resetting temporary states, etc.
        """
        print(f"\n=== Player {self.id}'s Round Start ===")
        self.process_effects_start_of_turn()

    def before_action(self):
        # Implement any before-action effects here
        print(f"Player {self.id} is preparing to take actions.")

    def perform_actions(self, game_engine):
        """
        Allows the player to perform multiple actions in their turn until they choose to stop
        or run out of available actions.
        """
        while True:
            self.show_hand()
            
            available_actions = self.get_available_actions()
            if not available_actions:
                print("No available actions to perform.")
                break

            # Debug Statement
            print(f"Debug: Available Actions = {available_actions} (Type: {type(available_actions)})")

            selected_action = self.interface.prompt_action_selection(available_actions)
            if not selected_action:
                print("No action selected. Returning to turn start.")
                continue
            
            success = selected_action.execute(self, game_engine)
            if success:
                selected_action.post_process(self)
            else:
                print("Action failed. Returning to turn start.")
                continue
            # Action points are deducted within execute_action if successful
            
            if not self.get_available_actions():
                print("No more available actions.")
                break

            continue_turn = self.interface.prompt_yes_no("Do you want to perform another action?")
            if not continue_turn:
                break

    def round_end(self):
        # Implement any round-end effects here
        print(f"Player {self.id}'s round is ending.")
        self.reset_actions()


    def process_effects_start_of_turn(self):
        # Process ongoing effects at the start of the player's turn
        for effect in list(self.effects.values()):
            if hasattr(effect, 'process_turn'):
                effect.process_turn(self)

    def apply_effect(self, effect):
        effect_name = type(effect).__name__
        self.effects[effect_name] = effect
        print(f"Player {self.id} received effect: {effect_name}.")

    def take_damage(self, amount, damage_type='attack'):
        print(f"Player {self.id} takes {amount} {damage_type} damage.")
        
        # Draw cards equal to the damage taken
        cards_drawn = self.deck.deal(amount)
        self.receive_cards(cards_drawn)
        
        # Handle exploding hand if hand size exceeds the limit
        self.handle_exploding_hand()

    def get_available_actions(self):
        """
        Determines which actions are currently available to the player.
        Returns a list of action names.
        """
        available_actions = []
        for action in self.all_actions:
            if action.available(self):
                available_actions.append(action)
        
        # Include card-based actions
        for card in self.hand:
            if card.is_attack():
                action = AttackCardAction(card)
            elif card.is_magic():
                action = MagicCardAction(card)
            else:
                continue

            if action.available(self):
                available_actions.append(action)

        return available_actions

    def reset_actions(self):
        self.action_points = {
            "general": 1,
            "attack": 0,
            "magic": 0,
            "special": 0
        }

    def can_draw_cards(self, number):
        return (len(self.hand) + number) <= self.max_hand_size

    def can_play_magic(self):
        # Check if player has any magic cards in hand
        return any(card.is_magic() for card in self.hand)

    def receive_cards(self, cards):
        self.hand.extend(cards)
        print(f"Player {self.id} received cards: {[card.name for card in cards]}")

    def handle_exploding_hand(self):
        if len(self.hand) > self.max_hand_size:
            excess_cards = len(self.hand) - self.max_hand_size
            print(f"Player {self.id} has exceeded the hand limit by {excess_cards} card(s). Must discard down to {self.max_hand_size} cards.")

            # Allow the player to discard excess cards
            for _ in range(excess_cards):
                while True:
                    print(f"Current Hand: {[card.name for card in self.hand]}")
                    try:
                        discard_choice = int(input("Select a card to discard by number: "))
                        if 0 <= discard_choice < len(self.hand):
                            discarded_card = self.hand.pop(discard_choice)
                            self.deck.recycle([discarded_card])
                            print(f"Discarded card: {discarded_card.name}")
                            # Deduct morale based on discarded cards
                            self.team.add_morale(-1)
                            break
                        else:
                            print("Invalid selection. Try again.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

            print(f"Player {self.id}'s hand size is now {len(self.hand)}.")

    def get_public_info(self):
        """
        Returns a string containing the player's public information without revealing the hand.
        Includes hand size.
        """
        return (f"Player {self.id}, Jewels: {self.jewels}, Hand Size: {len(self.hand)}, Effects: {list(self.effects.keys())}, Health: {self.health}")

    def show_hand(self):
        """
        Displays the player's current hand.
        """
        print(f"\n--- Player {self.id}'s Hand ---")
        for idx, card in enumerate(self.hand):
            print(f"{idx}: {card}")
        print("--------------------------\n")

    def get_valid_counter_cards(self, attack_card):
        """
        Returns a list of valid counter cards based on the attack card.
        """
        if attack_card.is_dark_extinction():
            return [card for card in self.hand if card.is_holy_light()]
        else:
            # Normal counter rules
            return [card for card in self.hand if (card.is_attack() and card.element == attack_card.element) or card.is_holy_light()]

    
    
    def respond_to_damage(self, damage):
        """
        Allows the player to respond to incoming damage with healing or other effects.
        
        :param damage: Incoming damage value.
        :return: Dictionary containing the amount of healing used.
        """
        # Placeholder: Automatically use available healing
        healing_available = self.get_available_healing()
        healing_to_use = min(healing_available, damage)
        if healing_to_use > 0:
            self.use_healing(healing_to_use)
        return {'healing': healing_to_use}

    def get_available_healing(self):
        """
        Returns the available healing points for the player.
        
        :return: Integer representing available healing.
        """
        # Example: Sum of healing effects
        return sum(effect.amount for effect in self.effects.values() if isinstance(effect, HealingEffect))

    def use_healing(self, amount):
        """
        Uses a specified amount of healing.
        
        :param amount: Amount of healing to use.
        """
        # Placeholder: Reduce available healing effects accordingly
        print(f"Player {self.id} uses {amount} healing.")
        # Implement actual healing consumption logic here

    def take_damage(self, amount, damage_type='attack'):
        """
        Applies damage to the player.
        
        :param amount: Amount of damage to apply.
        :param damage_type: Type of damage ('attack' or 'magic').
        """
        self.health -= amount
        print(f"Player {self.id} takes {amount} {damage_type} damage. Remaining health: {self.health}")


    def __str__(self):
        # Optional: Override to prevent displaying the hand when not needed
        return self.get_public_info()
    


# class Character(Player):
#     def __init__(self, player):
#         self.player = player
#         self.setup_subscriptions()

#     def setup_subscriptions(self):
#         """
#         Subscribes character-specific methods to damage timeline events.
#         """
#         self.player.team.game_engine.event_manager.subscribe("damage_timeline_step_3", self.modify_damage_calculation)

#     def modify_damage_calculation(self, attack):
#         """
#         Example character-specific method that modifies damage calculation.
#         """
#         if self.player in [attack['attacker'], attack['defender']]:
#             original_damage = attack['damage_amount']
#             attack['damage_amount'] += 1  # Example: Increase damage by 1
#             print(f"[Character {self.player.id}] Modified damage from {original_damage} to {attack['damage_amount']}.")