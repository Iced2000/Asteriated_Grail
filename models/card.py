# models/card.py

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
    
    # element related
    def is_earth(self):
        return self._element == "earth"
    
    def is_wind(self):
        return self._element == "wind"
    
    def is_light(self):
        return self._element == "light"
    
    def is_fire(self):
        return self._element == "fire"
    
    def is_thunder(self):
        return self._element == "thunder"
    
    def is_water(self):
        return self._element == "water"
    
    # unique skill related
    def is_blood_knife(self):
        return self._unique_skill1 == "血影狂刀" or self._unique_skill2 == "血影狂刀"
    
    def is_blood_roar(self):
        return self._unique_skill1 == "血腥咆哮" or self._unique_skill2 == "血腥咆哮"

    def is_healing_light(self):
        return self._unique_skill1 == "治癒之光" or self._unique_skill2 == "治癒之光"

    def is_healing_art(self):
        return self._unique_skill1 == "治療術" or self._unique_skill2 == "治療術"

    def is_soul_gift(self):
        return self._unique_skill1 == "靈魂賜予" or self._unique_skill2 == "靈魂賜予"

    def is_soul_blast(self):
        return self._unique_skill1 == "靈魂震爆" or self._unique_skill2 == "靈魂震爆"

    def is_angel_wall(self):
        return self._unique_skill1 == "天使之牆" or self._unique_skill2 == "天使之牆"

    def is_power_blessing(self):
        return self._unique_skill1 == "威力賜福" or self._unique_skill2 == "威力賜福"

    def is_speed_blessing(self):
        return self._unique_skill1 == "迅捷賜福" or self._unique_skill2 == "迅捷賜福"

    def is_precise_shot(self):
        return self._unique_skill1 == "精准射擊" or self._unique_skill2 == "精准射擊"

    def is_flash_trap(self):
        return self._unique_skill1 == "閃光陷阱" or self._unique_skill2 == "閃光陷阱"

    def is_blood_cry(self):
        return self._unique_skill1 == "血之悲鳴" or self._unique_skill2 == "血之悲鳴"

    def is_meteor(self):
        return self._unique_skill1 == "隕石" or self._unique_skill2 == "隕石"

    def is_wind_blade(self):
        return self._unique_skill1 == "風刃" or self._unique_skill2 == "風刃"

    def is_fireball(self):
        return self._unique_skill1 == "火球" or self._unique_skill2 == "火球"

    def is_lightning(self):
        return self._unique_skill1 == "雷擊" or self._unique_skill2 == "雷擊"

    def is_freeze(self):
        return self._unique_skill1 == "冰凍" or self._unique_skill2 == "冰凍"
