# models/Effect.py

from abc import ABC, abstractmethod

class Effect:
    @abstractmethod
    def apply(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def __str__(self):
        return "Effect"

class BasicEffect(Effect):
    @abstractmethod
    def apply(self, player, **kwargs):
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def __str__(self):
        return "BasicEffect"

class PoisonEffect(BasicEffect):
    def __init__(self, source, target, card, amount=1):
        self.source = source
        self.target = target
        self.card = card
        self.amount = amount

    def apply(self, *args, **kwargs):
        print(f"Player {self.target.id} is poisoned by Player {self.source.id}.")
        self.target.effects.append(self)

    def execute(self, *args, **kwargs):
        game_engine = kwargs.get("game_engine")
        print(f"Applying PoisonEffect to Player {self.target.id}: {self.amount} damage.")

        # TODO: Implement PoisonEffect
        attack_event = {
            'attack_type': "magic",
            'attacker': self.source, 
            'defender': self.target, 
            'card': self.card,
            'damage_amount': self.amount,
        }
        game_engine.process_damage_timeline(attack_event, start_step=3)

        game_engine.deck.recycle([self.card])

    def __str__(self):
        return "Poison"

class WeaknessEffect(BasicEffect):
    def __init__(self, source, target, card):
        self.source = source
        self.target = target
        self.card = card

    def apply(self, *args, **kwargs):
        print(f"Player {self.target.id} is weakened by Player {self.source.id}.")
        self.target.effects.append(self)

    def execute(self, *args, **kwargs):
        """
        Returns True if the turn should continue, False if the turn should end.
        """
        game_engine = kwargs.get("game_engine")
        print(f"Applying WeaknessEffect to Player {self.target.id}.")
        
        valid_actions = ['skip turn', 'draw 3 cards']
        action = game_engine.interface.prompt_action_selection(valid_actions)
        if action == 'skip turn':
            game_engine.deck.recycle([self.card])
            return False
        elif action == 'draw 3 cards':
            attack_event = {
                'attack_type': "draw",
                'attacker': self.source, 
                'defender': self.target,
                'final_damage': 3,
            }
            game_engine.process_damage_timeline(attack_event, start_step=6)
            game_engine.deck.recycle([self.card])
            return True

    def __str__(self):
        return "Weakness"

class HolyShieldEffect(BasicEffect):
    def __init__(self, source, target, card):
        self.source = source
        self.target = target
        self.card = card

    def apply(self, *args, **kwargs):
        print(f"Player {self.target.id} activates Holy Shield.")
        self.target.effects.append(self)

    def execute(self, *args, **kwargs):
        game_engine = kwargs.get("game_engine")
        print(f"Applying HolyShieldEffect to Player {self.target.id}.")

        game_engine.deck.recycle([self.card])

    def __str__(self):
        return "Holy Shield"


class SpecialEffect(Effect):
    @abstractmethod
    def apply(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def __str__(self):
        return "SpecialEffect"