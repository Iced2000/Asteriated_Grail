# models/PlayerHand.py

class PlayerHand:
    def __init__(self, player, max_size=6):
        self.player = player
        self.cards = []
        self.max_size = max_size

    def add_card(self, card):
        self.cards.append(card)
        self.handle_exploding_hand()
    
    def add_cards(self, cards):
        self.cards.extend(cards)
        self.handle_exploding_hand()

    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
        else:
            raise Exception(f"Card {card} not found in hand.")

    def get_cards(self):
        return self.cards

    def size(self):
        return len(self.cards)

    def is_full(self):
        return len(self.cards) >= self.max_size

    def clear(self):
        self.cards = []

    def show_hand(self):
        """
        Displays the player's current hand.
        """
        self.player.interface.send_message(f"\n--- Player {self.player.id}'s Hand ---", player_id=self.player.id)
        for idx, card in enumerate(self.get_cards()):
            self.player.interface.send_message(f"{idx}: {card}", player_id=self.player.id)
        self.player.interface.send_message("--------------------------\n", player_id=self.player.id)

    def handle_exploding_hand(self):
        if self.is_full():
            excess_cards = self.size() - self.max_size
            self.player.interface.send_message(f"Player {self.player.id} has exceeded the hand limit by {excess_cards} card(s). Must discard down to {self.max_size} cards.", player_id=self.player.id)

            discard_choice = self.player.interface.prompt_multiple_action_selection(self.get_cards(), min_selections=excess_cards, 
                                                                             max_selections=excess_cards, player_id=self.player.id)
            for card in discard_choice:
                self.remove_card(card)
                self.player.deck.recycle([card])
                self.player.team.add_morale(-1)

            self.player.interface.send_message(f"Player {self.player.id}'s hand size is now {self.size()}.", debug=True)

    def can_draw_cards(self, number):
        return (len(self.cards) + number) <= self.max_size
    
    def __str__(self):
        return f"Hand: {[str(card) for card in self.cards]}"