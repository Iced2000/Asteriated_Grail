# models/action/counter_action.py

from abc import ABC, abstractmethod
from .base_action import BaseAction, CardAction

class BaseCounterAction(BaseAction):
    def __init__(self, player, game_engine, attack_event):
        super().__init__(player, game_engine)
        self._attack_event = attack_event

    @property
    def name(self):
        return "Counter"

    @abstractmethod
    def available(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    def on_action_success(self):
        raise Exception("Counter action should not be successful")
        
class CounterCardAction(BaseCounterAction, CardAction):
    def __init__(self, player, game_engine, attack_event, card):
        BaseCounterAction.__init__(self, player, game_engine, attack_event)
        CardAction.__init__(self, card)

    @property
    def name(self):
        return f"Counter with {self.card}"

    def available(self):
        return (
            self.card.is_attack() and
            (self._attack_event['attack_type'] == "attack" or
             self._attack_event['attack_type'] == "counter") and
            (self._attack_event['card'].get_element() == self.card.get_element() or 
            self.card.is_dark_extinction()) and
            self._game_engine.get_attack_target(self._player, counter=True, attacker=self._attack_event['attacker'])
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Counter Action with {self.card.get_name()}.", debug=True)
        
        candidates = self._game_engine.get_attack_target(self._player, counter=True, attacker=self._attack_event['attacker'])
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self.card)
        
        counter_event = {
            'attack_type': "counter",
            'attacker': self._player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
            'can_not_counter': self.card.is_dark_extinction(),
        }
        self._game_engine.process_damage_timeline(counter_event, start_step=2)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self.card.get_name()} to counter Player {target.get_id()}.", broadcast=True)

        return True

class HolyLightCardAction(BaseCounterAction, CardAction):
    def __init__(self, player, game_engine, attack_event, card):
        BaseCounterAction.__init__(self, player, game_engine, attack_event)
        CardAction.__init__(self, card)

    @property
    def name(self):
        return f"Holy Light"

    def available(self):
        return (
            self.card.is_holy_light()
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} uses Holy Light", broadcast=True)
        self._player.remove_cards(self.card)
        
        return True

class MagicBulletCounterCardAction(BaseCounterAction, CardAction):
    def __init__(self, player, game_engine, attack_event, card):
        BaseCounterAction.__init__(self, player, game_engine, attack_event)
        CardAction.__init__(self, card)

    @property
    def name(self):
        return f"Counter {self.card}"
    
    def available(self):
        return (
            self.card.is_magic_bullet() and
            self._attack_event['attack_type'] == "magic_bullet"
        )
    
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Magic Bullet Counter Action with {self.card.get_name()}.", debug=True)
        
        target = self._game_engine.get_magic_bullet_target(self._player)
        
        self._player.remove_cards(self.card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': self._player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': self._attack_event['damage_amount'] + 1,
        }
        self._game_engine.process_damage_timeline(attack_event, start_step=1)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self.card.get_name()} to counter Player {target.get_id()}.", broadcast=True)
        
        return True