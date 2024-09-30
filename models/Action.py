# models/Action.py

from abc import ABC, abstractmethod
from models.Effect import PoisonEffect, WeaknessEffect, HolyShieldEffect

class Action(ABC):
    @property
    @abstractmethod
    def name(self):
        """Returns the name of the action."""
        pass

    @abstractmethod
    def available(self, *args, **kwargs):
        """Returns a dictionary of required action points for the action."""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Executes the action.
        Should return True if the action was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def on_action_success(self, *args, **kwargs):
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

    def available(self, *args, **kwargs):
        return True

    def execute(self, *args, **kwargs):
        raise Exception("No response action should not be executed")

    def on_action_success(self, *args, **kwargs):
        raise Exception("No response action should not be successful")
    
    def is_no_response(self):
        return True


class AttackAction(Action):
    @property
    @abstractmethod
    def name(self):
        pass
    
    @abstractmethod
    def available(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def on_action_success(self, *args, **kwargs):
        player = kwargs.get("player")
        if player.action_points["attack"] > 0:
            player.action_points["attack"] -= 1
        else:
            player.action_points["general"] -= 1

class AttackCardAction(AttackAction):
    def __init__(self, card):
        self.card = card

    @property
    def name(self):
        return f"Attack with {self.card.card_id} {self.card.name}"

    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        attack_event = kwargs.get("attack_event")
        return (
            self.card.is_attack() and
            (player.action_points.get("attack", 0) >= 1 or
             player.action_points.get("general", 0) >= 1)
        )

    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        game_engine = kwargs.get("game_engine")
        print(f"\nPlayer {player.id} is attempting an Attack Action with {self.card.name}.")
        
        # Select a valid target
        candidates = game_engine.get_attack_target(player)
        
        # Prompt player to select a target
        target = game_engine.interface.prompt_target_selection(candidates)
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        # Play the attack card
        player.hand.remove(self.card)
        
        attack_event = {
            'attack_type': "attack",
            'attacker': player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
            'can_not_counter': self.card.is_dark_extinction(),
        }
        game_engine.process_damage_timeline(attack_event, start_step=1)

        game_engine.deck.recycle([self.card])
        print(f"Player {player.id} plays {self.card.name} to attack Player {target.id}.")

        return True


class MagicAction(Action):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def available(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def on_action_success(self, *args, **kwargs):
        player = kwargs.get("player")
        if player.action_points["magic"] > 0:
            player.action_points["magic"] -= 1
        else:
            player.action_points["general"] -= 1

class MagicCardAction(MagicAction):
    def __init__(self, card):
        self.card = card

    @property
    def name(self):
        return f"Cast {self.card.card_id} {self.card.name}"

    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        return (
            (self.card.is_poison() or
             self.card.is_weakness() or
             self.card.is_holy_shield()) and
            (player.action_points.get("magic", 0) >= 1 or
             player.action_points.get("general", 0) >= 1)
        )

    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        game_engine = kwargs.get("game_engine")
        print(f"\nPlayer {player.id} is attempting a Magic Action with {self.card.name}.")
        
        # Select a valid target
        target = player.interface.prompt_target_selection(game_engine.players)
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        player.hand.remove(self.card)

        # Apply the magic effect based on the card type
        if self.card.is_poison():
            effect = PoisonEffect(source=player, target=target, card=self.card)
        elif self.card.is_weakness():
            effect = WeaknessEffect(source=player, target=target, card=self.card)
        elif self.card.is_holy_shield():
            effect = HolyShieldEffect(source=player, target=target, card=self.card)
        else:
            raise Exception("Invalid magic card.")
        
        effect.apply(target)
        print(f"Player {target.id} is affected by {self.card.name}.")
        
        return True

class MagicBulletCardAction(MagicAction):
    def __init__(self, card):
        self.card = card

    @property
    def name(self):
        return f"Cast {self.card.card_id} {self.card.name}"
    
    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        return (
            self.card.is_magic_bullet() and
            (player.action_points.get("magic", 0) >= 1 or
             player.action_points.get("general", 0) >= 1)
        )
    
    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        game_engine = kwargs.get("game_engine")
        print(f"\nPlayer {player.id} is attempting a Magic Bullet Action with {self.card.name}.")
        
        # Select a valid target
        target = game_engine.get_magic_bullet_target(player)
        
        # Play the magic bullet card
        player.hand.remove(self.card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
        }
        game_engine.process_damage_timeline(attack_event, start_step=1)

        game_engine.deck.recycle([self.card])
        print(f"Player {player.id} plays {self.card.name} to cast Magic Bullet on Player {target.id}.")
        
        return True


class SpecialAction(Action):
    @abstractmethod
    def available(self, *args, **kwargs):
        pass

    def on_action_success(self, *args, **kwargs):
        player = kwargs.get("player")
        if player.action_points["special"] > 0:
            player.action_points["special"] -= 1
        else:
            player.action_points["general"] -= 1

class SynthesisAction(SpecialAction):
    @property
    def name(self):
        return "Synthesize"

    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        return (player.can_draw_cards(3) and
               player.team.jewels.gem + player.team.jewels.crystal >= 3 and
                (player.action_points["general"] >= 1 or 
                 player.action_points["special"] >= 1))

    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        game_engine = kwargs.get("game_engine")
        # Check if team has at least 3 jewels
        total_jewels = player.team.jewels.gem + player.team.jewels.crystal
        if total_jewels < 3:
            print("Not enough jewels to perform 'Synthesize'. Action canceled.")
            return False

        # Check if player can draw three cards without exceeding hand size
        if not player.can_draw_cards(3):
            print(f"Cannot perform 'Synthesize' as drawing 3 cards would exceed hand size of {player.max_hand_size}. Action canceled.")
            return False

        # Draw three cards from the deck
        drawn_cards = player.deck.deal(3)
        if not drawn_cards:
            print("No cards drawn. Synthesize action ends.")
            return False

        player.receive_cards(drawn_cards)
        
        # Prompt the player to use jewels for synthesis
        while True:
            try:
                print(f"Current jewels: {player.team.jewels}")
                gems_to_use = int(input("Enter the number of Gems to use for Synthesis (0 to 3): "))
                crystals_to_use = 3 - gems_to_use
                if gems_to_use < 0 or gems_to_use > player.team.jewels.gem:
                    print(f"Invalid number of Gems. You have {player.team.jewels.gem} Gem(s).")
                    continue
                if crystals_to_use < 0 or crystals_to_use > player.team.jewels.crystal:
                    print(f"Not enough Crystals to use. You have {player.team.jewels.crystal} Crystal(s).")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter numeric values.")

        # Remove chosen jewels from the team
        removed = player.team.jewels.remove_jewel(gem_remove=gems_to_use, crystal_remove=crystals_to_use)
        if not removed:
            print("Failed to remove jewels. Action canceled.")
            return False

        # Perform synthesis: convert 3 jewels into 1 Grail
        player.team.add_grail(1)
        print(f"{player.team} synthesized 1 Grail. Current Grail: {player.team.grail}")

        # Opposing team loses 1 morale
        opposing_team = game_engine.get_opposite_team(player.team)
        opposing_team.add_morale(-1)
        print(f"{opposing_team} loses 1 morale due to Synthesis. Current Morale: {opposing_team.morale}")
        return True

class PurchaseAction(SpecialAction):
    @property
    def name(self):
        return "Purchase"

    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        return (player.can_draw_cards(3) and
                (player.action_points["general"] >= 1 or 
                 player.action_points["special"] >= 1))
        
    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        print(f"\nPlayer {player.id} is attempting a Purchase Action.")

        if not player.can_draw_cards(3):
            print(f"Cannot perform 'Purchase' as drawing 3 cards would exceed hand size of {player.max_hand_size}. Action canceled.")
            return False

        # Draw cards from the deck
        drawn_cards = player.deck.deal(3)
        if not drawn_cards:
            print("No cards drawn. Purchase action ends.")
            return False
        
        player.receive_cards(drawn_cards)
        
        # Check if team's jewels are already at maximum
        current_jewels = player.team.jewels.gem + player.team.jewels.crystal
        if current_jewels >= player.team.jewels.max_jewel:
            print(f"{player.team}'s jewels are already at maximum. Purchase completed without adding jewels.")
        elif current_jewels == player.team.jewels.max_jewel - 1:
            # If there's space for only one jewel, let the player choose
            while True:
                choice = input("You can add one jewel. Enter 'g' for Gem or 'c' for Crystal: ").lower().strip()
                if choice == 'g' and player.team.jewels.can_add(gem_add=1):
                    player.team.jewels.add_jewel(gem_add=1)
                    print(f"{player.team} gains 1 Gem from Purchase.")
                    break
                elif choice == 'c' and player.team.jewels.can_add(crystal_add=1):
                    player.team.jewels.add_jewel(crystal_add=1)
                    print(f"{player.team} gains 1 Crystal from Purchase.")
                    break
                else:
                    print("Invalid choice. Please try again.")
        else:
            # Add both Gem and Crystal if possible
            if player.team.jewels.can_add(gem_add=1, crystal_add=1):
                player.team.jewels.add_jewel(gem_add=1, crystal_add=1)
                print(f"{player.team} gains 1 Gem and 1 Crystal from Purchase.")
            else:
                print("Unexpected error in adding jewels. Purchase completed without adding jewels.")
        return True

class RefineAction(SpecialAction):
    @property
    def name(self):
        return "Refine"

    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        return (
            (player.action_points.get("general", 0) >= 1 or player.action_points.get("special", 0) >= 1) and
            (player.team.jewels.gem + player.team.jewels.crystal >= 1) and
            (player.jewels.gem + player.jewels.crystal < player.jewels.max_jewel)
        )

    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        print(f"\nPlayer {player.id} is attempting a Refine Action.")

        # Determine the number of jewels to transfer (1 or 2)
        available_jewels = player.team.jewels.gem + player.team.jewels.crystal
        player_available_space = player.jewels.max_jewel - (player.jewels.gem + player.jewels.crystal)
        if available_jewels == 0 or player_available_space == 0:
            print("No jewels available to refine or player's jewel capacity is full. Action canceled.")
            return False

        max_transfer = min(2, available_jewels, player_available_space)
        while True:
            try:
                # Display current jewels
                print(f"Team Jewels: Gems = {player.team.jewels.gem}, Crystals = {player.team.jewels.crystal}")

                num_to_transfer = int(input(f"How many jewels do you want to refine? (1 or {max_transfer}): ").strip())
                if num_to_transfer < 1 or num_to_transfer > max_transfer:
                    print(f"Invalid number. You can refine up to {max_transfer} jewel(s). Please try again.")
                    continue
                
                gems_to_transfer = int(input(f"Enter the number of Gems to transfer (0 to {min(num_to_transfer, player.team.jewels.gem)}): "))
                crystals_to_transfer = num_to_transfer - gems_to_transfer
                if gems_to_transfer < 0 or gems_to_transfer > player.team.jewels.gem:
                    print(f"Invalid number of Gems. You have {player.team.jewels.gem} Gem(s).")
                    continue
                if crystals_to_transfer < 0 or crystals_to_transfer > player.team.jewels.crystal:
                    print(f"Not enough Crystals to transfer. You have {player.team.jewels.crystal} Crystal(s).")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter numeric values.")

        # Remove chosen jewels from the team
        removed = player.team.jewels.remove_jewel(gem_remove=gems_to_transfer, crystal_remove=crystals_to_transfer)
        if not removed:
            print("Failed to remove jewels. Action canceled.")
            return False

        # Check if adding jewels would exceed player's jewel capacity
        if not player.jewels.can_add(gem_add=gems_to_transfer, crystal_add=crystals_to_transfer):
            print(f"Cannot transfer jewels as it would exceed your jewel capacity of {player.jewels.max_jewel}. Action canceled.")
            # Refund jewels to the team
            player.team.jewels.add_jewel(gem_add=gems_to_transfer, crystal_add=crystals_to_transfer)
            return False

        # Add jewels to the player's jewels
        player.jewels.add_jewel(gem_add=gems_to_transfer, crystal_add=crystals_to_transfer)
        print(f"Player {player.id} refined {num_to_transfer} jewel(s). Current Jewels: {player.jewels}")
        return True


class CounterAction(Action):
    @property
    def name(self):
        return "Counter"

    @abstractmethod
    def available(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def on_action_success(self, *args, **kwargs):
        raise Exception("Counter action should not be successful")
        
class CounterCardAction(CounterAction):
    def __init__(self, card):
        self.card = card

    @property
    def name(self):
        return f"Counter with {self.card.card_id} {self.card.name}"

    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        attack_event = kwargs.get("attack_event")
        # TODO: Check available target
        return (
            self.card.is_attack() and
            (attack_event['card'].element == self.card.element or 
            attack_event['card'].is_dark_extinction())
        )

    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        game_engine = kwargs.get("game_engine")
        attack_event = kwargs.get("attack_event")
        print(f"\nPlayer {player.id} is attempting a Counter Action with {self.card.name}.")
        
        # Select a valid target
        candidates = game_engine.get_attack_target(player, counter=True, attacker=attack_event['attacker'])
        if not candidates:
            raise Exception("No available opponents to counter. Action canceled.")
        
        # Prompt player to select a target
        target = game_engine.interface.prompt_target_selection(candidates)
        if not target:
            raise Exception("No valid target selected. Action canceled.")
        
        # Play the attack card
        player.hand.remove(self.card)
        
        attack_event = {
            'attack_type': "counter",
            'attacker': player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': 2,
            'can_not_counter': self.card.is_dark_extinction(),
        }
        game_engine.process_damage_timeline(attack_event, start_step=2)

        game_engine.deck.recycle([self.card])
        print(f"Player {player.id} plays {self.card.name} to counter Player {target.id}.")

        return True

class HolyLightCardAction(CounterAction):
    def __init__(self, card):
        self.card = card

    @property
    def name(self):
        return f"Holy Light"

    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        attack_event = kwargs.get("attack_event")
        return (
            self.card.is_holy_light()
        )

    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        game_engine = kwargs.get("game_engine")
        print(f"\nPlayer {player.id} uses Holy Light")
        
        player.hand.remove(self.card)
        game_engine.deck.recycle([self.card])
        
        return True

class MagicBulletCounterCardAction(CounterAction):
    def __init__(self, card):
        self.card = card

    @property
    def name(self):
        return f"Counter {self.card.card_id} {self.card.name}"
    
    def available(self, *args, **kwargs):
        player = kwargs.get("player")
        attack_event = kwargs.get("attack_event")
        return (
            self.card.is_magic_bullet() and
            attack_event['attack_type'] == "magic_bullet"
        )
    
    def execute(self, *args, **kwargs):
        player = kwargs.get("player")
        game_engine = kwargs.get("game_engine")
        attack_event = kwargs.get("attack_event")
        print(f"\nPlayer {player.id} is attempting a Magic Bullet Counter Action with {self.card.name}.")
        
        # Select a valid target
        target = game_engine.get_magic_bullet_target(player)
        
        # Play the magic bullet card
        player.hand.remove(self.card)

        attack_event = {
            'attack_type': "magic_bullet",
            'attacker': player, 
            'defender': target, 
            'card': self.card,
            'damage_amount': attack_event['damage_amount'] + 1,
        }
        game_engine.process_damage_timeline(attack_event, start_step=1)

        game_engine.deck.recycle([self.card])
        print(f"Player {player.id} plays {self.card.name} to counter Player {target.id}.")
        
        return True