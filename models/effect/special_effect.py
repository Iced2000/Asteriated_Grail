# models/effect/special_effect.py

from abc import ABC, abstractmethod
from .base_effect import BaseEffect

class SpecialEffect(BaseEffect):
    @abstractmethod
    def apply(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def __str__(self):
        return "SpecialEffect"