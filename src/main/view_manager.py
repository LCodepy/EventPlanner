import time
from typing import Optional

import pygame.display

from src.events.event import Event, OpenViewEvent, CloseViewEvent, ResizeViewEvent, MouseReleaseEvent, MouseClickEvent, \
    MouseFocusChangedEvent, AddTaskEvent, AddCalendarEventEvent, MouseMotionEvent, EditTaskEvent, \
    EditCalendarEventEvent, ShowIndependentLabelEvent, HideIndependentLabelEvent, TimerEvent
from src.events.event_loop import EventLoop
from src.ui.colors import Colors
from src.ui.independent_label import IndependentLabel
from src.utils.animations import ChangeValuesAnimation
from src.views.calendar_view import CalendarView
from src.views.choose_month_view import ChooseMonthView
from src.views.event_list_view import EventListView
from src.views.options_view import OptionsView
from src.views.profile_view import ProfileView
from src.views.search_view import SearchView
from src.views.switch_accounts_view import SwitchAccountsView
from src.views.todo_list_view import TodoListView
from src.views.view import View


class ViewManager:

    def __init__(self, display: pygame.Surface, event_loop: EventLoop, top_bar_view: View, side_bar_view: View, main_view: View) -> None:
        self.display = display
        self.event_loop = event_loop
        self.top_bar_view = top_bar_view
        self.side_bar_view = side_bar_view
        self.main_view = main_view
        self.side_view: Optional[View] = None
        self.top_view: Optional[View] = None
        self.options_view: Optional[View] = None
        self.independent_label: Optional[IndependentLabel] = None

        self.side_view_classes = (ProfileView, SearchView, TodoListView, EventListView, )

        self.opened_top_view_last_frame = False

        self.screen_fog = pygame.Surface(
            (self.display.get_width(), self.display.get_height() - self.top_bar_view.height), pygame.SRCALPHA
        )
        self.screen_fog_animation = ChangeValuesAnimation("IncreaseScreenFog", self.event_loop, 0.4)

    def register_events(self, event: Event) -> bool:
        registered_events = False

        if isinstance(event, OpenViewEvent):
            registered_events = self.open_view(event)
        elif isinstance(event, CloseViewEvent):
            registered_events = self.close_view(event)
        elif isinstance(event, ResizeViewEvent):
            registered_events = self.resize_view(event)
        elif isinstance(event, ShowIndependentLabelEvent):
            self.independent_label = event.label
            registered_events = True
        elif isinstance(event, HideIndependentLabelEvent):
            self.independent_label = None
            registered_events = True

        if self.screen_fog_animation.register_event(event):
            registered_events = True

        if self.top_view and self.top_view.register_event(event):
            registered_events = True
            self.top_view.set_rendering(True)

        if self.top_bar_view and self.top_bar_view.register_event(event):
            self.top_bar_view.set_rendering(True)
            registered_events = True

        if (
                not self.opened_top_view_last_frame and
                not isinstance(event, (AddTaskEvent, AddCalendarEventEvent, EditTaskEvent, EditCalendarEventEvent))
        ):
            if self.top_view and isinstance(event, MouseClickEvent) and not self.top_view.is_focused(event) and not \
                    self.top_bar_view.is_focused(event):
                self.top_view = None
                self.screen_fog_animation.start([150], [0])
                return True
            elif self.top_view:
                return registered_events

        if isinstance(event, MouseClickEvent) and self.options_view and not self.options_view.is_focused(event):
            self.options_view = None
            registered_events = True

        if self.options_view is not None and self.options_view.register_event(event):
            self.options_view.set_rendering(True)
            for view in self.get_views():
                if view:
                    view.register_event(MouseFocusChangedEvent(time.time(), False))
            return True

        for view in self.get_views():
            if view and view.register_event(event):
                view.set_rendering(True)
                registered_events = True

        return registered_events

    def open_view(self, event: OpenViewEvent) -> bool:
        if event.is_popup:
            self.top_view = event.view
            self.screen_fog_animation.start([0], [150])
            self.opened_top_view_last_frame = True
            self.event_loop.enqueue_event(MouseFocusChangedEvent(time.time(), False))
        elif isinstance(event.view, (OptionsView, SwitchAccountsView, ChooseMonthView, )):
            self.options_view = event.view
        elif isinstance(event.view, self.side_view_classes):
            if self.side_view:
                self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.side_view))
                event.view.resize(width=self.side_view.width)
            side_bar_exists = self.side_view is not None
            event.view.x = self.side_bar_view.width
            event.view.y = self.top_bar_view.height
            self.side_view = event.view
            if self.side_bar_view.width + event.view.width + self.main_view.get_min_size()[0] > \
                    pygame.display.get_window_size()[0]:
                event.view.resize(width=self.side_view.get_min_size()[0])
            if not side_bar_exists:
                self.main_view.resize(
                    width=pygame.display.get_window_size()[0] - self.side_bar_view.width - event.view.width
                )
                self.main_view.x += event.view.width
        elif event.view is self.main_view.__class__ and self.side_view:
            self.side_view = None
            self.main_view.resize(width=pygame.display.get_window_size()[0] - self.side_bar_view.width)
            self.main_view.x = self.side_bar_view.width
        elif isinstance(event.view, CalendarView):
            w, h = self.main_view.width, self.main_view.height
            x = self.main_view.x
            self.main_view = event.view
            self.main_view.resize(w, h)
            self.main_view.x = x
        return True

    def close_view(self, event: CloseViewEvent) -> bool:
        event.view.on_delete()

        if event.view in self.get_views():
            self.delete_view(event.view)
            if isinstance(event.view, self.side_view_classes):
                self.main_view.resize(width=pygame.display.get_window_size()[0] - self.side_bar_view.width)
                self.main_view.x -= event.view.width
        elif event.view == self.top_view:
            self.top_view = None
            self.screen_fog_animation.start([150], [0])
        elif event.view == self.options_view:
            self.options_view = None
        return True

    def resize_view(self, event: ResizeViewEvent) -> bool:
        if isinstance(event.view, self.side_view_classes):
            main_view_width = max(self.main_view.get_min_size()[0],
                                  pygame.display.get_window_size()[0] - self.side_bar_view.width - event.width)
            event.view.resize(width=pygame.display.get_window_size()[0] - self.side_bar_view.width - main_view_width)
            self.main_view.resize(width=main_view_width)
            self.main_view.x = pygame.display.get_window_size()[0] - main_view_width
        return True

    def render(self, force_render: bool = False) -> None:
        for view in self.get_views():
            if view and (view.rendering or force_render):
                view.render()

        if self.screen_fog_animation.values:
            self.screen_fog.fill(Colors.BLACK)
            self.screen_fog.set_alpha(self.screen_fog_animation.values[0])
            self.display.blit(self.screen_fog, (0, self.top_bar_view.height))

        if self.top_view:
            self.top_view.render()

        if self.options_view:
            self.options_view.render()

        if self.independent_label:
            self.independent_label.render()

    def resize(self, window_size: (int, int)) -> None:
        self.top_bar_view.resize(width=window_size[0])

        self.side_bar_view.resize(height=window_size[1] - self.top_bar_view.height)
        if self.side_view:
            self.side_view.resize(height=window_size[1] - self.top_bar_view.height)

        if self.main_view:
            side_view_width = self.side_view.width if self.side_view else 0
            self.main_view.resize(
                width=window_size[0] - self.side_bar_view.width - side_view_width,
                height=window_size[1] - self.top_bar_view.height
            )

        if self.top_view:
            self.top_view.x = window_size[0] // 2 - self.top_view.width // 2
            self.top_view.y = window_size[1] // 2 - self.top_view.height // 2

        self.screen_fog = pygame.Surface(window_size, pygame.SRCALPHA)

    def reset_views(self) -> None:
        for view in self.get_views():
            if view:
                view.set_rendering(False)
        self.opened_top_view_last_frame = False

    def delete_view(self, view: View):
        view.on_delete()
        if view == self.main_view:
            self.main_view = None
        elif view == self.side_view:
            self.side_view = None
        elif view == self.top_view:
            self.top_view = None

    def get_views(self) -> list[View]:
        return [self.top_bar_view, self.side_bar_view, self.main_view, self.side_view]

    def get_min_size(self) -> (int, int):
        side_view_width = self.side_view.width if self.side_view else 130
        min_view_height = max(self.main_view.get_min_size()[1] if self.main_view else 0,
                              self.side_view.get_min_size()[1] if self.side_view else 0)
        return self.side_bar_view.get_min_size()[0] + side_view_width + self.main_view.get_min_size()[0], \
            self.top_bar_view.get_min_size()[1] + min_view_height
