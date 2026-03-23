from src.deck_editor_storage import (
    deck_file_path,
    delete_deck,
    load_deck_names,
    read_deck_file,
    rename_deck,
)
from src.data.constants import Flashcard


class DeckManagerSession:
    """State and logic for the deck management hub screen."""

    def __init__(self, initial_deck_name: str = "") -> None:
        self.decks = load_deck_names()
        self.current_index = 0
        if initial_deck_name in self.decks:
            self.current_index = self.decks.index(initial_deck_name)

    def has_decks(self) -> bool:
        return bool(self.decks)

    def current_deck_name(self) -> str:
        if not self.decks:
            return ""
        return self.decks[self.current_index]

    def current_deck_cards(self) -> list[Flashcard]:
        deck_name = self.current_deck_name()
        if not deck_name:
            return []
        return read_deck_file(deck_file_path(deck_name))

    def current_deck_card_count(self) -> int:
        return len(self.current_deck_cards())

    def select_index(self, index: int) -> None:
        if not self.decks:
            return
        self.current_index = max(0, min(index, len(self.decks) - 1))

    def rename_current_deck(self, new_name: str) -> str:
        deck_name = self.current_deck_name()
        normalized_name = new_name.strip()
        if not deck_name or not normalized_name:
            return ""
        if not rename_deck(deck_name, normalized_name):
            return ""
        self.decks = load_deck_names()
        if normalized_name in self.decks:
            self.current_index = self.decks.index(normalized_name)
        return normalized_name

    def delete_current_deck(self) -> str:
        deck_name = self.current_deck_name()
        if not deck_name:
            return ""
        delete_deck(deck_name)
        self.decks = load_deck_names()
        if self.current_index >= len(self.decks):
            self.current_index = max(len(self.decks) - 1, 0)
        return deck_name
