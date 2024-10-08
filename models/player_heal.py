# models/player_heal.py

class PlayerHeal:
    def __init__(self, max_amount=2):
        self._max_amount = max_amount
        self._amount = 2

    def add(self, amount):
        self._amount = min(self._amount + amount, self._max_amount)

    def remove(self, amount):
        self._amount = max(self._amount - amount, 0)

    def get_amount(self):
        return self._amount
    
    def __str__(self):
        return f"{self._amount}/{self._max_amount}"

