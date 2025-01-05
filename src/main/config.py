class Config:

    @property
    def window_width(self) -> int:
        return 1200

    @property
    def window_height(self) -> int:
        return 830

    @property
    def window_size(self) -> (int, int):
        return self.window_width, self.window_height

    @property
    def window_title(self) -> str:
        return "Event Planner"

    @property
    def fps(self) -> int:
        return 60

    @property
    def time_zone(self) -> str:
        return "Europe/Belgrade"
