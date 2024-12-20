# models/characters/base_player.py

from timeline import GameTimeline, DamageTimeline
from models import Jewel, PlayerHeal, PlayerHand, PlayerEffects
from models.effect import PoisonEffect, WeaknessEffect
from factories.action_factory import ActionFactory

class BasePlayer:
    def __init__(self, character_config):
        self._id = character_config['player_id']
        self._team = character_config['team']
        self._game_engine = character_config['game_engine']
        self._deck = self._game_engine.get_deck()
        self._interface = self._game_engine.get_interface()
        self._event_manager = self._game_engine.get_event_manager()
        self._action_factory = ActionFactory(player=self)
        
        self._heal = PlayerHeal()
        self._hand = PlayerHand()
        self._effects = PlayerEffects()
        self._jewels = Jewel(maxJewel=3)  # Player's jewel capacity is 3
        self._state = {
            'can_be_attacked': True,
        } # allowed actions
        self._action_points = {
            "general": 1,
            "attack": 0,
            "magic": 0,
            "special": 0
        }
        
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        for event_type, handlers in GameTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self._event_manager.subscribe(event_type, handler, priority=priority)

        for event_type, handlers in DamageTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self._event_manager.subscribe(event_type, handler, priority=priority)

    def _poison_trigger(self, event):
        if event.data['player'].get_id() != self._id:
            return
        self._interface.send_message(f'processing poison trigger for player {self._id}', debug=True)
        poison_effects = self._effects.get_effects(PoisonEffect)
        seats = self._game_engine.get_seats_order(self)
        poison_effects_sorted = sorted(poison_effects, key=lambda effect: seats.index(effect.get_source().get_id()))
        for poison_effect in poison_effects_sorted:
            poison_effect.execute()

    def _weakness_trigger(self, event):
        if event.data['player'].get_id() != self._id:
            return
        self._interface.send_message(f'processing weakness trigger for player {self._id}', debug=True)
        weakness_effects = self._effects.get_effects(WeaknessEffect)
        if len(weakness_effects) > 1:
            raise Exception("Player has more than one weakness effect.")
        if len(weakness_effects) == 1:
            continue_turn = weakness_effects[0].execute()
            return continue_turn
    
    def perform_actions(self):
        """
        Allows the player to perform multiple actions in their turn until they choose to stop
        or run out of available actions.
        """
        self.show_hand()
        available_actions = self._get_available_actions()
        while True:
            if not available_actions:
                raise Exception("No available actions to perform.")

            selected_action = self._interface.prompt_action_selection(available_actions, player_id=self._id)
            if not selected_action:
                raise Exception("Player chose not to select an action.")
            
            if selected_action.is_no_response():
                self._interface.send_message(f"Player {self._id} chose to end their turn.", broadcast=True)
                break
            
            success = selected_action.execute()
            if success:
                selected_action.on_action_success()
                self._event_manager.emit('after_action_phase', player=self, action=selected_action)
            else:
                raise Exception("Action execution failed.")
            # Action points are deducted within execute_action if successful
            
            available_actions = self._get_available_actions()
            if not available_actions:
                self._interface.send_message("No more available actions.", debug=True)
                break
            else:
                available_actions.extend(self._action_factory.create_no_response_action())
    
    def after_action(self, event):
        self._interface.send_message(f"Player {self._id} performed action: {event.data['action']}", debug=True)

    def reset_actions(self):
        self._interface.send_message(f'resetting actions for player {self._id}', debug=True)
        self._action_points = {
            "general": 1,
            "attack": 0,
            "magic": 0,
            "special": 0
        }

    def draw_initial_hand(self):
        self._interface.send_message(f"Player {self._id} drew initial hand.", debug=True)
        initial_cards = self._deck.deal(3)
        exploded = self._hand.add_cards(initial_cards)
        if exploded:
            raise Exception("Player's initial hand exploded.")

    def take_damage(self, amount, damage_type='attack', **kwargs):
        self._interface.send_message(f"Player {self._id} takes {amount} {damage_type} damage.", debug=True)
        cards_drawn = self._deck.deal(amount)
        morale_penalty = self.add_cards(cards_drawn)
        if 'event' in kwargs:
            if kwargs['event'].get('max_morale_penalty', 100) < morale_penalty:
                morale_penalty = kwargs['event'].get('max_morale_penalty', 100)
            kwargs['event'].data['morale_penalty'] = morale_penalty
        self._team.add_morale(-morale_penalty)

    def _get_available_actions(self):
        available_actions = []

        available_actions.extend(self._action_factory.create_character_action())
        for card in self._hand.get_cards():
            available_actions.extend(self._action_factory.create_card_action(card))
        available_actions.extend(self._action_factory.create_special_action())

        return available_actions
    
    def get_valid_counter_actions(self, attack_event):
        """
        Returns a list of valid counter cards based on the attack card.
        """
        valid_counter_actions = []
        valid_counter_actions.extend(self._action_factory.create_no_response_action())
        for card in self._hand.get_cards():
            valid_counter_actions.extend(self._action_factory.create_counter_card_action(attack_event, card))
        
        return valid_counter_actions

    def get_public_info(self):
        """
        Returns a string containing the player's public information without revealing the hand.
        Includes hand size.
        """
        return (f"Player {self._id}, Jewels(G/C): {self._jewels}, \
Hand: {self._hand}, Effects: {self._effects}, \
Heal: {self._heal}")

    def respond_to_damage(self, damage):
        """
        Allows the player to respond to incoming damage with healing or other effects.
        
        :param damage: Incoming damage value.
        :return: Dictionary containing the amount of healing used.
        """
        healing_available = min(self._heal.get_amount(), damage)
        healing_to_use = 0
        if healing_available > 0:
            self._interface.send_message(f"Player {self._id} has {healing_available} healing available.", debug=True)
            actions = [i for i in range(healing_available + 1)]
            healing_to_use = self._interface.prompt_action_selection(actions, player_id=self._id)
        if healing_to_use > 0:
            self._use_healing(healing_to_use)
        return {'healing': healing_to_use}
    
    def __str__(self):
        # Optional: Override to prevent displaying the hand when not needed
        return self.get_public_info()
    
    # Getters
    def get_id(self):
        return self._id
    
    def get_team(self):
        return self._team
    
    def get_state(self):
        return self._state
    
    def get_action_points(self):
        return self._action_points
    
    def get_jewels(self):
        return self._jewels
    
    # hand related
    def show_hand(self):
        hand = self._hand.get_cards()
        self._interface.send_message(f"\n--- Player {self._id}'s Hand ---", player_id=self._id)
        for idx, card in enumerate(hand):
            self._interface.send_message(f"{idx}: {card}", player_id=self._id)
        self._interface.send_message("--------------------------\n", player_id=self._id)
    
    def add_cards(self, cards):
        """
        Adds cards to the player's hand.
        Returns the morale penalty for the player's team if the hand exploded.
        """
        if not isinstance(cards, list):
            cards = [cards]
        hand_exploded = self._hand.add_cards(cards)
        if hand_exploded:
            return self._handle_exploding_hand()
        return 0

    def remove_cards(self, cards, recycle=True, exhibition=True):
        if not isinstance(cards, list):
            cards = [cards]
        self._hand.remove_cards(cards)
        if recycle:
            self._deck.recycle(cards)
        if exhibition:
            self._interface.send_message(f"Player {self._id} discarded {cards} for exhibition.", broadcast=True)

    def _handle_exploding_hand(self):
        """
        Handles the case where the player's hand exceeds the maximum size.
        Discards excess cards.
        Returns the morale penalty for the player's team.
        """
        excess_cards = self._hand.size() - self._hand.get_max_size()
        self._interface.send_message(f"Player {self._id} has exceeded the hand limit by {excess_cards} card(s). Must discard down to {self._hand.get_max_size()} cards.", player_id=self._id)

        discard_choice = self._interface.prompt_multiple_action_selection(self._hand.get_cards(), min_selections=excess_cards, 
                                                                            max_selections=excess_cards, player_id=self._id)
        self.remove_cards(discard_choice)
        self._interface.send_message(f"Player {self._id}'s hand size is now {self._hand.size()}.", debug=True)
        
        morale_penalty = excess_cards
        return morale_penalty

    def can_draw_cards(self, num_cards):
        return self._hand.can_draw_cards(num_cards)
    
    def get_hand_size(self):
        return self._hand.size()
    
    def set_hand_max_size(self, max_size):
        """
        Sets the maximum size of the player's hand.
        Returns the morale penalty for the player's team if the hand exploded.
        """
        self._hand.set_max_size(max_size)
        if self._hand.exploded():
            return self._handle_exploding_hand()
        return 0
    
    def get_hand_max_size(self):
        return self._hand.get_max_size()
    
    def get_hand_cards(self):
        return self._hand.get_cards()
    
    #TODO
    # can discard same type of hand cards
    # discard same type of hand cards
    
    # effects related
    def get_effects(self, effect_type=None):
        return self._effects.get_effects(effect_type)
    
    def add_effect(self, effect):
        self._effects.add_effect(effect)
    
    def remove_effect(self, effect):
        self._effects.remove_effect(effect)
    
    # healing related
    def _use_healing(self, amount):
        self._interface.send_message(f"Player {self._id} uses {amount} healing.", debug=True)
        self._heal.remove(amount)

    def get_heal_amount(self):
        return self._heal.get_amount()
    
    def add_heal(self, amount):
        self._heal.add(amount)
    
    def remove_heal(self, amount):
        self._heal.remove(amount)
    
    def get_heal_max_amount(self):
        return self._heal.get_max_amount()
    
    def set_heal_max_amount(self, max_amount):
        self._heal.set_max_amount(max_amount)
        self._heal.set_amount(min(self._heal.get_amount(), max_amount))
    
    # jewel related
    def can_add_jewel(self, gem_add=0, crystal_add=0):
        return self._jewels.can_add(gem_add, crystal_add)
    
    def can_remove_jewel(self, gem_remove=0, crystal_remove=0):
        return self._jewels.can_remove(gem_remove, crystal_remove)
    
    def add_jewel(self, gem_add=0, crystal_add=0):
        self._interface.send_message(f"Player {self._id} added {gem_add} gem(s) and {crystal_add} crystal(s).", debug=True)
        self._jewels.add_jewel(gem_add, crystal_add)
    
    def remove_jewel(self, gem_remove=0, crystal_remove=0):
        self._interface.send_message(f"Player {self._id} removed {gem_remove} gem(s) and {crystal_remove} crystal(s).", debug=True)
        self._jewels.remove_jewel(gem_remove, crystal_remove)
    
    def get_jewel_combination(self, min_num, max_num, gem_min=0, crystal_min=0):
        return self._jewels.get_jewel_combination(min_num, max_num, gem_min, crystal_min)

    # action points related
    def add_action_point(self, action_type):
        self._interface.send_message(f"Player {self._id} added 1 action point to {action_type}.", debug=True)
        self._action_points[action_type] += 1
    
    def remove_action_point(self, action_type):
        if self._action_points[action_type] > 0:
            self._action_points[action_type] -= 1
        elif self._action_points['general'] > 0:
            self._action_points['general'] -= 1
        else:
            raise Exception("Not enough action points to remove.")
    
    def can_perform_action(self, action_type):
        state_allowed = self._state.get(f'can_{action_type}', True)
        action_point_allowed = self._action_points[action_type] > 0 or self._action_points['general'] > 0
        return state_allowed and action_point_allowed
    
    # state related
    def set_state(self, state_type, value):
        self._state[state_type] = value
    
    def set_targetable_state(self, effect_type, value):
        self._state[f'can_be_{effect_type}'] = value
    
    def can_be_targeted(self, effect_type):
        return self._state.get(f'can_be_{effect_type}', True)
        
