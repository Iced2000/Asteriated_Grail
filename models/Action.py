# models/Action.py

from abc import ABC, abstractmethod
from models.Effect import PoisonEffect, WeaknessEffect, HolyShieldEffect

class Action(ABC):
    def __init__(self, player, game_engine):
        self.player = player
        self.game_engine = game_engine
        self.interface = game_engine.interface

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
        if self.player.action_points["attack"] > 0:
            self.player.action_points["attack"] -= 1
        else:
            self.player.action_points["general"] -= 1

class AttackCardAction(AttackAction):
    def __init__(self, player, game_engine, card):
        super().__init__(player, game_engine)
        self.card = card

    @property
    def name(self):
        return f"Attack with {self.card.card_id} {self.card.name}"

    def available(self):
        return (
            self.card.is_attack() and
            (self.player.action_points.get("attack", 0) >= 1 or
             self.player.action_points.get("general", 0) >= 1)
        )

    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting an Attack Action with {self.card.name}.", debug=True)
        
        candidates = self.game_engine.get_attack_target(self.player)
        target = self.interface.prompt_action_selection(candidates, player_id=self.player.id)
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self.player.hand.remove_card(self.card)
        
        attack_event = {
            'attack_type': "attack",
            'attacker': self.player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
            'can_not_counter': self.card.is_dark_extinction(),
        }
        self.game_engine.process_damage_timeline(attack_event, start_step=1)

        self.game_engine.deck.recycle([self.card])
        self.interface.send_message(f"Player {self.player.id} plays {self.card.name} to attack Player {target.id}.", broadcast=True)

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
        if self.player.action_points["magic"] > 0:
            self.player.action_points["magic"] -= 1
        else:
            self.player.action_points["general"] -= 1

class MagicCardAction(MagicAction):
    def __init__(self, player, game_engine, card):
        super().__init__(player, game_engine)
        self.card = card

    @property
    def name(self):
        return f"Cast {self.card.card_id} {self.card.name}"

    def available(self):
        return (
            (self.card.is_poison() or
             self.card.is_weakness() or
             self.card.is_holy_shield()) and
            (self.player.action_points.get("magic", 0) >= 1 or
             self.player.action_points.get("general", 0) >= 1)
        )

    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting a Magic Action with {self.card.name}.", debug=True)
        
        target = self.interface.prompt_action_selection(self.game_engine.players, player_id=self.player.id)
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self.player.hand.remove_card(self.card)
        
        if self.card.is_poison():
            effect = PoisonEffect(source=self.player, target=target, game_engine=self.game_engine, card=self.card)
        elif self.card.is_weakness():
            effect = WeaknessEffect(source=self.player, target=target, game_engine=self.game_engine, card=self.card)
        elif self.card.is_holy_shield():
            effect = HolyShieldEffect(source=self.player, target=target, game_engine=self.game_engine, card=self.card)
        else:
            raise Exception("Invalid magic card.")
        
        effect.apply()
        self.interface.send_message(f"Player {target.id} is affected by {self.card.name} by Player {self.player.id}.", broadcast=True)
        
        return True

class MagicBulletCardAction(MagicAction):
    def __init__(self, player, game_engine, card):
        super().__init__(player, game_engine)
        self.card = card

    @property
    def name(self):
        return f"Cast {self.card.card_id} {self.card.name}"
    
    def available(self):
        return (
            self.card.is_magic_bullet() and
            (self.player.action_points.get("magic", 0) >= 1 or
             self.player.action_points.get("general", 0) >= 1)
        )
    
    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting a Magic Bullet Action with {self.card.name}.", debug=True)
        
        target = self.game_engine.get_magic_bullet_target(self.player)
        
        self.player.hand.remove_card(self.card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': self.player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
        }
        self.game_engine.process_damage_timeline(attack_event, start_step=1)

        self.game_engine.deck.recycle([self.card])
        self.interface.send_message(f"Player {self.player.id} plays {self.card.name} to cast Magic Bullet on Player {target.id}.", broadcast=True)
        
        return True


