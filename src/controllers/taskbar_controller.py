import time
from typing import Callable

from src.controllers.profile_controller import ProfileController
from src.controllers.search_controller import SearchController
from src.controllers.todo_list_controller import TodoListController
from src.events.event import OpenViewEvent, CloseViewEvent, ShowIndependentLabelEvent, HideIndependentLabelEvent, \
    TimerEvent
from src.events.event_loop import EventLoop
from src.models.calendar_model import CalendarModel
from src.models.taskbar_model import TaskbarModel
from src.models.todo_list_model import TodoListModel
from src.ui.alignment import HorizontalAlignment
from src.ui.button import Button
from src.ui.colors import Colors
from src.ui.independent_label import IndependentLabel
from src.ui.label import Label
from src.utils.assets import Assets
from src.views.calendar_view import CalendarView
from src.views.profile_view import ProfileView
from src.views.search_view import SearchView
from src.views.taskbar_view import TaskbarView
from src.views.todo_list_view import TodoListView
from src.views.view import View


class TaskbarController:

    def __init__(self, model: TaskbarModel, view: TaskbarView, event_loop: EventLoop) -> None:
        self.model = model
        self.view = view
        self.event_loop = event_loop

        self.todo_list_opened = False
        self.search_opened = False
        self.profile_opened = False
        self.todo_list_view = None
        self.search_view = None
        self.profile_view = None

        self.showing_labels = False
        self.in_show_mode = False
        self.last_label_show_time = 0

        self.label_width = 110
        self.label_height = 26
        self.wait_duration = 0.8
        self.show_mode_exit_time = 0.4

        self.view.bind_on_close(self.on_close)

        self.view.profile_button.bind_on_click(self.open_profile_view)
        self.view.profile_button.bind_on_enter(self.show_profile_label)
        self.view.profile_button.bind_on_exit(self.hide_label)

        self.view.search_button.bind_on_click(self.open_search_view)
        self.view.search_button.bind_on_enter(self.show_search_label)
        self.view.search_button.bind_on_exit(self.hide_label)

        self.view.calendar_view_button.bind_on_click(self.open_calendar_view)
        self.view.calendar_view_button.bind_on_enter(self.show_calendar_label)
        self.view.calendar_view_button.bind_on_exit(self.hide_label)

        self.view.todo_list_button.bind_on_click(self.open_todo_list)
        self.view.todo_list_button.bind_on_enter(self.show_todo_list_label)
        self.view.todo_list_button.bind_on_exit(self.hide_label)

        self.view.settings_button.bind_on_enter(self.show_settings_label)
        self.view.settings_button.bind_on_exit(self.hide_label)

    def open_profile_view(self) -> None:
        if self.profile_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.profile_view))
        else:
            self.profile_view = ProfileView(
                self.view.display, self.event_loop, 300, self.view.display.get_height() - 30, 0, 0
            )
            ProfileController(self.profile_view, self.event_loop)
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), self.profile_view, False))

        self.profile_opened = not self.profile_opened
        self.hide_label()

    def open_search_view(self) -> None:
        if self.search_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.search_view))
        else:
            model = CalendarModel()
            self.search_view = SearchView(
                self.view.display, model, self.event_loop, 300, self.view.display.get_height() - 30, 0, 0
            )
            SearchController(model, self.search_view, self.event_loop)
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), self.search_view, False))

        self.search_opened = not self.search_opened
        self.hide_label()

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
        elif self.search_opened:
            self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.search_view))
        else:
            self.event_loop.enqueue_event(OpenViewEvent(time.time(), CalendarView, False))
        self.hide_label()

    def on_close(self, view: View) -> None:
        if view == self.todo_list_view:
            self.todo_list_opened = False
        elif view == self.search_view:
            self.search_opened = False
        elif view == self.profile_view:
            self.profile_opened = False

    def hide_label(self) -> None:
        self.event_loop.enqueue_event(HideIndependentLabelEvent(time.time()))
        self.showing_labels = False
        self.last_label_show_time = time.time()

    def show_label(self, button: Button, fn: Callable, text: str) -> None:
        if time.time() - self.last_label_show_time >= self.show_mode_exit_time:
            self.in_show_mode = False

        if not self.showing_labels and button.hovering and not self.in_show_mode:
            self.event_loop.enqueue_event(TimerEvent(time.time(), self.wait_duration, fn))
            self.showing_labels = True
            return

        if not button.hovering:
            return

        label = IndependentLabel(
            self.view.display,
            Label(
                text=text, text_color=Colors.GREY140,
                font=Assets().font18, horizontal_text_alignment=HorizontalAlignment.LEFT
            ),
            self.label_width, self.label_height,
            self.view.width - 2,
            button.get_rect().centery + 14,
        )
        self.event_loop.enqueue_event(ShowIndependentLabelEvent(time.time(), label))
        self.in_show_mode = True

    def show_profile_label(self) -> None:
        self.show_label(
            self.view.profile_button, self.show_profile_label, self.view.language_manager.get_string("profile")
        )

    def show_search_label(self) -> None:
        self.show_label(
            self.view.search_button, self.show_search_label, self.view.language_manager.get_string("search")
        )

    def show_calendar_label(self) -> None:
        self.show_label(
            self.view.calendar_view_button, self.show_calendar_label, self.view.language_manager.get_string("calendar")
        )

    def show_todo_list_label(self) -> None:
        self.show_label(
            self.view.todo_list_button, self.show_todo_list_label, self.view.language_manager.get_string("todo_list")
        )

    def show_settings_label(self) -> None:
        self.show_label(
            self.view.settings_button, self.show_settings_label, self.view.language_manager.get_string("settings")
        )
