# models/Team.py

from .Jewel import AgrJewel

class Team:
    def __init__(self, is_red, game_engine):
        self._is_red = is_red
        self._game_engine = game_engine
        self._interface = game_engine.get_interface()
        self._event_manager = game_engine.get_event_manager()
        self._jewels = AgrJewel(maxJewel=5)
        self._morale = 15
        self._grail = 0
        self._players = []

    def add_player(self, player):
        self._interface.send_message(f"Player {player.get_id()} added to {'Red' if self._is_red else 'Blue'} Team.", debug=True)
        self._players.append(player)

    def add_morale(self, amount):
        self._morale += amount
        action = "increased" if amount >= 0 else "decreased"
        self._interface.send_message(f"{'Red' if self._is_red else 'Blue'} Team morale {action} by {abs(amount)}. Current morale: {self._morale}", broadcast=True)
        self._check_end()

    def add_grail(self, amount):
        self._grail += amount
        self._interface.send_message(f"{'Red' if self._is_red else 'Blue'} Team grail increased by {amount}. Current grail: {self._grail}", broadcast=True)
        self._check_end()

    def _check_end(self):
        if self._grail >= 5:
            self._interface.send_message(f"{'Red' if self._is_red else 'Blue'} Team has synthesized 5 grails and wins the game!", broadcast=True)
            self._game_engine.end_game(self._is_red)
        if self._morale <= 0:
            self._interface.send_message(f"{'Red' if self._is_red else 'Blue'} Team morale has dropped to {self._morale} and loses the game!", broadcast=True)
            self._game_engine.end_game(not self._is_red)
    
    def add_jewel(self, gem_add=0, crystal_add=0):
        self._interface.send_message(f"{'Red' if self._is_red else 'Blue'} Team added {gem_add} gem(s) and {crystal_add} crystal(s).", debug=True)
        self._jewels.add_jewel(gem_add, crystal_add)
    
    def remove_jewel(self, gem_remove=0, crystal_remove=0):
        self._interface.send_message(f"{'Red' if self._is_red else 'Blue'} Team removed {gem_remove} gem(s) and {crystal_remove} crystal(s).", debug=True)
        self._jewels.remove_jewel(gem_remove, crystal_remove)

    def is_red(self):
        return self._is_red
    
    def get_opposite_team(self):
        return self._game_engine.get_opposite_team(self)

    def __str__(self):
        team_color = "Red" if self._is_red else "Blue"
        team_info = (f"{team_color} Team - Morale: {self._morale}, Grail: {self._grail}, Jewels(G/C): {self._jewels}\n"
                     f"Players:")
        for player in self._players:
            player_info = f"  {player.get_public_info()}"
            team_info += f"\n{player_info}"
        return team_info
    
    def total_jewels(self):
        return self._jewels.total_jewels()
    
    def can_remove_jewel(self, gem_remove=0, crystal_remove=0):
        return self._jewels.can_remove(gem_remove, crystal_remove)
    
    def can_add_jewel(self, gem_add=0, crystal_add=0):
        return self._jewels.can_add(gem_add, crystal_add)
    
    def can_synthesis(self):
        return self._jewels.total_jewels() >= 3
    
    def can_refine(self):
        return self._jewels.total_jewels() >= 1
    
    def get_synthesis_jewel_combination(self):
        return self._jewels.get_jewel_combination(min_num=3, max_num=3)
    
    def get_refine_jewel_combination(self):
        return self._jewels.get_jewel_combination(min_num=1, max_num=2)