class SpecialAction(Action):
    @abstractmethod
    def available(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass

    def on_action_success(self):
        if self.player.action_points["special"] > 0:
            self.player.action_points["special"] -= 1
        else:
            self.player.action_points["general"] -= 1

class SynthesisAction(SpecialAction):
    @property
    def name(self):
        return "Synthesize"

    def available(self):
        return (self.player.hand.can_draw_cards(3) and
               self.player.team.jewels.total_jewels() >= 3 and
                (self.player.action_points["general"] >= 1 or 
                 self.player.action_points["special"] >= 1))

    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting a Synthesis Action.", debug=True)

        if self.player.team.jewels.total_jewels() < 3:
            raise Exception("Not enough jewels to perform 'Synthesize'. Action canceled.")
        if not self.player.hand.can_draw_cards(3):
            raise Exception(f"Cannot perform 'Synthesize' as drawing 3 cards would exceed hand size of {self.player.max_hand_size}. Action canceled.")

        valid_combinations = self.player.team.jewels.get_jewel_combination(min_num=3, max_num=3, gem_min=0, crystal_min=0)
        if not valid_combinations:
            raise Exception("No valid jewel combination to perform 'Synthesize'. Action canceled.")
        
        gems_to_use, crystals_to_use = self.interface.prompt_action_selection(valid_combinations, player_id=self.player.id)

        removed = self.player.team.jewels.remove_jewel(gem_remove=gems_to_use, crystal_remove=crystals_to_use)
        if not removed:
            raise Exception("Failed to remove jewels. Action canceled.")

        drawn_cards = self.player.deck.deal(3)
        if not drawn_cards:
            raise Exception("No cards drawn. Synthesis action ends.")
        self.player.hand.add_cards(drawn_cards)

        self.player.team.add_grail(1)
        self.interface.send_message(f"{self.player.team} synthesized 1 Grail. Current Grail: {self.player.team.grail}", broadcast=True)

        opposing_team = self.game_engine.get_opposite_team(self.player.team)
        opposing_team.add_morale(-1)
        self.interface.send_message(f"{opposing_team} loses 1 morale due to Synthesis. Current Morale: {opposing_team.morale}", broadcast=True)
        return True

class PurchaseAction(SpecialAction):
    @property
    def name(self):
        return "Purchase"

    def available(self):
        return (self.player.hand.can_draw_cards(3) and
                (self.player.action_points["general"] >= 1 or 
                 self.player.action_points["special"] >= 1))
        
    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting a Purchase Action.", debug=True)

        if not self.player.hand.can_draw_cards(3):
            raise Exception(f"Cannot perform 'Purchase' as drawing 3 cards would exceed hand size of {self.player.hand.max_size}. Action canceled.")

        drawn_cards = self.player.deck.deal(3)
        if not drawn_cards:
            raise Exception("No cards drawn. Purchase action ends.")

        self.interface.send_message(f"Player {self.player.id} drew: {[card.name for card in drawn_cards]}", player_id=self.player.id)
        
        self.player.hand.add_cards(drawn_cards)
        
        current_jewels = self.player.team.jewels.total_jewels()
        if current_jewels >= self.player.team.jewels.max_jewel:
            self.interface.send_message(f"{self.player.team}'s jewels are already at maximum. Purchase completed without adding jewels.", broadcast=True)
        elif current_jewels == self.player.team.jewels.max_jewel - 1:
            self.interface.send_message(f"You can add one more jewel to reach the maximum of {self.player.team.jewels.max_jewel}.", player_id=self.player.id)
            choice = self.interface.prompt_action_selection(['gem', 'crystal'], player_id=self.player.id)
            if choice == 'gem':
                self.player.team.jewels.add_jewel(gem_add=1)
                self.interface.send_message(f"{self.player.team} gains 1 Gem from Purchase.", broadcast=True)
            elif choice == 'crystal':
                self.player.team.jewels.add_jewel(crystal_add=1)
                self.interface.send_message(f"{self.player.team} gains 1 Crystal from Purchase.", broadcast=True)
            else:
                raise Exception("Invalid choice for adding jewel in Purchase action.")
        else:
            if self.player.team.jewels.can_add(gem_add=1, crystal_add=1):
                self.player.team.jewels.add_jewel(gem_add=1, crystal_add=1)
                self.interface.send_message(f"{self.player.team} gains 1 Gem and 1 Crystal from Purchase.", broadcast=True)
            else:
                raise Exception("Unexpected error in adding jewels. Purchase completed without adding jewels.")
        return True

class RefineAction(SpecialAction):
    @property
    def name(self):
        return "Refine"

    def available(self):
        return (
            (self.player.action_points.get("general", 0) >= 1 or 
             self.player.action_points.get("special", 0) >= 1) and
            (self.player.team.jewels.total_jewels() >= 1) and
            (self.player.jewels.total_jewels() < self.player.jewels.max_jewel)
        )

    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting a Refine Action.", debug=True)

        available_jewels = self.player.team.jewels.total_jewels()
        player_available_space = self.player.jewels.max_jewel - self.player.jewels.total_jewels()
        if available_jewels == 0 or player_available_space == 0:
            raise Exception("No jewels available to refine or player's jewel capacity is full. Action canceled.")

        max_transfer = min(2, available_jewels, player_available_space)
        valid_combinations = self.player.team.jewels.get_jewel_combination(min_num=1, max_num=max_transfer, gem_min=0, crystal_min=0)
        if not valid_combinations:
            raise Exception("No valid jewel combination to perform 'Refine'. Action canceled.")
        
        gems_to_transfer, crystals_to_transfer = self.interface.prompt_action_selection(valid_combinations, player_id=self.player.id)

        removed = self.player.team.jewels.remove_jewel(gem_remove=gems_to_transfer, crystal_remove=crystals_to_transfer)
        if not removed:
            raise Exception("Failed to remove jewels. Action canceled.")

        if not self.player.jewels.can_add(gem_add=gems_to_transfer, crystal_add=crystals_to_transfer):
            raise Exception(f"Cannot transfer jewels as it would exceed your jewel capacity of {self.player.jewels.max_jewel}. Action canceled.")

        self.player.jewels.add_jewel(gem_add=gems_to_transfer, crystal_add=crystals_to_transfer)
        self.interface.send_message(f"Player {self.player.id} refined {gems_to_transfer} gem(s) and {crystals_to_transfer} crystal(s). Current Jewels: {self.player.jewels}", broadcast=True)
        return True


class CounterAction(Action):
    def __init__(self, player, game_engine, attack_event):
        super().__init__(player, game_engine)
        self.attack_event = attack_event

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
        self.card = card

    @property
    def name(self):
        return f"Counter with {self.card.card_id} {self.card.name}"

    def available(self):
        return (
            self.card.is_attack() and
            (self.attack_event['card'].element == self.card.element or 
            self.attack_event['card'].is_dark_extinction()) and
            len(self.game_engine.get_attack_target(self.player, counter=True, attacker=self.attack_event['attacker'])) > 0
        )

    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting a Counter Action with {self.card.name}.", debug=True)
        
        candidates = self.game_engine.get_attack_target(self.player, counter=True, attacker=self.attack_event['attacker'])
        if not candidates:
            raise Exception("No available opponents to counter. Action canceled.")
        
        target = self.interface.prompt_action_selection(candidates, player_id=self.player.id)
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        self.player.hand.remove(self.card)
        
        counter_event = {
            'attack_type': "counter",
            'attacker': self.player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
            'can_not_counter': self.card.is_dark_extinction(),
        }
        self.game_engine.process_damage_timeline(counter_event, start_step=2)

        self.game_engine.deck.recycle([self.card])
        self.interface.send_message(f"Player {self.player.id} plays {self.card.name} to counter Player {target.id}.", broadcast=True)

        return True

class HolyLightCardAction(CounterAction):
    def __init__(self, player, game_engine, attack_event, card):
        super().__init__(player, game_engine, attack_event)
        self.card = card

    @property
    def name(self):
        return f"Holy Light"

    def available(self):
        return (
            self.card.is_holy_light()
        )

    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} uses Holy Light", broadcast=True)
        
        self.player.hand.remove_card(self.card)
        self.game_engine.deck.recycle([self.card])
        
        return True

class MagicBulletCounterCardAction(CounterAction):
    def __init__(self, player, game_engine, attack_event, card):
        super().__init__(player, game_engine, attack_event)
        self.card = card

    @property
    def name(self):
        return f"Counter {self.card.card_id} {self.card.name}"
    
    def available(self):
        return (
            self.card.is_magic_bullet() and
            self.attack_event['attack_type'] == "magic_bullet"
        )
    
    def execute(self):
        self.interface.send_message(f"\nPlayer {self.player.id} is attempting a Magic Bullet Counter Action with {self.card.name}.", debug=True)
        
        target = self.game_engine.get_magic_bullet_target(self.player)
        
        self.player.hand.remove_card(self.card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': self.player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': self.attack_event['damage_amount'] + 1,
        }
        self.game_engine.process_damage_timeline(attack_event, start_step=1)

        self.game_engine.deck.recycle([self.card])
        self.interface.send_message(f"Player {self.player.id} plays {self.card.name} to counter Player {target.id}.", broadcast=True)
        
        return True