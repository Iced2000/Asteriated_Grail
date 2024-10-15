# models/action/attack_action.py

from abc import ABC, abstractmethod
from .base_action import BaseAction, CardAction

class BaseAttackAction(BaseAction):
    @property
    @abstractmethod
    def name(self):
        pass
    
    @abstractmethod
    def available(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    def on_action_success(self):
        self._player.remove_action_point("attack")

class AttackCardAction(BaseAttackAction, CardAction):
    def __init__(self, player, game_engine, card):
        BaseAttackAction.__init__(self, player, game_engine)
        CardAction.__init__(self, card)

    @property
    def name(self):
        return f"Attack with {self.card}"

    def available(self):
        return (
            self.card.is_attack() and
            self._player.can_perform_action("attack")
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting an Attack Action with {self.card.get_name()}.", debug=True)
        
        candidates = self._game_engine.get_attack_target(self._player)
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self.card)
        
        attack_event = {
            'attack_type': "attack",
            'attacker': self._player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
            'can_not_counter': self.card.is_dark_extinction(),
        }
        self._game_engine.process_damage_timeline(attack_event, start_step=1)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self.card.get_name()} to attack Player {target.get_id()}.", broadcast=True)

        return True