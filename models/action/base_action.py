# models/action/base_action.py

from abc import ABC, abstractmethod

class BaseAction(ABC):
    def __init__(self, player, game_engine):
        self._player = player
        self._game_engine = game_engine
        self._interface = game_engine.get_interface()

    @property
    @abstractmethod
    def name(self):
        """Returns the name of the action."""
        pass

    @abstractmethod
    def available(self):
        """Returns a boolean indicating if the action is available."""
        pass

    @abstractmethod
    def execute(self):
        """
        Executes the action.
        Should return True if the action was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def on_action_success(self):
        """
        Handles post-processing after the action is executed.
        """
        pass

    def is_no_response(self):
        """
        Returns True if the action is a no response action, False otherwise.
        """
        return False

    def __str__(self):
        return self.name

class NoResponseAction(BaseAction):
    @property
    def name(self):
        return f"No Response"

    def available(self):
        return True

    def execute(self):
        raise Exception("No response action should not be executed")

    def on_action_success(self):
        raise Exception("No response action should not be successful")
    
    def is_no_response(self):
        return True