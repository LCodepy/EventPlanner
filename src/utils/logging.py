from colorama import Fore, init


init(autoreset=True)
_LOGGING_ENABLED = False


class Log:

    @staticmethod
    def enable() -> None:
        global _LOGGING_ENABLED
        _LOGGING_ENABLED = True

    @staticmethod
    def disable() -> None:
        global _LOGGING_ENABLED
        _LOGGING_ENABLED = False

    @staticmethod
    def i(text: str) -> None:
        if not _LOGGING_ENABLED:
            return
        print(Fore.BLUE + "LOG\\INFO: " + text)

    @staticmethod
    def e(text: str) -> None:
        if not _LOGGING_ENABLED:
            return
        print(Fore.RED + "LOG\\ERROR: " + text)
