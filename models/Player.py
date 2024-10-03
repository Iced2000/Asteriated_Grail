# models/Player.py

from .Jewel import AgrJewel
from .Action import (
    SynthesisAction,
    PurchaseAction, RefineAction,
    AttackCardAction, MagicCardAction, HolyLightCardAction,
    CounterCardAction, NoResponseAction, MagicBulletCounterCardAction, MagicBulletCardAction
)
from .Effect import HolyShieldEffect, PoisonEffect, WeaknessEffect
from .Heal import Heal
from utils.decorators import subscribe
from game_engine.EventManager import Event
from timeline.game_timeline import GameTimeline
from timeline.damage_timeline import DamageTimeline

class Player:
    def __init__(self, player_id, team, deck, interface, event_manager, game_engine):
        self.id = player_id
        self.team = team
        self.deck = deck
        self.interface = interface
        self.event_manager = event_manager
        self.game_engine = game_engine
        self.heal = Heal()
        self.hand = []
        self.jewels = AgrJewel(interface=interface, maxJewel=3)  # Player's jewel capacity is 3
        self.max_hand_size = 6  # Define maximum hand size as per rules
        self.effects = []  # List to hold active effects
        self.can_be_attacked = True
        self.action_points = {
            "general": 1,
            "attack": 0,
            "magic": 0,
            "special": 0
        }
        
        self.setup_event_handlers()

    def setup_event_handlers(self):
        for event_type, handlers in GameTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self.event_manager.subscribe(event_type, handler, priority=priority)

        for event_type, handlers in DamageTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self.event_manager.subscribe(event_type, handler, priority=priority)

    def poison_trigger(self, event):
        if event.data['player'].id != self.id:
            return
        self.interface.send_message(f'processing poison trigger for player {self.id}', debug=True)
        poison_effects = [effect for effect in self.effects if isinstance(effect, PoisonEffect)]
        seats = self.game_engine.get_seats_order(self)
        poison_effects_sorted = sorted(poison_effects, key=lambda effect: seats.index(effect.source.id))
        for poison_effect in poison_effects_sorted:
            poison_effect.execute()

    def weakness_trigger(self, event):
        if event.data['player'].id != self.id:
            return
        self.interface.send_message(f'processing weakness trigger for player {self.id}', debug=True)
        weakness_effects = [effect for effect in self.effects if isinstance(effect, WeaknessEffect)]
        if len(weakness_effects) > 1:
            raise Exception("Player has more than one weakness effect.")
        if len(weakness_effects) != 0:
            continue_turn = weakness_effects[0].execute()
            return continue_turn
    
    def perform_actions(self):
        """
        Allows the player to perform multiple actions in their turn until they choose to stop
        or run out of available actions.
        """
        self.show_hand()
        available_actions = self.get_available_actions()
        while True:
            if not available_actions:
                raise Exception("No available actions to perform.")

            selected_action = self.interface.prompt_action_selection(available_actions, player_id=self.id)
            if not selected_action:
                raise Exception("Player chose not to select an action.")
            
            if selected_action.is_no_response():
                self.interface.send_message(f"Player {self.id} chose to end their turn.", broadcast=True)
                break
            
            success = selected_action.execute()
            if success:
                selected_action.on_action_success()
                self.event_manager.emit('after_action_phase', player=self, action=selected_action)
            else:
                raise Exception("Action execution failed.")
            # Action points are deducted within execute_action if successful
            
            available_actions = self.get_available_actions()
            if not available_actions:
                self.interface.send_message("No more available actions.", debug=True)
                break
            else:
                available_actions.append(NoResponseAction(player=self, game_engine=self.game_engine))
    
    def after_action(self, event):
        self.interface.send_message(f"Player {self.id} performed action: {event.data['action']}", debug=True)

    def reset_actions(self):
        self.interface.send_message(f'resetting actions for player {self.id}', debug=True)
        self.action_points = {
            "general": 1,
            "attack": 0,
            "magic": 0,
            "special": 0
        }



    def draw_initial_hand(self):
        self.hand = self.deck.deal(6)
        self.interface.send_message(f"Player {self.id} drew initial hand: {[card.name for card in self.hand]}", debug=True)

    # def apply_effect(self, effect):
    #     effect_name = type(effect).__name__
    #     self.effects[effect_name] = effect
    #     self.interface.send_message(f"Player {self.id} received effect: {effect_name}.")

    def take_damage(self, amount, damage_type='attack'):
        self.interface.send_message(f"Player {self.id} takes {amount} {damage_type} damage.", debug=True)
        
        # Draw cards equal to the damage taken
        cards_drawn = self.deck.deal(amount)
        self.receive_cards(cards_drawn)
        
        # Handle exploding hand if hand size exceeds the limit
        self.handle_exploding_hand()

    def get_available_actions(self):
        """
        Determines which actions are currently available to the player.
        Returns a list of actions.
        """
        available_actions = []
        for action in [SynthesisAction(player=self, game_engine=self.game_engine), 
                       PurchaseAction(player=self, game_engine=self.game_engine), 
                       RefineAction(player=self, game_engine=self.game_engine)]:
            if action.available():
                available_actions.append(action)
        
        # Include card-based actions
        for card in self.hand:
            if card.is_attack():
                action = AttackCardAction(player=self, game_engine=self.game_engine, card=card)
            elif card.is_magic_bullet():
                action = MagicBulletCardAction(player=self, game_engine=self.game_engine, card=card)
            elif card.is_magic():
                action = MagicCardAction(player=self, game_engine=self.game_engine, card=card)
            else:
                raise Exception("Card is not an attack or magic card.")

            if action.available():
                available_actions.append(action)

        return available_actions

    

    def can_draw_cards(self, number):
        return (len(self.hand) + number) <= self.max_hand_size

    def can_play_magic(self):
        # Check if player has any magic cards in hand
        return any(card.is_magic() for card in self.hand)

    def receive_cards(self, cards):
        self.hand.extend(cards)
        self.interface.send_message(f"Player {self.id} received cards: {[card.name for card in cards]}", debug=True)

    def handle_exploding_hand(self):
        if len(self.hand) > self.max_hand_size:
            excess_cards = len(self.hand) - self.max_hand_size
            self.interface.send_message(f"Player {self.id} has exceeded the hand limit by {excess_cards} card(s). Must discard down to {self.max_hand_size} cards.", player_id=self.id)

            discard_choice = self.interface.prompt_multiple_action_selection(self.hand, min_selections=excess_cards, 
                                                                             max_selections=excess_cards, player_id=self.id)
            for card in discard_choice:
                self.hand.remove(card)
                self.deck.recycle([card])
                self.team.add_morale(-1)

            self.interface.send_message(f"Player {self.id}'s hand size is now {len(self.hand)}.", debug=True)

    def get_public_info(self):
        """
        Returns a string containing the player's public information without revealing the hand.
        Includes hand size.
        """
        return (f"Player {self.id}, Jewels(G/C): {self.jewels}, \
Hand: {len(self.hand)}/{self.max_hand_size}, Effects: {self.effects}, \
Heal: {self.heal}")

    def show_hand(self):
        """
        Displays the player's current hand.
        """
        self.interface.send_message(f"\n--- Player {self.id}'s Hand ---", player_id=self.id)
        for idx, card in enumerate(self.hand):
            self.interface.send_message(f"{idx}: {card}", player_id=self.id)
        self.interface.send_message("--------------------------\n", player_id=self.id)

    def get_valid_counter_actions(self, attack_event):
        """
        Returns a list of valid counter cards based on the attack card.
        """
        valid_counter_actions = [NoResponseAction(player=self, game_engine=self.game_engine)]

        for card in self.hand:
            if card.is_attack():
                if attack_event.get('can_not_counter', False):
                    continue
                action = CounterCardAction(player=self, game_engine=self.game_engine, attack_event=attack_event, card=card)
            elif card.is_holy_light():
                action = HolyLightCardAction(player=self, game_engine=self.game_engine, attack_event=attack_event, card=card)
            elif card.is_magic():
                action = MagicBulletCounterCardAction(player=self, game_engine=self.game_engine, attack_event=attack_event, card=card)
            else:
                raise Exception("Card is not an attack or magic card.")

            if action.available():
                valid_counter_actions.append(action)
        
        return valid_counter_actions

    def respond_to_damage(self, damage):
        """
        Allows the player to respond to incoming damage with healing or other effects.
        
        :param damage: Incoming damage value.
        :return: Dictionary containing the amount of healing used.
        """
        # Placeholder: Automatically use available healing
        healing_available = min(self.heal.get_amount(), damage)
        healing_to_use = 0
        if healing_available > 0:
            self.interface.send_message(f"Player {self.id} has {healing_available} healing available.", debug=True)
            actions = [i for i in range(healing_available + 1)]
            healing_to_use = self.interface.prompt_action_selection(actions, player_id=self.id)
        if healing_to_use > 0:
            self.use_healing(healing_to_use)
        return {'healing': healing_to_use}

    def use_healing(self, amount):
        """
        Uses a specified amount of healing.
        
        :param amount: Amount of healing to use.
        """
        # Placeholder: Reduce available healing effects accordingly
        self.interface.send_message(f"Player {self.id} uses {amount} healing.", debug=True)
        # Implement actual healing consumption logic here
        self.heal.remove(amount)

    def get_holy_shield_effect(self):
        for effect in self.effects:
            if isinstance(effect, HolyShieldEffect):
                return effect
        return None
    

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
#             self.interface.send_message(f"[Character {self.player.id}] Modified damage from {original_damage} to {attack['damage_amount']}.")