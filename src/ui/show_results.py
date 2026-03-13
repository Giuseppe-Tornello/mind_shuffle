from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Label, Static

from src.ui import ui_constants


class ShowResults(Widget):
    """Summary screen shown at the end of a session."""

    class GoHome(Message):
        """Request navigation back to the home screen."""

    def __init__(self, correct_answers: int, wrong_answers: int) -> None:
        super().__init__()
        self.correct_answers = correct_answers
        self.wrong_answers = wrong_answers

    def compose(self) -> ComposeResult:
        total = self.correct_answers + self.wrong_answers
        accuracy = (self.correct_answers / total * 100) if total else 0.0

        with VerticalScroll(id="show_results"):
            yield Label(ui_constants.SHOW_RESULTS_TITLE, id="show_results_title")
            yield Static(
                ui_constants.SHOW_RESULTS_CORRECT.format(correct=self.correct_answers),
                id="show_results_correct",
            )
            yield Static(
                ui_constants.SHOW_RESULTS_WRONG.format(wrong=self.wrong_answers),
                id="show_results_wrong",
            )
            yield Static(
                ui_constants.SHOW_RESULTS_TOTAL.format(total=total),
                id="show_results_total",
            )
            yield Static(
                ui_constants.SHOW_RESULTS_ACCURACY.format(accuracy=accuracy),
                id="show_results_accuracy",
            )
            yield Button(ui_constants.ACTION_HOME, id="show_results_home")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "show_results_home":
            self.post_message(self.GoHome())
