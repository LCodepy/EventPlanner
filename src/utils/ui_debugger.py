_SHOW_UI_BOXES = False


class UIDebugger:

    box_color = (200, 0, 0)
    center_point_color = (200, 0, 0)

    @staticmethod
    def enable() -> None:
        global _SHOW_UI_BOXES
        _SHOW_UI_BOXES = True

    @staticmethod
    def disable() -> None:
        global _SHOW_UI_BOXES
        _SHOW_UI_BOXES = False

    @staticmethod
    def is_enabled() -> bool:
        return _SHOW_UI_BOXES
