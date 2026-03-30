from colorsys import hsv_to_rgb
from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.events import Resize
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Static

LOGO_PATH = Path(__file__).resolve().parent / "mind_shuffle_logo.txt"
HOME_LOGO_HORIZONTAL_PADDING = 4
HOME_LOGO_ANIMATION_STEP = 0.03
HOME_LOGO_ANIMATION_INTERVAL = 0.08


class HomeView(Widget):
    """Home che mostra il logo ASCII con dimensione statica."""

    def __init__(self) -> None:
        super().__init__()
        self.logo_text = LOGO_PATH.read_text(encoding="utf-8").rstrip("\n")
        self._color_phase = 0.0
        self._animation_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Static("", id="home_logo")

    def on_mount(self) -> None:
        self._refresh_logo()
        self._animation_timer = self.set_interval(
            HOME_LOGO_ANIMATION_INTERVAL,
            self._advance_logo_colors,
        )

    def on_resize(self, _: Resize) -> None:
        self._refresh_logo()

    def _refresh_logo(self) -> None:
        logo = self.query_one("#home_logo", Static)
        padding = " " * HOME_LOGO_HORIZONTAL_PADDING
        padded_logo = [
            f"{padding}{line}{padding}" for line in self.logo_text.splitlines()
        ]
        available_width = max(self.size.width - 2, 1)
        centered_lines = [line.center(available_width) for line in padded_logo]
        available_height = max(self.size.height, 1)
        top_padding = max((available_height - len(centered_lines)) // 2, 0)
        centered_logo = ([""] * top_padding) + centered_lines
        logo.update(self._build_rainbow_text(centered_logo))

    def _advance_logo_colors(self) -> None:
        self._color_phase = (self._color_phase + HOME_LOGO_ANIMATION_STEP) % 1.0
        self._refresh_logo()

    def _build_rainbow_text(self, lines: list[str]) -> Text:
        rainbow = Text()
        visible_chars = 0
        for row_index, line in enumerate(lines):
            for char in line:
                if char.strip():
                    hue = (self._color_phase + visible_chars * 0.01) % 1.0
                    red, green, blue = hsv_to_rgb(hue, 0.8, 1.0)
                    style = f"bold rgb({int(red * 255)},{int(green * 255)},{int(blue * 255)})"
                    rainbow.append(char, style=style)
                    visible_chars += 1
                else:
                    rainbow.append(char)
            if row_index < len(lines) - 1:
                rainbow.append("\n")
        return rainbow
