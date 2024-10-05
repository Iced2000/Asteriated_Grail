# factories/character_factory.py

from models.characters import BasePlayer
# from models.characters.warrior import Warrior
# from models.characters.mage import Mage

class CharacterFactory:
    @staticmethod
    def create_character(character_config):
        character_type = character_config['character_type']
        if character_type == "BasePlayer":
            return BasePlayer(character_config)
        else:
            raise ValueError(f"Unknown character type: {character_type}")