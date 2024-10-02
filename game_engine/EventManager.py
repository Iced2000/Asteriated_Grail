# game_engine/EventManager.py
from timeline.damage_timeline import DamageTimeline
from timeline.game_timeline import GameTimeline

class EventManager:
    def __init__(self, console_interface):
        self.interface = console_interface
        self.listeners = {}
        for event_type in GameTimeline.keys():
            self.listeners[event_type] = []
        for event_type in DamageTimeline.keys():
            self.listeners[event_type] = []
    
    def subscribe(self, event_type, listener, name=None):
        """
        Subscribes a listener (function) to a specific event type.
        
        :param event_type: The type of event to listen for.
        :param listener: The function to call when the event is emitted.
        :param name: Optional name for the listener. If not provided, the function's __name__ is used.
        """
        if event_type not in self.listeners:
            raise ValueError(f"Event type '{event_type}' is not in the game or damage timeline.")
        listener_name = name if name else listener.__name__
        self.listeners[event_type].append((listener_name, listener))
        self.interface.send_message(f"Listener '{listener_name}' subscribed to {event_type}.", debug=True)
    
    def emit(self, event_type, **kwargs):
        """
        Emits an event, calling all subscribed listeners with provided keyword arguments.
        If any listener returns False, continue processing but return False at the end.
        
        :param event_type: The type of event to emit.
        :param kwargs: Additional data to pass to listeners.
        :return: True if all listeners processed successfully, False if any listener returned False.
        """
        listeners = self.listeners.get(event_type, [])
        self.interface.send_message(f"Emitting event '{event_type}' to {len(listeners)} listener(s).", debug=True)
        all_successful = True
        for listener_name, listener in listeners:
            result = listener(**kwargs)
            if result is False:
                self.interface.send_message(f"Listener {listener_name} returned False for event '{event_type}'.", debug=True)
                all_successful = False
        return all_successful
    
    def sort_listeners(self):
        """
        Sorts all listeners for each event type based on the order defined in the timelines.
        Listeners not in the order list are placed at the back.
        """
        for event_type in self.listeners.keys():
            if event_type not in GameTimeline and event_type not in DamageTimeline:
                raise ValueError(f"Event type '{event_type}' is not in the game or damage timeline.")
            
            if event_type in GameTimeline:
                order = GameTimeline[event_type]
            elif event_type in DamageTimeline:
                order = DamageTimeline[event_type]
            
            listener_dict = {name: listener for name, listener in self.listeners[event_type]}
            sorted_listeners = [(name, listener_dict[name]) for name in order if name in listener_dict]
            remaining_listeners = [(name, listener) for name, listener in listener_dict.items() if name not in order]
            self.listeners[event_type] = sorted_listeners + remaining_listeners
            self.interface.send_message(f"Listeners for {event_type} sorted in the given order.", debug=True)

"""
# Define some example listeners
def listener1(**kwargs):
    self.interface.send_message("Listener 1 executed")

def listener2(**kwargs):
    self.interface.send_message("Listener 2 executed")

def listener3(**kwargs):
    self.interface.send_message("Listener 3 executed")

# Subscribe listeners
event_manager = EventManager()
event_manager.subscribe("attack", listener1, "listener1")
event_manager.subscribe("attack", listener2, "listener2")
event_manager.subscribe("attack", listener3, "listener3")

# Sort all listeners
event_manager.sort_listeners()
"""