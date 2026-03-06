import json
from pathlib import Path
from typing import TypedDict

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static

from src.deckcheck import is_valid_deck_file
from src.ui import ui_constants
from src.ui.card_types import CardData

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DeckData(TypedDict):
    name: str
    cards: list[CardData]


class DeckSelector(Widget):
    """Selector for available decks used to start a review session."""

    class DeckChosen(Message):
        """Event emitted when the user chooses a deck."""

        def __init__(self, deck_name: str, cards: list[CardData]) -> None:
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
        deck_dir = PROJECT_ROOT / "storage" / "decks"
        decks: list[DeckData] = []

        for deck_path in sorted(deck_dir.glob("*.json")):
            if not is_valid_deck_file(str(deck_path)):
                continue
            try:
                with deck_path.open("r", encoding="utf-8") as deck_file:
                    raw_cards = json.load(deck_file)
            except (OSError, json.JSONDecodeError):
                continue

            if not isinstance(raw_cards, list):
                continue

            cards: list[CardData] = []
            for raw_card in raw_cards:
                if not isinstance(raw_card, dict):
                    continue

                question = str(raw_card.get("question", "")).strip()
                answer = str(raw_card.get("answer", "")).strip()
                tip = str(raw_card.get("tip") or "").strip()

                if not question or not answer:
                    continue

                cards.append(
                    {
                        "question": question,
                        "answer": answer,
                        "tip": tip,
                    }
                )

            if cards:
                decks.append({"name": deck_path.stem, "cards": cards})

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
