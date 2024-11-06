from src.events.event import Event


class EventQueue:

    def __init__(self) -> None:
        self.queue = []

    def add(self, event: Event) -> None:
        self.queue.append(event)

    def get(self) -> Event:
        if not self.queue:
            raise StopIteration()
        event = self.queue[0]
        self.queue = self.queue[1:]
        return event

    def clear(self) -> None:
        self.queue.clear()

    def is_empty(self) -> bool:
        return bool(self.queue)

