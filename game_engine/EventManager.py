# game_engine/EventManager.py

class EventManager:
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, event_type, listener):
        """
        Subscribes a listener (function) to a specific event type.
        
        :param event_type: The type of event to listen for.
        :param listener: The function to call when the event is emitted.
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)
        print(f"Listener subscribed to {event_type}.")

    def emit(self, event_type, **kwargs):
        """
        Emits an event, calling all subscribed listeners with provided keyword arguments.
        
        :param event_type: The type of event to emit.
        :param kwargs: Additional data to pass to listeners.
        """
        listeners = self.listeners.get(event_type, [])
        print(f"Emitting event '{event_type}' to {len(listeners)} listener(s).")
        for listener in listeners:
            listener(**kwargs)