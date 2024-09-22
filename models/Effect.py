# models/Effect.py

class Effect:
    def apply(self, player, **kwargs):
        pass

class PoisonEffect(Effect):
    def __init__(self, amount=1, duration=1):
        self.amount = amount
        self.duration = duration  # Number of turns the poison is active

    def apply(self, player, **kwargs):
        print(f"Player {player.id} is poisoned for {self.duration} turn(s).")
        player.effects['poison'] = self

    def process_turn(self, player):
        print(f"Applying PoisonEffect to Player {player.id}: {self.amount} damage.")
        player.take_damage(self.amount, damage_type='magic')
        self.duration -= 1
        if self.duration <= 0:
            del player.effects['poison']
            print(f"PoisonEffect on Player {player.id} has expired.")

class WeaknessEffect(Effect):
    def __init__(self, duration=1):
        self.duration = duration

    def apply(self, player, **kwargs):
        print(f"Player {player.id} is weakened for {self.duration} turn(s).")
        player.effects['weakness'] = self

    def process_turn(self, player):
        print(f"Applying WeaknessEffect to Player {player.id}.")
        # Implement any weakness-related penalties here (e.g., reducing action points)
        self.duration -= 1
        if self.duration <= 0:
            del player.effects['weakness']
            print(f"WeaknessEffect on Player {player.id} has expired.")

class HolyShieldEffect(Effect):
    def __init__(self):
        self.active = True  # Indicates if the shield is active

    def apply(self, player, **kwargs):
        print(f"Player {player.id} activates Holy Shield.")
        player.effects['holy_shield'] = self

    def absorb_attack(self):
        if self.active:
            self.active = False
            print("Holy Shield absorbed the attack and is now deactivated.")
            return True
        return False

class MagicBulletEffect(Effect):
    def __init__(self, damage_increment=1):
        self.damage_increment = damage_increment  # Damage added with each pass

    def apply(self, player, target, game_engine, **kwargs):
        print(f"Magic Bullet cast by Player {player.id} towards Player {target.id}.")
        # Emit a new attack event with increased damage
        game_engine.event_manager.emit("attack", attacker=player, defender=target, card=None, damage_increment=self.damage_increment)

class HealingEffect(Effect):
    def __init__(self, amount=1):
        self.amount = amount
        self.duration = 1  # Number of turns the healing is active

    def apply(self, player, **kwargs):
        print(f"Player {player.id} gains {self.amount} healing effect.")
        player.effects['healing'] = self

    def process_turn(self, player):
        # Example logic for processing healing effects each turn
        self.duration -= 1
        if self.duration <= 0:
            del player.effects['healing']
            print(f"Healing effect on Player {player.id} has expired.")