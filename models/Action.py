# models/Action.py

from abc import ABC, abstractmethod
from models.Effect import PoisonEffect, WeaknessEffect, HolyShieldEffect

class Action(ABC):
    def __init__(self, player, game_engine):
        self._player = player
        self._game_engine = game_engine
        self._interface = game_engine.get_interface()

    @property
    @abstractmethod
    def name(self):
        """Returns the name of the action."""
        pass

    @abstractmethod
    def available(self):
        """Returns a boolean indicating if the action is available."""
        pass

    @abstractmethod
    def execute(self):
        """
        Executes the action.
        Should return True if the action was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def on_action_success(self):
        """
        Handles post-processing after the action is executed.
        """
        pass

    def is_no_response(self):
        """
        Returns True if the action is a no response action, False otherwise.
        """
        return False

    def __str__(self):
        return self.name

class NoResponseAction(Action):
    @property
    def name(self):
        return f"No Response"

    def available(self):
        return True

    def execute(self):
        raise Exception("No response action should not be executed")

    def on_action_success(self):
        raise Exception("No response action should not be successful")
    
    def is_no_response(self):
        return True


class AttackAction(Action):
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

class AttackCardAction(AttackAction):
    def __init__(self, player, game_engine, card):
        super().__init__(player, game_engine)
        self._card = card

    @property
    def name(self):
        return f"Attack with {self._card}"

    def available(self):
        return (
            self._card.is_attack() and
            self._player.can_perform_action("attack")
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting an Attack Action with {self._card.get_name()}.", debug=True)
        
        candidates = self._game_engine.get_attack_target(self._player)
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self._card)
        
        attack_event = {
            'attack_type': "attack",
            'attacker': self._player, 
            'defender': target, 
            'card': self._card,
            'damage_amount': 2,
            'can_not_counter': self._card.is_dark_extinction(),
        }
        self._game_engine.process_damage_timeline(attack_event, start_step=1)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self._card.get_name()} to attack Player {target.get_id()}.", broadcast=True)

        return True


class MagicAction(Action):
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

class MagicCardAction(MagicAction):
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

class MagicBulletCardAction(MagicAction):
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


class SpecialAction(Action):
    @abstractmethod
    def available(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass

    def on_action_success(self):
        self._player.remove_action_point("special")

class SynthesisAction(SpecialAction):
    @property
    def name(self):
        return "Synthesize"

    def available(self):
        return (self._player.can_draw_cards(3) and
               self._player.get_team().can_synthesis() and
               self._player.can_perform_action("special"))

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Synthesis Action.", debug=True)

        if not self._player.get_team().can_synthesis():
            raise Exception("Not enough jewels to perform 'Synthesize'. Action canceled.")
        if not self._player.can_draw_cards(3):
            raise Exception(f"Cannot perform 'Synthesize' as drawing 3 cards would exceed hand size. Action canceled.")

        valid_combinations = self._player.get_team().get_synthesis_jewel_combination()
        if not valid_combinations:
            raise Exception("No valid jewel combination to perform 'Synthesize'. Action canceled.")
        
        gems_to_use, crystals_to_use = self._interface.prompt_action_selection(valid_combinations, player_id=self._player.get_id())

        self._player.get_team().remove_jewel(gem_remove=gems_to_use, crystal_remove=crystals_to_use)
        
        self._player.take_damage(3, damage_type="draw")
        self._player.get_team().add_grail(1)
        self._player.get_team().get_opposite_team().add_morale(-1)

        return True

class PurchaseAction(SpecialAction):
    @property
    def name(self):
        return "Purchase"

    def available(self):
        return (self._player.can_draw_cards(3) and
               self._player.can_perform_action("special"))
        
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Purchase Action.", debug=True)

        if not self._player.can_draw_cards(3):
            raise Exception(f"Cannot perform 'Purchase' as drawing 3 cards would exceed hand size. Action canceled.")

        self._player.take_damage(3, damage_type="draw")
        
        if self._player.get_team().can_add_jewel(gem_add=1, crystal_add=1):
            self._player.get_team().add_jewel(gem_add=1, crystal_add=1)
            self._interface.send_message(f"{self._player.get_team()} gains 1 Gem and 1 Crystal from Purchase.", debug=True)
        elif self._player.get_team().can_add_jewel(gem_add=1) or self._player.get_team().can_add_jewel(crystal_add=1):
            self._interface.send_message(f"You can add one more jewel to team.", player_id=self._player.get_id())
            choices = []
            if self._player.get_team().can_add_jewel(gem_add=1):
                choices.append('gem')
            if self._player.get_team().can_add_jewel(crystal_add=1):
                choices.append('crystal')
            choice = self._interface.prompt_action_selection(choices, player_id=self._player.get_id())
            if choice == 'gem':
                self._player.get_team().add_jewel(gem_add=1)
                self._interface.send_message(f"{self._player.get_team()} gains 1 Gem from Purchase.", debug=True)
            elif choice == 'crystal':
                self._player.get_team().add_jewel(crystal_add=1)
                self._interface.send_message(f"{self._player.get_team()} gains 1 Crystal from Purchase.", debug=True)
            else:
                raise Exception("Invalid choice for adding jewel in Purchase action.")
        else:
            self._interface.send_message(f"{self._player.get_team()}'s jewels are already at maximum. Purchase completed without adding jewels.", debug=True)

        return True

class RefineAction(SpecialAction):
    @property
    def name(self):
        return "Refine"

    def available(self):
        return (
            self._player.can_perform_action("special") and
            self._player.get_team().can_refine() and
            (self._player.can_add_jewel(gem_add=1) or 
             self._player.can_add_jewel(crystal_add=1))
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Refine Action.", debug=True)

        candidates = self._player.get_team().get_refine_jewel_combination()
        valid_combinations = []
        for combination in candidates:
            if self._player.can_add_jewel(gem_add=combination[0], crystal_add=combination[1]):
                valid_combinations.append(combination)

        if not valid_combinations:
            raise Exception("No valid jewel combination to perform 'Refine'. Action canceled.")
        
        gems_to_transfer, crystals_to_transfer = self._interface.prompt_action_selection(valid_combinations, player_id=self._player.get_id())

        self._player.get_team().remove_jewel(gem_remove=gems_to_transfer, crystal_remove=crystals_to_transfer)
        self._player.add_jewel(gem_add=gems_to_transfer, crystal_add=crystals_to_transfer)
        self._interface.send_message(f"Player {self._player.get_id()} refined {gems_to_transfer} gem(s) and {crystals_to_transfer} crystal(s). Current Jewels: {self._player.get_jewels()}", broadcast=True)
        
        return True


class CounterAction(Action):
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
        
class CounterCardAction(CounterAction):
    def __init__(self, player, game_engine, attack_event, card):
        super().__init__(player, game_engine, attack_event)
        self._card = card

    @property
    def name(self):
        return f"Counter with {self._card}"

    def available(self):
        return (
            self._card.is_attack() and
            (self._attack_event['attack_type'] == "attack" or
             self._attack_event['attack_type'] == "counter") and
            (self._attack_event['card'].get_element() == self._card.get_element() or 
            self._card.is_dark_extinction()) and
            self._game_engine.get_attack_target(self._player, counter=True, attacker=self._attack_event['attacker'])
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Counter Action with {self._card.get_name()}.", debug=True)
        
        candidates = self._game_engine.get_attack_target(self._player, counter=True, attacker=self._attack_event['attacker'])
        target = self._interface.prompt_action_selection(candidates, player_id=self._player.get_id())
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self._player.remove_cards(self._card)
        
        counter_event = {
            'attack_type': "counter",
            'attacker': self._player, 
            'defender': target, 
            'card': self._card,
            'damage_amount': 2,
            'can_not_counter': self._card.is_dark_extinction(),
        }
        self._game_engine.process_damage_timeline(counter_event, start_step=2)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self._card.get_name()} to counter Player {target.get_id()}.", broadcast=True)

        return True

class HolyLightCardAction(CounterAction):
    def __init__(self, player, game_engine, attack_event, card):
        super().__init__(player, game_engine, attack_event)
        self._card = card

    @property
    def name(self):
        return f"Holy Light"

    def available(self):
        return (
            self._card.is_holy_light()
        )

    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} uses Holy Light", broadcast=True)
        self._player.remove_cards(self._card)
        
        return True

class MagicBulletCounterCardAction(CounterAction):
    def __init__(self, player, game_engine, attack_event, card):
        super().__init__(player, game_engine, attack_event)
        self._card = card

    @property
    def name(self):
        return f"Counter {self._card}"
    
    def available(self):
        return (
            self._card.is_magic_bullet() and
            self._attack_event['attack_type'] == "magic_bullet"
        )
    
    def execute(self):
        self._interface.send_message(f"\nPlayer {self._player.get_id()} is attempting a Magic Bullet Counter Action with {self._card.get_name()}.", debug=True)
        
        target = self._game_engine.get_magic_bullet_target(self._player)
        
        self._player.remove_cards(self._card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': self._player, 
            'defender': target, 
            'card': self._card,
            'damage_amount': self._attack_event['damage_amount'] + 1,
        }
        self._game_engine.process_damage_timeline(attack_event, start_step=1)
        self._interface.send_message(f"Player {self._player.get_id()} plays {self._card.get_name()} to counter Player {target.get_id()}.", broadcast=True)
        
        return True