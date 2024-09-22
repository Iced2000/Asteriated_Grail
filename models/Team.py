# models/Team.py

from .Jewel import AgrJewel

class Team:
    def __init__(self, is_red):
        self.is_red = is_red
        self.jewels = AgrJewel(maxJewel=5)
        self.morale = 15
        self.grail = 0
        self.players = []

    def add_player(self, player):
        self.players.append(player)
        print(f"Player {player.id} added to {'Red' if self.is_red else 'Blue'} Team.")

    def add_morale(self, amount):
        self.morale += amount
        action = "increased" if amount >= 0 else "decreased"
        print(f"{'Red' if self.is_red else 'Blue'} Team morale {action} by {abs(amount)}. Current morale: {self.morale}")
        return self.check_end()

    def add_grail(self, amount):
        self.grail += amount
        print(f"{'Red' if self.is_red else 'Blue'} Team grail increased by {amount}. Current grail: {self.grail}")
        return self.check_end()

    def check_end(self):
        if self.grail >= 5:
            print(f"{'Red' if self.is_red else 'Blue'} Team has synthesized 5 grails and wins the game!")
            return True
        if self.morale <= 0:
            print(f"{'Red' if self.is_red else 'Blue'} Team morale has dropped to {self.morale} and loses the game!")
            return True
        return False

    def has_won(self):
        return self.grail >= 5 or self.morale <= 0

    def __str__(self, current_player_id=None):
        """
        Returns a string containing the team's status.
        Optionally includes each player's public information or full hand based on current_player_id.
        """
        team_color = "Red" if self.is_red else "Blue"
        team_info = (f"{team_color} Team - Morale: {self.morale}, Grail: {self.grail}, Jewels: {self.jewels}\n"
                     f"Players:")
        for player in self.players:
            player_info = f"  {player.get_public_info()}"
            team_info += f"\n{player_info}"
        return team_info