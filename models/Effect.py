# models/Effect.py

from abc import ABC, abstractmethod

class Effect:
    def __init__(self, source, target, game_engine):
        self.source = source
        self.target = target
        self.game_engine = game_engine
        self.interface = game_engine.interface

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
        self.card = card

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
        self.amount = amount

    def apply(self):
        self.interface.send_message(f"Player {self.target.id} is poisoned by Player {self.source.id}.", debug=True)
        self.target.effects.add_effect(self)

    def execute(self):
        self.interface.send_message(f"Applying PoisonEffect to Player {self.target.id} by Player {self.source.id}: {self.amount} damage.", broadcast=True)

        attack_event = {
            'attack_type': "magic",
            'attacker': self.source, 
            'defender': self.target, 
            'card': self.card,
            'damage_amount': self.amount,
        }
        self.game_engine.process_damage_timeline(attack_event, start_step=3)
        self.game_engine.deck.recycle([self.card])
        self.target.effects.remove_effect(self)

    def __str__(self):
        return "Poison"

class WeaknessEffect(BasicEffect):
    def apply(self):
        self.interface.send_message(f"Player {self.target.id} is weakened by Player {self.source.id}.", debug=True)
        self.target.effects.add_effect(self)

    def execute(self):
        """
        Returns True if the turn should continue, False if the turn should end.
        """
        self.interface.send_message(f"Applying WeaknessEffect to Player {self.target.id} by Player {self.source.id}.", broadcast=True)
        
        valid_actions = ['skip turn', 'draw 3 cards']
        action = self.interface.prompt_action_selection(valid_actions, player_id=self.target.id)
        if action == 'skip turn':
            self.target.effects.remove_effect(self)
            self.game_engine.deck.recycle([self.card])
            return False
        elif action == 'draw 3 cards':
            attack_event = {
                'attack_type': "draw",
                'attacker': self.source, 
                'defender': self.target,
                'final_damage': 3,
            }
            self.game_engine.process_damage_timeline(attack_event, start_step=6)
            self.target.effects.remove_effect(self)
            self.game_engine.deck.recycle([self.card])
            return True

    def __str__(self):
        return "Weakness"

class HolyShieldEffect(BasicEffect):
    def apply(self):
        self.interface.send_message(f"Player {self.target.id} activates Holy Shield.", debug=True)
        self.target.effects.add_effect(self)

    def execute(self):
        self.interface.send_message(f"Applying HolyShieldEffect to Player {self.target.id}.", broadcast=True)
        self.target.effects.remove_effect(self)
        self.game_engine.deck.recycle([self.card])

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