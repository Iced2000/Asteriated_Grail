# models/Deck.py

import random
from .Card import Card

class Deck:
    def __init__(self, card_file_path):
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
            print(f"Loaded {len(cards)} cards into the deck.")
        except FileNotFoundError:
            print(f"Card file {path} not found.")
        return cards

    def shuffle(self):
        random.shuffle(self.cards)
        print("Deck shuffled.")

    def deal(self, num):
        dealt_cards = []
        for _ in range(num):
            if not self.cards:
                self.reset_deck()
            if self.cards:
                dealt_cards.append(self.cards.pop())
        print(f"Dealt {len(dealt_cards)} card(s).")
        return dealt_cards

    def recycle(self, cards):
        self.discards.extend(cards)
        print(f"Recycled {len(cards)} card(s) into discards.")

    def reset_deck(self):
        if self.discards:
            self.cards = self.discards.copy()
            self.discards = []
            self.shuffle()
            print("Deck reset from discards.")
        else:
            print("No cards to reset the deck.")

    def __str__(self):
        return f"Deck has {len(self.cards)} card(s)."