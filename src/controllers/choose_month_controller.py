import time

from src.events.event import ChangeMonthEvent, CloseViewEvent
from src.events.event_loop import EventLoop
from src.views.choose_month_view import ChooseMonthView


class ChooseMonthController:

    def __init__(self, view: ChooseMonthView, event_loop: EventLoop) -> None:
        self.view = view
        self.event_loop = event_loop

        self.view.bind_on_create_buttons(self.bind_buttons)
        self.bind_buttons()

    def bind_buttons(self) -> None:
        for i, btn in enumerate(self.view.buttons):
            btn.bind_on_click(lambda m=i: self.change_month(m+1))

    def change_month(self, m: int) -> None:
        self.event_loop.enqueue_event(ChangeMonthEvent(time.time(), m))
        self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.view))
