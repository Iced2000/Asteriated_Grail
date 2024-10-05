# models/player_hand.py

class PlayerHand:
    def __init__(self, max_size=6):
        self._cards = []
        self._max_size = max_size
    
    def add_cards(self, cards):
        self._cards.extend(cards)
        return self.exploded()

    def remove_cards(self, cards):
        for card in cards:
            if card in self._cards:
                self._cards.remove(card)
            else:
                raise Exception(f"Card {card} not found in hand.")

    def size(self):
        return len(self._cards)
    
    def get_max_size(self):
        return self._max_size

    def is_full(self):
        return len(self._cards) == self._max_size
    
    def exploded(self):
        return len(self._cards) > self._max_size

    def clear(self):
        self._cards = []

    def can_draw_cards(self, number):
        return (len(self._cards) + number) <= self._max_size
    
    def __str__(self):
        return f"{len(self._cards)}/{self._max_size}"
    
    def get_cards(self):
        return self._cards