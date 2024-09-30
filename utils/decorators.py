def subscribe(event_type, name=None):
    def decorator(func):
        func._subscribe_event = event_type
        func._subscribe_name = name if callable(name) else (lambda instance: name)
        return func
    return decorator
