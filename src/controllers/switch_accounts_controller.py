import time
from threading import Thread

from src.events.event import UserSignInEvent, CloseViewEvent
from src.events.event_loop import EventLoop
from src.main.account_manager import AccountManager
from src.views.switch_accounts_view import SwitchAccountsView


class SwitchAccountsController:

    def __init__(self, view: SwitchAccountsView, event_loop: EventLoop) -> None:
        self.view = view
        self.event_loop = event_loop

        self.view.add_account_button.bind_on_click(self.on_add_account)
        self.view.bind_on_create_accounts(self.bind_accounts)
        self.bind_accounts()

    def on_add_account(self) -> None:
        AccountManager().sing_in_new_user()
        self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.view))

    def on_account_click(self, email: str) -> None:
        AccountManager().sign_in_user(email)
        self.event_loop.enqueue_event(CloseViewEvent(time.time(), self.view))

    def bind_accounts(self) -> None:
        for acc in self.view.accounts:
            acc.button.bind_on_click(lambda email=acc.user.email: self.on_account_click(email))
