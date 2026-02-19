from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Static

from src.deck_manager_session import DeckManagerSession
from src.ui import ui_constants


class DeckManagerActions(Widget):
    """Screen showing the available actions for the selected deck."""

    class BackRequested(Message):
        """Request navigation back to deck selection."""

    class DuplicateDeckRequested(Message):
        """Request creation of a copy of the current deck."""

        def __init__(self, cards: list[dict], suggested_name: str, source_deck_name: str) -> None:
            super().__init__()
            self.cards = cards
            self.suggested_name = suggested_name
            self.source_deck_name = source_deck_name

    class EditDeckRequested(Message):
        """Request opening the editor for the current deck."""

        def __init__(self, deck_name: str) -> None:
            super().__init__()
            self.deck_name = deck_name

    def __init__(self, deck_name: str) -> None:
        super().__init__()
        self.session = DeckManagerSession(deck_name)
        self.is_confirming_delete = False

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="deck_manager_actions_view"):
            yield Static(ui_constants.DECK_MANAGER_ACTIONS_TITLE, id="deck_manager_actions_title")
            yield Static(self.session.current_deck_name(), id="deck_manager_actions_name")
            yield Static(
                ui_constants.DECK_MANAGER_COUNT.format(
                    card_count=self.session.current_deck_card_count()
                ),
                id="deck_manager_actions_count",
            )
            with Horizontal(id="deck_manager_actions_row"):
                yield Button(ui_constants.DECK_MANAGER_ACTIONS_BACK_BUTTON, id="deck_manager_back")
                yield Button(ui_constants.DECK_MANAGER_DUPLICATE_BUTTON, id="deck_manager_duplicate")
                yield Button(ui_constants.DECK_MANAGER_EDIT_BUTTON, id="deck_manager_edit")
                yield Button(ui_constants.DECK_MANAGER_DELETE_BUTTON, id="deck_manager_delete")
            with Horizontal(id="deck_manager_delete_confirm_row"):
                yield Static(
                    ui_constants.DECK_MANAGER_DELETE_CONFIRM_TEXT,
                    id="deck_manager_delete_confirm_text",
                )
                yield Button(
                    ui_constants.DECK_MANAGER_DELETE_CANCEL_BUTTON,
                    id="deck_manager_delete_cancel",
                )
                yield Button(
                    ui_constants.DECK_MANAGER_DELETE_CONFIRM_BUTTON,
                    id="deck_manager_delete_confirm",
                    variant="error",
                )
            yield Static("", id="deck_manager_actions_status")

    def on_mount(self) -> None:
        self._refresh_delete_confirmation()
        self.query_one("#deck_manager_edit", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "deck_manager_back":
            self.post_message(self.BackRequested())
            return
        if button_id == "deck_manager_duplicate":
            deck_name = self.session.current_deck_name()
            self.post_message(
                self.DuplicateDeckRequested(
                    cards=self.session.current_deck_cards(),
                    suggested_name=f"{deck_name}_copy",
                    source_deck_name=deck_name,
                )
            )
            return
        if button_id == "deck_manager_edit":
            deck_name = self.session.current_deck_name()
            if deck_name:
                self.post_message(self.EditDeckRequested(deck_name))
            return
        if button_id == "deck_manager_delete":
            self.is_confirming_delete = True
            self._status().update("")
            self._refresh_delete_confirmation()
            self.query_one("#deck_manager_delete_cancel", Button).focus()
            return
        if button_id == "deck_manager_delete_cancel":
            self.is_confirming_delete = False
            self._refresh_delete_confirmation()
            self.query_one("#deck_manager_edit", Button).focus()
            return
        if button_id == "deck_manager_delete_confirm":
            deleted_name = self.session.delete_current_deck()
            if not deleted_name:
                self._status().update(ui_constants.DECK_EDITOR_DELETE_ERROR)
                self.is_confirming_delete = False
                self._refresh_delete_confirmation()
                return
            self.post_message(self.BackRequested())

    def _status(self) -> Static:
        return self.query_one("#deck_manager_actions_status", Static)

    def _refresh_delete_confirmation(self) -> None:
        display = "block" if self.is_confirming_delete else "none"
        self.query_one("#deck_manager_delete_confirm_row", Horizontal).styles.display = display
