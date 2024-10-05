# models/effect/base_effect.py

from abc import ABC, abstractmethod

class BaseEffect(ABC):
    def __init__(self, source, target, game_engine):
        self._source = source
        self._target = target
        self._game_engine = game_engine
        self._interface = game_engine.get_interface()

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def __str__(self):
        return "Effect"