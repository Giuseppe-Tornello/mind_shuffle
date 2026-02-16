from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

from src.deck_importer_service import DeckImporterService
from src.ui import ui_constants


class DeckImporter(Widget):
    """UI for importing a remote deck from a JSON URL.

    This widget stays intentionally thin: the service returns a simplified status
    that the UI translates into user-facing messages.
    """

    def __init__(self) -> None:
        super().__init__()
        self.service = DeckImporterService()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="deck_importer"):
            yield Label(ui_constants.DECK_IMPORTER_TITLE, id="deck_importer_title")
            yield Label(ui_constants.DECK_IMPORTER_URL_PLACEHOLDER, classes="field_label")
            yield Input(
                id="deck_importer_url",
            )
            yield Label(ui_constants.DECK_IMPORTER_NAME_PLACEHOLDER, classes="field_label")
            yield Input(
                id="deck_importer_name",
            )
            with Horizontal(id="deck_importer_actions"):
                yield Button(
                    ui_constants.DECK_IMPORTER_IMPORT_BUTTON,
                    id="deck_importer_button",
                    variant="primary",
                )
            yield Static(ui_constants.DECK_IMPORTER_READY_STATUS, id="deck_importer_status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "deck_importer_button":
            return

        status = self._status()
        url = self._input("deck_importer_url").value.strip()
        if not url:
            status.update(ui_constants.DECK_IMPORTER_URL_ERROR)
            return

        result, deck_name = self.service.import_from_url(
            url=url,
            deck_name=self._input("deck_importer_name").value,
        )
        # The UI only knows the result codes; all import logic
        # stays confined to the service.
        if result == "invalid_deck":
            status.update(ui_constants.DECK_IMPORTER_INVALID_DECK)
            return
        if result == "name_error":
            status.update(ui_constants.DECK_IMPORTER_NAME_ERROR)
            return
        if result == "url_error":
            status.update(ui_constants.DECK_IMPORTER_URL_ERROR)
            return
        status.update(ui_constants.DECK_IMPORTER_SUCCESS.format(deck_name=deck_name))
        self._input("deck_importer_name").value = deck_name

    def _input(self, input_id: str) -> Input:
        return self.query_one(f"#{input_id}", Input)

    def _status(self) -> Static:
        return self.query_one("#deck_importer_status", Static)
