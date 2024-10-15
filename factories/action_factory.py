# factories/action_factory.py

from models.action import (
    AttackCardAction,
    PoisonCardAction, 
    WeaknessCardAction, 
    HolyShieldCardAction, 
    MagicBulletCardAction,
    SynthesisAction, 
    PurchaseAction, 
    RefineAction,
    CounterCardAction, 
    HolyLightCardAction, 
    MagicBulletCounterCardAction,
    NoResponseAction
)
CHARACTER_ACTIONS = [

]

CARD_ACTIONS = [
    AttackCardAction,
    MagicBulletCardAction,
    PoisonCardAction,
    WeaknessCardAction,
    HolyShieldCardAction
]

SPECIAL_ACTIONS = [
    SynthesisAction,
    PurchaseAction,
    RefineAction
]

COUNTER_CARD_ACTIONS = [
    CounterCardAction,
    HolyLightCardAction,
    MagicBulletCounterCardAction
]

class ActionFactory:
    def __init__(self, player):
        self._player = player
        self._game_engine = player._game_engine
        self._character_actions = CHARACTER_ACTIONS
        self._card_actions = CARD_ACTIONS
        self._counter_card_actions = COUNTER_CARD_ACTIONS
        self._special_actions = SPECIAL_ACTIONS
    
    def create_character_action(self):
        actions = []
        for action_type in self._character_actions:
            action = action_type(player=self._player, game_engine=self._game_engine)
            if action.available():
                actions.append(action)
        return actions
    
    def create_no_response_action(self):
        return [NoResponseAction(player=self._player, game_engine=self._game_engine)]
    
    def create_card_action(self, card):
        card_actions = []
        for action_type in self._card_actions:
            action = action_type(player=self._player, game_engine=self._game_engine, card=card)
            if action.available():
                card_actions.append(action)
        return card_actions
    
    def create_special_action(self):
        special_actions = []
        for action_type in self._special_actions:
            action = action_type(player=self._player, game_engine=self._game_engine)
            if action.available():
                special_actions.append(action)
        return special_actions
    
    def create_counter_card_action(self, attack_event, card):
        counter_card_actions = []
        for action_type in self._counter_card_actions:
            action = action_type(player=self._player, game_engine=self._game_engine, 
                                 attack_event=attack_event, card=card)
            if action.available():
                counter_card_actions.append(action)
        return counter_card_actions



