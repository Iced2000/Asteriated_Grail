# models/Action.py

from abc import ABC, abstractmethod
from models.Effect import PoisonEffect, WeaknessEffect, HolyShieldEffect, MagicBulletEffect

class Action(ABC):
    @property
    @abstractmethod
    def name(self):
        """Returns the name of the action."""
        pass

    @abstractmethod
    def available(self, player):
        """Returns a dictionary of required action points for the action."""
        pass

    @abstractmethod
    def execute(self, player, game_engine):
        """
        Executes the action.
        Should return True if the action was successful, False otherwise.
        """
        pass

    @abstractmethod
    def post_process(self, player):
        """
        Handles post-processing after the action is executed.
        """
        pass

    def __str__(self):
        return self.name

class AttackAction(Action):
    @property
    @abstractmethod
    def name(self):
        pass
    
    @abstractmethod
    def available(self, player):
        pass

    @abstractmethod
    def execute(self, player, game_engine):
        pass

    def post_process(self, player):
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

    def available(self, player):
        return (
            self.card.is_attack() and
            (player.action_points.get("attack", 0) >= 1 or
             player.action_points.get("general", 0) >= 1)
        )

    def execute(self, player, game_engine):
        print(f"\nPlayer {player.id} is attempting an Attack Action with {self.card.name}.")
        
        # Select a valid target
        opponents = [p for p in game_engine.players if p.team != player.team and p.can_be_attacked]
        if not opponents:
            print("No available opponents to attack. Action canceled.")
            return False
        
        # Prompt player to select a target
        target = game_engine.interface.prompt_target_selection(opponents)
        if not target:
            print("No valid target selected. Action canceled.")
            return False
        
        # Play the attack card
        player.hand.remove(self.card)
        game_engine.deck.recycle([self.card])
        print(f"Player {player.id} plays {self.card.name} to attack Player {target.id}.")
        
        # # Emit attack event
        # game_engine.event_manager.emit(
        #     "attack",
        #     attacker=player,
        #     defender=target,
        #     card=self.card
        # )

        game_engine.execute_attack(attacker_id=player.id, defender_id=target.id, card=self.card)

        return True

class MagicAction(Action):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def available(self, player):
        pass

    @abstractmethod
    def execute(self, player, game_engine):
        pass

    def post_process(self, player):
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

    def available(self, player):
        return (
            (self.card.is_poison() or
             self.card.is_weakness() or
             self.card.is_holy_shield() or
             self.card.is_magic_bullet()) and
            (player.action_points.get("magic", 0) >= 1 or
             player.action_points.get("general", 0) >= 1)
        )

    def execute(self, player, game_engine):
        print(f"\nPlayer {player.id} is attempting a Magic Action with {self.card.name}.")
        
        # Select a valid target
        target = player.interface.prompt_target_selection(game_engine.players)
        if not target:
            print("No valid target selected. Action canceled.")
            return False
        
        # Apply the magic effect based on the card type
        if self.card.is_poison():
            effect = PoisonEffect(amount=1, duration=1)
        elif self.card.is_weakness():
            effect = WeaknessEffect(duration=1)
        elif self.card.is_holy_shield():
            effect = HolyShieldEffect()
        else:
            print("Invalid magic card.")
            return False
        
        effect.apply(target)
        print(f"Player {target.id} is affected by {self.card.name}.")
        
        # Play the magic card
        player.hand.remove(self.card)
        game_engine.deck.recycle([self.card])
        
        return True

class SpecialAction(Action):
    @abstractmethod
    def available(self, player):
        pass

    def post_process(self, player):
        if player.action_points["special"] > 0:
            player.action_points["special"] -= 1
        else:
            player.action_points["general"] -= 1

class SynthesisAction(SpecialAction):
    @property
    def name(self):
        return "Synthesize"

    def available(self, player):
        return (player.can_draw_cards(3) and
               player.team.jewels.gem + player.team.jewels.crystal >= 3 and
                (player.action_points["general"] >= 1 or 
                 player.action_points["special"] >= 1))

    def execute(self, player, game_engine):
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

    def available(self, player):
        return (player.can_draw_cards(3) and
                (player.action_points["general"] >= 1 or 
                 player.action_points["special"] >= 1))
        
    def execute(self, player, game_engine):
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

    def available(self, player):
        return (
            (player.action_points.get("general", 0) >= 1 or player.action_points.get("special", 0) >= 1) and
            (player.team.jewels.gem + player.team.jewels.crystal >= 1) and
            (player.jewels.gem + player.jewels.crystal < player.jewels.max_jewel)
        )

    def execute(self, player, game_engine):
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