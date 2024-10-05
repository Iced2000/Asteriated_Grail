# models/Card.py

class Card:
    def __init__(self, card_id, card_type, element, property_, name, unique_skill1=None, unique_skill2=None):
        self._card_id = int(card_id)
        self._card_type = card_type.lower()
        self._element = element.lower()
        self._property = property_.lower()
        self._name = name
        self._unique_skill1 = unique_skill1
        self._unique_skill2 = unique_skill2

    def __str__(self):
        return f"Card(ID: {self._card_id}, Type: {self._card_type}, Element: {self._element}, Property: {self._property}, Name: {self._name})"

    def get_card_id(self):
        return self._card_id
    
    def get_card_type(self):
        return self._card_type
    
    def get_element(self):
        return self._element
    
    def get_property(self):
        return self._property
    
    def get_name(self):
        return self._name
    
    # type related
    def is_attack(self):
        return self._card_type == "attack"

    def is_magic(self):
        return self._card_type == "magic"
    
    def is_poison(self):
        return self._name == "中毒"

    def is_weakness(self):
        return self._name == "虛弱"

    def is_holy_shield(self):
        return self._name == "聖盾"

    def is_magic_bullet(self):
        return self._name == "魔彈"

    def is_dark_extinction(self):
        return self._name == "暗滅"

    def is_holy_light(self):
        return self._name == "聖光"
    
    # Add more methods based on card functionalities as needed