from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

from src.deck_manager_session import DeckManagerSession
from src.ui import ui_constants


class DeckManager(Widget):
    """Hub di gestione mazzi: selezione via lista scrollabile, rename e accesso alle azioni."""

    class CreateDeckRequested(Message):
        """Richiede la schermata di creazione di un mazzo vuoto."""

    class OpenDeckActionsRequested(Message):
        """Richiede la schermata azioni per il mazzo corrente."""

        def __init__(self, deck_name: str) -> None:
            super().__init__()
            self.deck_name = deck_name

    def __init__(self, initial_deck_name: str = "") -> None:
        super().__init__()
        self.session = DeckManagerSession(initial_deck_name=initial_deck_name)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="deck_manager"):
            yield Static(ui_constants.DECK_MANAGER_TITLE, id="deck_manager_title")

            if not self.session.has_decks():
                yield Static(ui_constants.DECK_MANAGER_EMPTY, id="deck_manager_empty")
                yield Button(ui_constants.DECK_MANAGER_CREATE_BUTTON, id="deck_manager_create")
                yield Static("", id="deck_manager_status")
                return

            yield Static(ui_constants.DECK_MANAGER_SELECTED_LABEL, id="deck_manager_label")
            yield ListView(
                *[
                    ListItem(Label(deck_name, expand=True), name=deck_name)
                    for deck_name in self.session.decks
                ],
                id="deck_manager_list",
            )
            yield Static("", id="deck_manager_count")
            yield Label(ui_constants.DECK_MANAGER_RENAME_LABEL, classes="field_label")
            with Horizontal(id="deck_manager_rename_row"):
                yield Input(id="deck_manager_rename_input")
                yield Button(ui_constants.DECK_MANAGER_RENAME_BUTTON, id="deck_manager_rename")
            with Horizontal(id="deck_manager_actions"):
                yield Button(ui_constants.DECK_MANAGER_CREATE_BUTTON, id="deck_manager_create")
                yield Button(ui_constants.DECK_MANAGER_OPEN_BUTTON, id="deck_manager_open")
            yield Static("", id="deck_manager_status")

    def on_mount(self) -> None:
        self._restore_selection()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "deck_manager_create":
            self.post_message(self.CreateDeckRequested())
            return
        if button_id == "deck_manager_open":
            deck_name = self.session.current_deck_name()
            if deck_name:
                self.post_message(self.OpenDeckActionsRequested(deck_name))
            return
        if button_id == "deck_manager_rename":
            self._rename_current_deck()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "deck_manager_rename_input":
            self._rename_current_deck()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id != "deck_manager_list" or event.item is None:
            return
        if event.item.name in self.session.decks:
            self.session.select_index(self.session.decks.index(event.item.name))
            self._refresh_content()

    def _rename_current_deck(self) -> None:
        new_name = self.query_one("#deck_manager_rename_input", Input).value
        renamed_name = self.session.rename_current_deck(new_name)
        if not renamed_name:
            self._status().update(ui_constants.DECK_MANAGER_RENAME_ERROR)
            return
        self._status().update(ui_constants.DECK_MANAGER_RENAME_SUCCESS.format(deck_name=renamed_name))
        self.refresh(recompose=True)
        self.call_after_refresh(self._restore_selection)

    def _refresh_content(self) -> None:
        if not self.session.has_decks():
            return
        self.query_one("#deck_manager_count", Static).update(
            ui_constants.DECK_MANAGER_COUNT.format(
                card_count=self.session.current_deck_card_count()
            )
        )
        self.query_one("#deck_manager_rename_input", Input).value = self.session.current_deck_name()

    def _restore_selection(self) -> None:
        self._refresh_content()
        if self.session.has_decks():
            deck_list = self.query_one("#deck_manager_list", ListView)
            deck_list.index = self.session.current_index
            deck_list.focus()
            return
        self.query_one("#deck_manager_create", Button).focus()

    def _status(self) -> Static:
        return self.query_one("#deck_manager_status", Static)
