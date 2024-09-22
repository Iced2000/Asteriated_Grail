# models/Card.py

class Card:
    def __init__(self, card_id, card_type, element, property_, name, unique_skill1=None, unique_skill2=None):
        self.card_id = int(card_id)
        self.card_type = card_type.lower()
        self.element = element.lower()
        self.property = property_.lower()
        self.name = name
        self.unique_skill1 = unique_skill1
        self.unique_skill2 = unique_skill2

    def __str__(self):
        return f"Card(ID: {self.card_id}, Type: {self.card_type}, Element: {self.element}, Property: {self.property}, Name: {self.name})"

    def is_attack(self):
        return self.card_type == "attack"

    def is_magic(self):
        return self.card_type == "magic"
    
    def is_poison(self):
        return self.name == "中毒"

    def is_weakness(self):
        return self.name == "虛弱"

    def is_holy_shield(self):
        return self.name == "聖盾"

    def is_magic_bullet(self):
        return self.name == "魔彈"

    def is_dark_extinction(self):
        return self.name == "暗滅"

    def is_holy_light(self):
        return self.name == "聖光"
    
    # Add more methods based on card functionalities as needed