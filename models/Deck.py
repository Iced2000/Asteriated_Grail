# models/deck.py

import random
from models import Card

class Deck:
    def __init__(self, card_file_path, interface):
        self.interface = interface
        self.cards = self.load_cards(card_file_path)
        self.discards = []
        self.shuffle()

    def load_cards(self, path):
        cards = []
        try:
            with open(path, 'r', encoding="UTF-8") as file:
                for line in file:
                    parts = line.strip().split(' ')
                    if len(parts) >= 5:
                        card = Card(
                            card_id=parts[0],
                            card_type=parts[1],
                            element=parts[2],
                            property_=parts[3],
                            name=parts[4],
                            unique_skill1=parts[5] if len(parts) > 5 else None,
                            unique_skill2=parts[6] if len(parts) > 6 else None
                        )
                        cards.append(card)
            self.interface.send_message(f"Loaded {len(cards)} cards into the deck.", debug=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"Card file {path} not found.")
        return cards

    def shuffle(self):
        random.shuffle(self.cards)
        self.interface.send_message("Deck shuffled.", debug=True)

    def deal(self, num):
        dealt_cards = []
        for _ in range(num):
            if not self.cards:
                self.reset_deck()
            if self.cards:
                dealt_cards.append(self.cards.pop())
        self.interface.send_message(f"Dealt {len(dealt_cards)} card(s).", debug=True)
        return dealt_cards

    def recycle(self, cards):
        self.discards.extend(cards)
        self.interface.send_message(f"Recycled {len(cards)} card(s) into discards.", debug=True)

    def reset_deck(self):
        if self.discards:
            self.cards = self.discards.copy()
            self.discards = []
            self.shuffle()
            self.interface.send_message("Deck reset from discards.", debug=True)
        else:
            self.interface.send_message("No cards to reset the deck.", debug=True)

    def __str__(self):
        return f"Deck has {len(self.cards)} card(s)."