# game_engine/event_manager.py

from collections import defaultdict
from timeline import GameTimeline, DamageTimeline

class Event:
    def __init__(self, event_type, **data):
        self.type = event_type
        self.data = data

class EventHandler:
    def __init__(self, callback, priority=0):
        self.callback = callback
        self.priority = priority

    def handle(self, event):
        return self.callback(event)

class EventManager:
    def __init__(self, console_interface):
        self.interface = console_interface
        self.handlers = defaultdict(list)
        self.initialize_timelines()

    def initialize_timelines(self):
        for event_type in GameTimeline.keys():
            self.handlers[event_type] = []
        for event_type in DamageTimeline.keys():
            self.handlers[event_type] = []

    def subscribe(self, event_type, listener, priority=0, name=None):
        if event_type not in self.handlers:
            raise ValueError(f"Event type '{event_type}' is not in the game or damage timeline.")
        listener_name = name if name else listener.__name__
        handler = EventHandler(listener, priority)
        self.handlers[event_type].append((listener_name, handler))
        self.sort_handlers(event_type)
        self.interface.send_message(f"Listener '{listener_name}' subscribed to {event_type} with priority {priority}.", debug=True)

    def sort_handlers(self, event_type):
        self.handlers[event_type].sort(key=lambda x: x[1].priority)

    def emit(self, event_type, **kwargs):
        event = Event(event_type, **kwargs)
        handlers = self.handlers.get(event_type, [])
        self.interface.send_message(f"Emitting event '{event_type}' to {len(handlers)} handler(s).", debug=True)
        all_successful = True
        for listener_name, handler in handlers:
            result = handler.handle(event)
            if result is False:
                self.interface.send_message(f"Handler {listener_name} returned False for event '{event_type}'.", debug=True)
                all_successful = False
                break
        return all_successful