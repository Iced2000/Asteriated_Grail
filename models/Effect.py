# models/Effect.py

from abc import ABC, abstractmethod

class Effect:
    def __init__(self, source, target, game_engine):
        self._source = source
        self._target = target
        self._game_engine = game_engine
        self._interface = game_engine.get_interface()

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def __str__(self):
        return "Effect"

class BasicEffect(Effect):
    def __init__(self, source, target, game_engine, card):
        super().__init__(source, target, game_engine)
        self._card = card

    @abstractmethod
    def apply(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def __str__(self):
        return "BasicEffect"

class PoisonEffect(BasicEffect):
    def __init__(self, source, target, game_engine, card, amount=1):
        super().__init__(source, target, game_engine, card)
        self._amount = amount

    def apply(self):
        self._interface.send_message(f"Player {self._target.get_id()} is poisoned by Player {self._source.get_id()}.", debug=True)
        self._target.add_effect(self)

    def execute(self):
        self._interface.send_message(f"Processing PoisonEffect to Player {self._target.get_id()} by Player {self._source.get_id()}: {self._amount} damage.", broadcast=True)

        attack_event = {
            'attack_type': "magic",
            'attacker': self._source,
            'defender': self._target,
            'card': self._card,
            'damage_amount': self._amount,
        }
        self._game_engine.process_damage_timeline(attack_event, start_step=3)
        self._game_engine.get_deck().recycle([self._card])
        self._target.remove_effect(self)

    def __str__(self):
        return "Poison"
    
    def get_source(self):
        return self._source

class WeaknessEffect(BasicEffect):
    def apply(self):
        self._interface.send_message(f"Player {self._target.get_id()} is weakened by Player {self._source.get_id()}.", debug=True)
        self._target.add_effect(self)
        self._target.set_targetable_state(effect_type="weakness", value=False)

    def execute(self):
        """
        Returns True if the turn should continue, False if the turn should end.
        """
        self._interface.send_message(f"Processing WeaknessEffect to Player {self._target.get_id()} by Player {self._source.get_id()}.", broadcast=True)
        
        valid_actions = ['skip turn', 'draw 3 cards']
        action = self._interface.prompt_action_selection(valid_actions, player_id=self._target.get_id())
        if action == 'skip turn':
            self._target.remove_effect(self)
            self._game_engine.get_deck().recycle([self._card])
            self._target.set_targetable_state(effect_type="weakness", value=True)
            return False
        elif action == 'draw 3 cards':
            attack_event = {
                'attack_type': "draw",
                'attacker': self._source, 
                'defender': self._target,
                'final_damage': 3,
            }
            self._game_engine.process_damage_timeline(attack_event, start_step=6)

            self._target.remove_effect(self)
            self._game_engine.get_deck().recycle([self._card])
            self._target.set_targetable_state(effect_type="weakness", value=True)
            return True

    def __str__(self):
        return "Weakness"

class HolyShieldEffect(BasicEffect):
    def apply(self):
        self._interface.send_message(f"Player {self._target.get_id()} activates Holy Shield.", debug=True)
        self._target.add_effect(self)
        self._target.set_targetable_state(effect_type="holy_shield", value=False)

    def execute(self):
        self._interface.send_message(f"Processing HolyShieldEffect to Player {self._target.get_id()}.", broadcast=True)
        self._target.remove_effect(self)
        self._game_engine.get_deck().recycle([self._card])
        self._target.set_targetable_state(effect_type="holy_shield", value=True)
    def __str__(self):
        return "Holy Shield"


class SpecialEffect(Effect):
    @abstractmethod
    def apply(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def __str__(self):
        return "SpecialEffect"