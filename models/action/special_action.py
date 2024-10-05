# models/action/special_action.py

from abc import ABC, abstractmethod
from .base_action import BaseAction

class BaseSpecialAction(BaseAction):
    @abstractmethod
    def available(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass

    def on_action_success(self):
        self._player.remove_action_point("special")

class SynthesisAction(BaseSpecialAction):
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

class PurchaseAction(BaseSpecialAction):
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

class RefineAction(BaseSpecialAction):
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