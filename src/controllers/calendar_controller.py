from src.models.calendar_model import CalendarModel
from src.views.calendar_view import CalendarView


class CalendarController:

    def __init__(self, model: CalendarModel, view: CalendarView) -> None:
        self.model = model
        self.view = view
