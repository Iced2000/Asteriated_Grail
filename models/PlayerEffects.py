# models/PlayerEffects.py

class PlayerEffects:
    def __init__(self):
        self.effects = []

    def add_effect(self, effect):
        self.effects.append(effect)

    def remove_effect(self, effect):
        if effect in self.effects:
            self.effects.remove(effect)
        else:
            raise Exception(f"Effect {effect} not found in effects.")

    def get_effects(self, effect_type=None):
        if effect_type:
            effects = [effect for effect in self.effects if isinstance(effect, effect_type)]
            return effects
        else:
            return self.effects
    
    def clear(self):
        self.effects = []

    def __str__(self):
        return f"Effects: {[str(effect) for effect in self.effects]}"