from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

from src.deck_creator_service import DeckCreatorService
from src.ui import ui_constants


class DeckCreator(Widget):
    """Schermata minima per creare un mazzo vuoto.

    Il widget non decide come creare il deck: delega tutto al service e
    si limita a raccogliere input e mostrare lo stato.
    """

    class DeckCreated(Message):
        """Notifica la creazione di un nuovo mazzo."""

        def __init__(self, deck_name: str) -> None:
            super().__init__()
            self.deck_name = deck_name

    class BackRequested(Message):
        """Richiede il ritorno alla schermata precedente del flusso mazzi."""

        def __init__(self, deck_name: str = "") -> None:
            super().__init__()
            self.deck_name = deck_name

    def __init__(
        self,
        initial_deck_name: str = "",
        initial_cards: list[dict] | None = None,
        back_deck_name: str = "",
    ) -> None:
        super().__init__()
        self.service = DeckCreatorService()
        self.initial_deck_name = initial_deck_name
        self.initial_cards = initial_cards or []
        self.back_deck_name = back_deck_name

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="deck_creator"):
            yield Label(ui_constants.DECK_CREATOR_TITLE, id="deck_creator_title")
            yield Label(ui_constants.DECK_CREATOR_DECK_PLACEHOLDER, classes="field_label")
            yield Input(id="deck_name_input")
            with Horizontal(id="deck_creator_actions"):
                yield Button(ui_constants.DECK_CREATOR_BACK_BUTTON, id="deck_creator_back")
                yield Button(ui_constants.DECK_CREATOR_CREATE_DECK_BUTTON, id="create_deck_button")
            yield Static("", id="deck_creator_status")

    def on_mount(self) -> None:
        if self.initial_deck_name:
            self._input().value = self.initial_deck_name
        self._input().focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "deck_creator_back":
            self.post_message(self.BackRequested(self.back_deck_name))
            return
        if event.button.id != "create_deck_button":
            return
        self._create_empty_deck()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "deck_name_input":
            return
        self._create_empty_deck()

    def _create_empty_deck(self) -> None:
        deck_name = self.service.create_deck(
            deck_name=self._input().value,
            cards=self.initial_cards,
        )
        if not deck_name:
            self._status().update(ui_constants.DECK_CREATOR_DECK_ERROR)
            return
        # La schermata padre usa questo messaggio per rientrare in DeckEditor
        # con il nuovo mazzo già selezionato.
        self._status().update(ui_constants.DECK_CREATOR_SUCCESS.format(deck_name=deck_name))
        self.post_message(self.DeckCreated(deck_name))

    def has_unsaved_changes(self) -> bool:
        return bool(self._input().value.strip())

    def warn_unsaved_changes(self) -> None:
        self._status().update(ui_constants.DECK_CREATOR_UNSAVED_WARNING)

    def _input(self) -> Input:
        return self.query_one("#deck_name_input", Input)

    def _status(self) -> Static:
        return self.query_one("#deck_creator_status", Static)
