from src.models.calendar_model import CalendarModel
from src.views.calendar_view import CalendarView


class CalendarController:

    def __init__(self, model: CalendarModel, view: CalendarView) -> None:
        self.model = model
        self.view = view

        self.view.previous_month_button.bind_on_click(self.change_to_previous_month)
        self.view.next_month_button.bind_on_click(self.change_to_next_month)

    def change_to_previous_month(self) -> None:
        self.view.month -= 1
        if self.view.month < 1:
            self.view.month = 12
            self.view.year -= 1

        self.view.create_weekday_labels()
        self.view.create_day_buttons()

        self.view.month_label.set_text(self.view.get_month_name(self.view.month).upper())
        self.view.year_label.set_text(str(self.view.year))

    def change_to_next_month(self) -> None:
        self.view.month += 1
        if self.view.month > 12:
            self.view.month = 1
            self.view.year += 1

        self.view.create_weekday_labels()
        self.view.create_day_buttons()

        self.view.month_label.set_text(self.view.get_month_name(self.view.month).upper())
        self.view.year_label.set_text(str(self.view.year))
