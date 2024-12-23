import time

from src.controllers.todo_list_controller import TodoListController
from src.events.event import OpenViewEvent, CloseViewEvent, ShowIndependentLabelEvent, HideIndependentLabelEvent, \
    TimerEvent
from src.events.event_loop import EventLoop
from src.models.taskbar_model import TaskbarModel
from src.models.todo_list_model import TodoListModel
from src.ui.alignment import HorizontalAlignment
from src.ui.colors import Colors
from src.ui.independent_label import IndependentLabel
from src.ui.label import Label
from src.utils.assets import Assets
from src.views.calendar_view import CalendarView
from src.views.taskbar_view import TaskbarView
from src.views.todo_list_view import TodoListView
from src.views.view import View


class TaskbarController:

    def __init__(self, model: TaskbarModel, view: TaskbarView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.todo_list_opened = False
        self.todo_list_view = None
        self.showing_labels = False
        self.in_show_mode = False
        self.last_label_show_time = 0

        self.label_width = 110
        self.label_height = 26
        self.wait_duration = 0.8
        self.show_mode_exit_time = 0.4

        self.view.bind_on_close(self.on_close)

        self.view.profile_button.bind_on_enter(self.show_profile_label)
        self.view.profile_button.bind_on_exit(self.hide_label)

        self.view.calendar_view_button.bind_on_click(self.open_calendar_view)
        self.view.calendar_view_button.bind_on_enter(self.show_calendar_label)
        self.view.calendar_view_button.bind_on_exit(self.hide_label)

        self.view.todo_list_button.bind_on_click(self.open_todo_list)
        self.view.todo_list_button.bind_on_enter(self.show_todo_list_label)
        self.view.todo_list_button.bind_on_exit(self.hide_label)

        self.view.settings_button.bind_on_enter(self.show_settings_label)
        self.view.settings_button.bind_on_exit(self.hide_label)

    def open_todo_list(self) -> None:
        if self.todo_list_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.todo_list_view))
        else:
            model = TodoListModel()
            self.todo_list_view = TodoListView(
                self.view.display, model, self.event_loop, 300, self.view.display.get_height() - 30, 0, 0
            )
            TodoListController(model, self.todo_list_view, self.event_loop)
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), self.todo_list_view, False))

        self.todo_list_opened = not self.todo_list_opened
        self.hide_label()

    def open_calendar_view(self) -> None:
        if self.todo_list_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.todo_list_view))
        else:
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), CalendarView, False))
        self.hide_label()

    def on_close(self, view: View) -> None:
        if view == self.todo_list_view:
            self.todo_list_opened = False

    def hide_label(self) -> None:
        self.event_loop.enqueue_event(HideIndependentLabelEvent(time.time()))
        self.showing_labels = False
        self.last_label_show_time = time.time()

    def show_profile_label(self) -> None:
        if time.time() - self.last_label_show_time >= self.show_mode_exit_time:
            self.in_show_mode = False

        if not self.showing_labels and self.view.profile_button.hovering and not self.in_show_mode:
            self.event_loop.enqueue_event(TimerEvent(time.time(), self.wait_duration, self.show_profile_label))
            self.showing_labels = True
            return

        if not self.view.profile_button.hovering:
            return

        label = IndependentLabel(
            self.view.display,
            Label(
                text=self.view.language_manager.get_string("profile"), text_color=Colors.GREY140,
                font=Assets().font18, horizontal_text_alignment=HorizontalAlignment.LEFT
            ),
            self.label_width, self.label_height,
            self.view.width - 2,
            self.view.profile_button.get_rect().centery + 14,
        )
        self.event_loop.enqueue_event(ShowIndependentLabelEvent(time.time(), label))
        self.in_show_mode = True

    def show_calendar_label(self) -> None:
        if time.time() - self.last_label_show_time >= self.show_mode_exit_time:
            self.in_show_mode = False

        if not self.showing_labels and self.view.calendar_view_button.hovering and not self.in_show_mode:
            self.event_loop.enqueue_event(TimerEvent(time.time(), self.wait_duration, self.show_calendar_label))
            self.showing_labels = True
            return

        if not self.view.calendar_view_button.hovering:
            return

        label = IndependentLabel(
            self.view.display,
            Label(
                text=self.view.language_manager.get_string("calendar"), text_color=Colors.GREY140,
                font=Assets().font18, horizontal_text_alignment=HorizontalAlignment.LEFT
            ),
            self.label_width, self.label_height,
            self.view.width - 2,
            self.view.calendar_view_button.get_rect().centery + 14,
        )
        self.event_loop.enqueue_event(ShowIndependentLabelEvent(time.time(), label))
        self.in_show_mode = True

    def show_todo_list_label(self) -> None:
        if time.time() - self.last_label_show_time >= self.show_mode_exit_time:
            self.in_show_mode = False

        if not self.showing_labels and self.view.todo_list_button.hovering and not self.in_show_mode:
            self.event_loop.enqueue_event(TimerEvent(time.time(), self.wait_duration, self.show_todo_list_label))
            self.showing_labels = True
            return

        if not self.view.todo_list_button.hovering:
            return

        label = IndependentLabel(
            self.view.display,
            Label(
                text=self.view.language_manager.get_string("todo_list"), text_color=Colors.GREY140,
                font=Assets().font18, horizontal_text_alignment=HorizontalAlignment.LEFT
            ),
            self.label_width, self.label_height,
            self.view.width - 2,
            self.view.todo_list_button.get_rect().centery + 14,
        )
        self.event_loop.enqueue_event(ShowIndependentLabelEvent(time.time(), label))
        self.in_show_mode = True

    def show_settings_label(self) -> None:
        if time.time() - self.last_label_show_time >= self.show_mode_exit_time:
            self.in_show_mode = False

        if not self.showing_labels and self.view.settings_button.hovering and not self.in_show_mode:
            self.event_loop.enqueue_event(TimerEvent(time.time(), self.wait_duration, self.show_settings_label))
            self.showing_labels = True
            return

        if not self.view.settings_button.hovering:
            return

        label = IndependentLabel(
            self.view.display,
            Label(
                text=self.view.language_manager.get_string("settings"), text_color=Colors.GREY140,
                font=Assets().font18, horizontal_text_alignment=HorizontalAlignment.LEFT
            ),
            self.label_width, self.label_height,
            self.view.width - 2,
            self.view.settings_button.get_rect().centery + 14,
        )
        self.event_loop.enqueue_event(ShowIndependentLabelEvent(time.time(), label))
        self.in_show_mode = True
