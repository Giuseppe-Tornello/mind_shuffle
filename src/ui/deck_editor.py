from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

from src.deck_editor_session import DeckEditorSession
from src.ui import ui_constants


class DeckEditor(Widget):
    """UI container for the deck editor.

    The real state lives in `DeckEditorSession`: this widget only renders fields,
    receives Textual events, and keeps values synchronized.
    Editing always happens against an in-memory working copy: the real file is
    updated only when the user confirms with "Save changes".
    """

    class BackRequested(Message):
        """Request navigation back to the current deck actions screen."""

        def __init__(self, deck_name: str) -> None:
            self.deck_name = deck_name
            super().__init__()

    class CreateDeckRequested(Message):
        """Request opening the create-deck screen."""

    def __init__(self, create_mode: bool = False, initial_deck_name: str = "") -> None:
        super().__init__()
        self.create_mode = create_mode
        self.session = DeckEditorSession(initial_deck_name=initial_deck_name)
        self._suspend_dirty_tracking = 0
        self._dirty_reset_generation = 0

    def compose(self) -> ComposeResult:
        title = (
            ui_constants.DECK_EDITOR_CREATE_TITLE
            if self.create_mode
            else ui_constants.DECK_EDITOR_TITLE
        )
        with VerticalScroll(id="deck_editor"):
            yield Label(title, id="deck_editor_title")

            if not self.create_mode:
                yield Label(ui_constants.DECK_EDITOR_DECK_LABEL, id="deck_editor_label")
                yield Static("", id="deck_editor_selected_name")

            yield Static("", id="deck_editor_progress")
            yield Label(ui_constants.DECK_EDITOR_CARD_NUMBER_LABEL, classes="field_label")
            with Horizontal(id="deck_editor_jump_row"):
                yield Button(ui_constants.DECK_EDITOR_PREV_BUTTON, id="deck_editor_prev")
                yield Input(id="deck_editor_card_number")
                yield Button(ui_constants.DECK_EDITOR_NEXT_BUTTON, id="deck_editor_next")
            yield Label(ui_constants.FIELD_QUESTION, classes="field_label")
            yield Input(id="deck_editor_question")
            yield Label(ui_constants.FIELD_ANSWER, classes="field_label")
            yield Input(id="deck_editor_answer")
            yield Label(ui_constants.FIELD_TIP, classes="field_label")
            yield Input(id="deck_editor_tip")
            yield Label(ui_constants.FIELD_TAGS, classes="field_label")
            yield Input(id="deck_editor_tags")
            with Horizontal(id="deck_editor_actions"):
                yield Button(ui_constants.DECK_EDITOR_NEW_BUTTON, id="deck_editor_new")
                yield Button(ui_constants.DECK_EDITOR_REMOVE_BUTTON, id="deck_editor_remove")
                yield Button(ui_constants.ACTION_BACK, id="deck_editor_back")
                yield Button(ui_constants.DECK_EDITOR_CANCEL_BUTTON, id="deck_editor_cancel")
                yield Button(
                    ui_constants.DECK_EDITOR_SAVE_BUTTON,
                    id="deck_editor_save",
                    variant="primary",
                )
            yield Static("", id="deck_editor_status")

    def on_mount(self) -> None:
        if not self.create_mode:
            deck_name = self.session.selected_or_first_deck()
            if deck_name and not self.session.load_selected_deck(deck_name):
                self._status().update(ui_constants.DECK_EDITOR_LOAD_ERROR)
            elif deck_name:
                self._sync_inputs_from_session()
            else:
                self._sync_inputs_from_session()
        else:
            self._sync_inputs_from_session()
        self._focus_initial_input()

    def on_input_changed(self, event: Input.Changed) -> None:
        if not event.input.id or not event.input.id.startswith("deck_editor_"):
            return
        if event.input.id == "deck_editor_card_number":
            return
        if self._suspend_dirty_tracking:
            return
        self.session.is_dirty = not self._inputs_match_session()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "deck_editor_prev":
            self._go_previous_card()
        elif button_id == "deck_editor_next":
            self._go_next_card()
        elif button_id == "deck_editor_new":
            self._add_card()
        elif button_id == "deck_editor_remove":
            self._remove_card()
        elif button_id == "deck_editor_back":
            self._handle_back_request()
        elif button_id == "deck_editor_cancel":
            self._cancel_changes()
        elif button_id == "deck_editor_save":
            self._save_deck()
        elif button_id == "deck_editor_delete":
            self._delete_deck()

    def has_unsaved_changes(self) -> bool:
        self.session.is_dirty = not self._inputs_match_session()
        return self.session.has_unsaved_changes()

    def warn_unsaved_changes(self) -> None:
        self._status().update(ui_constants.DECK_EDITOR_UNSAVED_WARNING)

    def _go_previous_card(self) -> None:
        self._store_current_inputs()
        self.session.previous_card()
        self._sync_inputs_from_session()

    def _go_next_card(self) -> None:
        self._store_current_inputs()
        self.session.next_card()
        self._sync_inputs_from_session()

    def _add_card(self) -> None:
        self._store_current_inputs()
        self.session.add_card()
        self._sync_inputs_from_session()

    def _remove_card(self) -> None:
        self._store_current_inputs()
        self.session.remove_current_card()
        self._sync_inputs_from_session()

    def _handle_back_request(self) -> None:
        if self.has_unsaved_changes():
            self.warn_unsaved_changes()
            return
        self._status().update("")
        self.post_message(self.BackRequested(self.session.deck_name))

    def _cancel_changes(self) -> None:
        self.session.discard_changes()
        self._status().update("")
        self.post_message(self.BackRequested(self.session.deck_name))

    def _save_deck(self) -> None:
        result = self.session.save_deck(
            question=self._input("deck_editor_question").value,
            answer=self._input("deck_editor_answer").value,
            tip=self._input("deck_editor_tip").value,
            tags_text=self._input("deck_editor_tags").value,
        )
        if result == "name_error":
            self._status().update(ui_constants.DECK_EDITOR_NAME_ERROR)
            return
        if result == "card_error":
            self._status().update(ui_constants.DECK_EDITOR_CARD_ERROR)
            return
        self._status().update(
            ui_constants.DECK_EDITOR_SAVE_SUCCESS.format(deck_name=self.session.deck_name)
        )
        self._refresh_deck_controls()
        self._schedule_dirty_reset()

    def _delete_deck(self) -> None:
        deleted_name = self.session.delete_current_deck()
        if deleted_name == "delete_error":
            self._status().update(ui_constants.DECK_EDITOR_DELETE_ERROR)
            return
        self._status().update(
            ui_constants.DECK_EDITOR_DELETE_SUCCESS.format(deck_name=deleted_name)
        )
        self._sync_inputs_from_session()

    def _store_current_inputs(self) -> None:
        self.session.save_current_card_fields(
            question=self._input("deck_editor_question").value,
            answer=self._input("deck_editor_answer").value,
            tip=self._input("deck_editor_tip").value,
            tags_text=self._input("deck_editor_tags").value,
        )

    def _sync_inputs_from_session(self) -> None:
        card = self.session.current_card()
        current, total = self.session.progress()
        self._set_input_value(self._input("deck_editor_question"), card.get("question", ""))
        self._set_input_value(self._input("deck_editor_answer"), card.get("answer", ""))
        self._set_input_value(self._input("deck_editor_tip"), card.get("tip") or "")
        self._set_input_value(
            self._input("deck_editor_tags"),
            ", ".join(card.get("tags") or []),
        )
        self._set_input_value(
            self._input("deck_editor_card_number"),
            str(self.session.current_index + 1) if total else "",
        )
        self._progress().update(
            ui_constants.DECK_EDITOR_PROGRESS.format(current=current, total=total)
            if total
            else ""
        )
        self._refresh_deck_controls()
        self._schedule_dirty_reset()

    def _refresh_deck_controls(self) -> None:
        if self.create_mode or not self.query("#deck_editor_selected_name"):
            return
        self.query_one("#deck_editor_selected_name", Static).update(
            self.session.deck_name or ui_constants.DECK_EDITOR_EMPTY
        )

    def _focus_initial_input(self) -> None:
        self._input("deck_editor_question").focus()

    def _schedule_dirty_reset(self) -> None:
        self._dirty_reset_generation += 1
        generation = self._dirty_reset_generation

        def clear_dirty() -> None:
            if generation != self._dirty_reset_generation:
                return
            self.session.is_dirty = not self._inputs_match_session()

        self.call_after_refresh(clear_dirty)

    def _inputs_match_session(self) -> bool:
        card = self.session.current_card()
        current_tags = [
            tag.strip()
            for tag in self._input("deck_editor_tags").value.split(",")
            if tag.strip()
        ]
        return (
            self._input("deck_editor_question").value.strip() == card.get("question", "")
            and self._input("deck_editor_answer").value.strip() == card.get("answer", "")
            and self._input("deck_editor_tip").value.strip() == (card.get("tip") or "")
            and current_tags == list(card.get("tags") or [])
        )

    def _set_input_value(self, input_widget: Input, value: str) -> None:
        self._suspend_dirty_tracking += 1
        try:
            input_widget.value = value
        finally:
            self._suspend_dirty_tracking -= 1

    def _input(self, input_id: str) -> Input:
        return self.query_one(f"#{input_id}", Input)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "deck_editor_card_number":
            self._go_to_card_number()

    def _go_to_card_number(self) -> None:
        raw_value = self._input("deck_editor_card_number").value.strip()
        if not raw_value.isdigit():
            self._status().update(ui_constants.DECK_EDITOR_CARD_NUMBER_ERROR)
            self._set_input_value(
                self._input("deck_editor_card_number"),
                str(self.session.current_index + 1) if self.session.cards else "",
            )
            return
        self._store_current_inputs()
        if not self.session.go_to_card(int(raw_value)):
            self._status().update(ui_constants.DECK_EDITOR_CARD_NUMBER_ERROR)
            self._set_input_value(
                self._input("deck_editor_card_number"),
                str(self.session.current_index + 1) if self.session.cards else "",
            )
            return
        self._status().update("")
        self._sync_inputs_from_session()

    def _status(self) -> Static:
        return self.query_one("#deck_editor_status", Static)

    def _progress(self) -> Static:
        return self.query_one("#deck_editor_progress", Static)
