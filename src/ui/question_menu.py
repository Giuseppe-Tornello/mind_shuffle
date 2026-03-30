from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.events import Key
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

from src.data.constants import Flashcard
from src.ui import ui_constants
from src.ui.question_session import QuestionSession


class QuestionMenu(Widget):
    """Widget used to train with question and answer cards."""

    class GoHome(Message):
        """Request navigation back to the home screen."""

    class ShowResultsRequested(Message):
        """Request opening the final results screen."""

        def __init__(self, correct_answers: int, wrong_answers: int) -> None:
            super().__init__()
            self.correct_answers = correct_answers
            self.wrong_answers = wrong_answers

    def __init__(self, cards: list[Flashcard] | None = None) -> None:
        super().__init__()
        self.session = QuestionSession(cards)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="question_menu"):
            yield Label(ui_constants.QUESTION_MENU_TITLE, id="question_menu_title")
            yield Static("", id="question_progress")
            yield Static("", id="question_text")
            yield Label(
                ui_constants.QUESTION_MENU_INPUT_LABEL, id="question_input_label"
            )
            yield Input(id="question_user_input")
            yield Static("", id="question_answer")
            yield Static("", id="question_tip")
            yield Static("", id="question_stats")
            with Horizontal(id="question_actions"):
                yield Button(
                    ui_constants.QUESTION_MENU_REVEAL_BUTTON,
                    id="btn_reveal",
                    variant="primary",
                )
                yield Button(
                    ui_constants.QUESTION_MENU_CORRECT_BUTTON,
                    id="btn_correct",
                    variant="success",
                )
                yield Button(
                    ui_constants.QUESTION_MENU_WRONG_BUTTON,
                    id="btn_wrong",
                    variant="error",
                )
                yield Button(ui_constants.ACTION_BACK, id="btn_prev")
                yield Button(ui_constants.QUESTION_MENU_NEXT_BUTTON, id="btn_next")
                yield Button(
                    ui_constants.QUESTION_MENU_FINISH_BUTTON,
                    id="btn_finish",
                    variant="warning",
                )
                yield Button(ui_constants.ACTION_HOME, id="btn_home")

    def on_mount(self) -> None:
        self._refresh_content()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Always persist the current input before changing screen or state.
        self._save_current_user_answer()
        focus_input = False
        should_refresh = True

        if event.button.id == "btn_reveal":
            self.session.reveal_answer()
        elif event.button.id == "btn_correct":
            should_refresh = self._register_and_advance(is_correct=True)
            focus_input = should_refresh
        elif event.button.id == "btn_wrong":
            should_refresh = self._register_and_advance(is_correct=False)
            focus_input = should_refresh
        elif event.button.id == "btn_prev":
            self.session.previous_question()
            focus_input = True
        elif event.button.id == "btn_next":
            self.session.next_question()
            focus_input = True
        elif event.button.id == "btn_finish":
            self._request_results()
            should_refresh = False
        elif event.button.id == "btn_home":
            self.post_message(self.GoHome())
            should_refresh = False
        if should_refresh:
            self._refresh_content()
        if focus_input:
            self._answer_input().focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "question_user_input":
            return
        self._save_current_user_answer()
        self.session.next_question()
        self._refresh_content()
        self._answer_input().focus()

    def on_key(self, event: Key) -> None:
        if not self.session.has_cards():
            return

        key = event.key
        focused = self.screen.focused
        if key in {"left", "right"} and isinstance(focused, Input):
            # Inside the input field, horizontal arrows must stay available for the caret.
            return

        # In the question menu, only horizontal arrows switch between questions.
        # Vertical arrows stay available to the container for focus navigation.
        if key == "left":
            self._navigate_questions(step=-1)
            event.stop()
            return

        if key == "right":
            self._navigate_questions(step=1)
            event.stop()

    def _register_answer(self, is_correct: bool) -> bool:
        was_registered = self.session.register_answer(is_correct)
        if not was_registered:
            return False

        if self.session.all_answered():
            return self._request_results()
        return False

    def _register_and_advance(self, is_correct: bool) -> bool:
        opened_results = self._register_answer(is_correct)
        if opened_results:
            return False

        if self.session.current_question_answered():
            self.session.next_question()
            return True
        return False

    def _save_current_user_answer(self) -> None:
        self.session.save_user_answer(self._answer_input().value)

    def _navigate_questions(self, step: int) -> None:
        self._save_current_user_answer()
        if step < 0:
            self.session.previous_question()
        else:
            self.session.next_question()
        self._refresh_content()
        self._answer_input().focus()

    def _request_results(self) -> bool:
        if not self.session.mark_results_requested():
            return False
        self.post_message(
            self.ShowResultsRequested(
                correct_answers=self.session.correct_answers,
                wrong_answers=self.session.wrong_answers,
            )
        )
        return True

    def _refresh_content(self) -> None:
        progress = self._static_widget("question_progress")
        question = self._static_widget("question_text")
        answer = self._static_widget("question_answer")
        tip = self._static_widget("question_tip")
        stats = self._static_widget("question_stats")
        btn_correct = self._button("btn_correct")
        btn_wrong = self._button("btn_wrong")

        if not self.session.has_cards():
            progress.update(ui_constants.QUESTION_MENU_NO_QUESTIONS)
            question.update(ui_constants.QUESTION_MENU_NO_QUESTIONS_HINT)
            answer.update(ui_constants.QUESTION_MENU_EMPTY_ANSWER)
            tip.update(ui_constants.QUESTION_MENU_EMPTY_TIP)
            stats.update(ui_constants.QUESTION_MENU_STATS.format(correct=0, wrong=0))
            btn_correct.disabled = True
            btn_wrong.disabled = True
            return

        card = self.session.current_card()
        user_input = self._answer_input()
        user_input.value = self.session.current_answer_text()
        answered_current = self.session.current_question_answered()

        progress.update(
            ui_constants.QUESTION_MENU_PROGRESS.format(
                current=self.session.current_index + 1, total=len(self.session.cards)
            )
        )
        question.update(
            f"{ui_constants.QUESTION_MENU_QUESTION_PREFIX}: "
            f"{card.get('question', ui_constants.QUESTION_MENU_QUESTION_MISSING)}"
        )

        if self.session.answer_visible:
            answer.update(
                f"{ui_constants.QUESTION_MENU_ANSWER_PREFIX}: "
                f"{card.get('answer', ui_constants.QUESTION_MENU_ANSWER_MISSING)}"
            )
            tip_text = card.get("tip", "")
            tip.update(
                f"{ui_constants.QUESTION_MENU_HINT_PREFIX}: {tip_text}"
                if tip_text
                else ""
            )
        else:
            answer.update(
                ui_constants.QUESTION_MENU_HIDDEN_ANSWER.format(
                    answer_prefix=ui_constants.QUESTION_MENU_ANSWER_PREFIX,
                    button_name=ui_constants.QUESTION_MENU_REVEAL_BUTTON,
                )
            )
            tip.update(ui_constants.QUESTION_MENU_EMPTY_TIP)

        stats.update(
            ui_constants.QUESTION_MENU_STATS.format(
                correct=self.session.correct_answers, wrong=self.session.wrong_answers
            )
        )
        btn_correct.disabled = answered_current
        btn_wrong.disabled = answered_current

    def _answer_input(self) -> Input:
        return self.query_one("#question_user_input", Input)

    def _button(self, button_id: str) -> Button:
        return self.query_one(f"#{button_id}", Button)

    def _static_widget(self, widget_id: str) -> Static:
        return self.query_one(f"#{widget_id}", Static)
