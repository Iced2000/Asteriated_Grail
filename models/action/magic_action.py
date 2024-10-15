# models/action/magic_action.py

from abc import ABC, abstractmethod
from models.effect import PoisonEffect, WeaknessEffect, HolyShieldEffect
from .base_action import BaseAction, CardAction

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

class PoisonCardAction(BaseMagicAction, CardAction):
    def __init__(self, player, game_engine, card):
        BaseMagicAction.__init__(self, player, game_engine)
        CardAction.__init__(self, card)
    
    @property
    def name(self):
        return f"Cast poison card {self.card}"

    def available(self):
        return (
            self.card.is_poison() and
            self._player.can_perform_action("magic")
        )
    
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Poison Action with {self.card.get_name()}.", debug=True)
        
        candidates = self._game_engine.get_magic_target(self._player, card=self.card)
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self.card, recycle=False)
        effect = PoisonEffect(source=self._player, target=target, game_engine=self._game_engine, card=self.card)
        effect.apply()
        self._interface.send_message(f"Player {target.get_id()} is affected by {self.card.get_name()} by Player {self._player.get_id()}.", broadcast=True)
        
        return True
    
class WeaknessCardAction(BaseMagicAction, CardAction):
    def __init__(self, player, game_engine, card):
        BaseMagicAction.__init__(self, player, game_engine)
        CardAction.__init__(self, card)
    
    @property
    def name(self):
        return f"Cast weakness card {self.card}"
    
    def available(self):
        return (
            self.card.is_weakness() and
            self._player.can_perform_action("magic")
        )
    
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Weakness Action with {self.card.get_name()}.", debug=True)

        candidates = self._game_engine.get_magic_target(self._player, card=self.card)
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self.card, recycle=False)
        effect = WeaknessEffect(source=self._player, target=target, game_engine=self._game_engine, card=self.card)
        effect.apply()
        self._interface.send_message(f"Player {target.get_id()} is affected by {self.card.get_name()} by Player {self._player.get_id()}.", broadcast=True)
        
        return True
    
class HolyShieldCardAction(BaseMagicAction, CardAction):
    def __init__(self, player, game_engine, card):
        BaseMagicAction.__init__(self, player, game_engine)
        CardAction.__init__(self, card)
    
    @property
    def name(self):
        return f"Cast holy shield card {self.card}"
    
    def available(self):
        # TODO: if four people have holy shield, then you can't cast magic cards
        return (
            self.card.is_holy_shield() and
            self._player.can_perform_action("magic")
        )
    
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Holy Shield Action with {self.card.get_name()}.", debug=True)
        
        candidates = self._game_engine.get_magic_target(self._player, card=self.card)
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self.card, recycle=False)
        effect = HolyShieldEffect(source=self._player, target=target, game_engine=self._game_engine, card=self.card)
        effect.apply()
        self._interface.send_message(f"Player {target.get_id()} is affected by {self.card.get_name()} by Player {self._player.get_id()}.", broadcast=True)
        
        return True
    
class MagicBulletCardAction(BaseMagicAction, CardAction):
    def __init__(self, player, game_engine, card):
        BaseMagicAction.__init__(self, player, game_engine)
        CardAction.__init__(self, card)

    @property
    def name(self):
        return f"Cast {self.card}"
    
    def available(self):
        return (
            self.card.is_magic_bullet() and
            self._player.can_perform_action("magic")
        )
    
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Magic Bullet Action with {self.card.get_name()}.", debug=True)
        
        target = self._game_engine.get_magic_bullet_target(self._player)
        
        self._player.remove_cards(self.card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': self._player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
        }
        self._game_engine.process_damage_timeline(attack_event, start_step=1)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self.card.get_name()} to cast Magic Bullet on Player {target.get_id()}.", broadcast=True)
        
        return True