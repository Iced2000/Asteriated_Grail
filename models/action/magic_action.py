# models/action/magic_action.py

from abc import ABC, abstractmethod
from models.effect import PoisonEffect, WeaknessEffect, HolyShieldEffect
from .base_action import BaseAction

class BaseMagicAction(BaseAction):
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
        self._player.remove_action_point("magic")

class MagicCardAction(BaseMagicAction):
    def __init__(self, player, game_engine, card):
        super().__init__(player, game_engine)
        self._card = card

    @property
    def name(self):
        return f"Cast {self._card}"

    def available(self):
        return (
            (self._card.is_poison() or
             self._card.is_weakness() or
             self._card.is_holy_shield()) and
            self._player.can_perform_action("magic")
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Magic Action with {self._card.get_name()}.", debug=True)
        
        candidates = self._game_engine.get_magic_target(self._player, card=self._card)
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self._card, recycle=False)
        
        if self._card.is_poison():
            effect = PoisonEffect(source=self._player, target=target, game_engine=self._game_engine, card=self._card)
        elif self._card.is_weakness():
            effect = WeaknessEffect(source=self._player, target=target, game_engine=self._game_engine, card=self._card)
        elif self._card.is_holy_shield():
            effect = HolyShieldEffect(source=self._player, target=target, game_engine=self._game_engine, card=self._card)
        else:
            raise Exception("Invalid magic card.")
        
        effect.apply()
        self._interface.send_message(f"Player {target.get_id()} is affected by {self._card.get_name()} by Player {self._player.get_id()}.", broadcast=True)
        
        return True

class MagicBulletCardAction(BaseMagicAction):
    def __init__(self, player, game_engine, card):
        super().__init__(player, game_engine)
        self._card = card

    @property
    def name(self):
        return f"Cast {self._card}"
    
    def available(self):
        return (
            self._card.is_magic_bullet() and
            self._player.can_perform_action("magic")
        )
    
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Magic Bullet Action with {self._card.get_name()}.", debug=True)
        
        target = self._game_engine.get_magic_bullet_target(self._player)
        
        self._player.remove_cards(self._card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': self._player, 
            'defender': target, 
            'card': self._card,
            'damage_amount': 2,
        }
        self._game_engine.process_damage_timeline(attack_event, start_step=1)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self._card.get_name()} to cast Magic Bullet on Player {target.get_id()}.", broadcast=True)
        
        return True