from typing import TypedDict

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static

from src.data.flashcard_utils import normalize_question_cards
from src.deck_editor_storage import deck_file_path, load_deck_names, read_deck_file
from src.ui import ui_constants
from src.data.constants import Flashcard


class DeckData(TypedDict):
    name: str
    cards: list[Flashcard]


class DeckSelector(Widget):
    """Selector for available decks used to start a review session."""

    class DeckChosen(Message):
        """Event emitted when the user chooses a deck."""

        def __init__(self, deck_name: str, cards: list[Flashcard]) -> None:
            super().__init__()
            self.deck_name = deck_name
            self.cards = cards

    def __init__(self) -> None:
        super().__init__()
        self.decks = self._load_decks()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="deck_selector"):
            yield Label(ui_constants.DECK_SELECTOR_TITLE, id="deck_selector_title")
            if not self.decks:
                yield Static(ui_constants.DECK_SELECTOR_EMPTY, id="deck_selector_empty")
                return

            yield ListView(
                *[
                    ListItem(
                        Label(
                            ui_constants.DECK_SELECTOR_ITEM.format(
                                deck_name=deck["name"],
                                card_count=len(deck["cards"]),
                            ),
                            expand=True,
                        ),
                        name=deck["name"],
                    )
                    for deck in self.decks
                ],
                id="deck_selector_list",
            )

    def on_mount(self) -> None:
        if not self.decks:
            return
        deck_list = self.query_one("#deck_selector_list", ListView)
        if getattr(deck_list, "index", None) is None and deck_list.children:
            deck_list.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._emit_deck_choice(event.item)

    def _load_decks(self) -> list[DeckData]:
        decks: list[DeckData] = []

        for deck_name in load_deck_names():
            raw_cards = read_deck_file(deck_file_path(deck_name))
            cards = normalize_question_cards(raw_cards)

            if cards:
                decks.append({"name": deck_name, "cards": cards})

        return decks

    def _emit_deck_choice(self, item: ListItem | None) -> None:
        if item is None or not item.name:
            return

        selected_name = item.name
        for deck in self.decks:
            if deck["name"] == selected_name:
                self.post_message(
                    self.DeckChosen(deck_name=deck["name"], cards=deck["cards"])
                )
                return
