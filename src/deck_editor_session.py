import json
import logging

from src.data.constants import Flashcard
from src.deck_editor_storage import (
    DeckFileError,
    deck_exists,
    delete_deck,
    deck_file_path,
    empty_card,
    load_deck_cards,
    load_deck_names,
    write_deck_file,
)

LOGGER = logging.getLogger(__name__)


class DeckEditorSession:
    """State and logic for the deck editor."""

    def __init__(self, initial_deck_name: str = "") -> None:
        self.initial_deck_name = initial_deck_name
        self.decks = load_deck_names()
        self.deck_name = ""
        self.original_cards: list[Flashcard] = []
        self.cards: list[Flashcard] = []
        self.current_index = 0
        self.is_dirty = False

    def has_unsaved_changes(self) -> bool:
        return self.is_dirty

    def has_decks(self) -> bool:
        return bool(self.decks)

    def selected_or_first_deck(self) -> str:
        """Prefer the caller-selected deck, otherwise use the first available one."""
        if self.initial_deck_name in self.decks:
            return self.initial_deck_name
        if self.initial_deck_name and deck_exists(self.initial_deck_name):
            return self.initial_deck_name
        if self.decks:
            return self.decks[0]
        return ""

    def load_selected_deck(self, deck_name: str) -> bool:
        """Load the persisted deck and prepare an editable in-memory working copy."""
        try:
            loaded_cards = load_deck_cards(deck_name)
        except (DeckFileError, OSError, json.JSONDecodeError):
            LOGGER.exception("Failed to load deck '%s' into editor session", deck_name)
            return False
        self.original_cards = [card.copy() for card in loaded_cards]
        self.cards = [card.copy() for card in loaded_cards]
        self.deck_name = deck_name
        self.current_index = 0
        self.is_dirty = False
        return True

    def current_card(self) -> Flashcard:
        if not self.cards:
            return empty_card(1)
        return self.cards[self.current_index]

    def progress(self) -> tuple[int, int]:
        if not self.cards:
            return (0, 0)
        return (self.current_index + 1, len(self.cards))

    def go_to_card(self, card_number: int) -> bool:
        """Move the editor to a specific card using 1-based numbering."""
        if not self.cards:
            return False
        if card_number < 1 or card_number > len(self.cards):
            return False
        self.current_index = card_number - 1
        return True

    def save_current_card_fields(
        self,
        question: str,
        answer: str,
        tip: str,
        tags_text: str,
    ) -> None:
        # The UI passes raw strings; the session normalizes them
        # into the format persisted on disk.
        if not self.cards:
            return
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        self.cards[self.current_index] = {
            "question": question.strip(),
            "answer": answer.strip(),
            "tip": tip.strip() or "",
            "tags": tags,
            "id": self.cards[self.current_index].get("id", self.current_index + 1),
        }

    def previous_card(self) -> None:
        if not self.cards:
            return
        self.current_index = (self.current_index - 1) % len(self.cards)

    def next_card(self) -> None:
        if not self.cards:
            return
        self.current_index = (self.current_index + 1) % len(self.cards)

    def add_card(self) -> None:
        """Add an empty card and make it the active one."""
        self.cards.append(empty_card(len(self.cards) + 1))
        self.current_index = len(self.cards) - 1
        self.is_dirty = True

    def remove_current_card(self) -> None:
        """Remove the active card from the working copy without touching the real file."""
        if not self.cards:
            return
        if len(self.cards) == 1:
            self.cards = [empty_card(1)]
            self.current_index = 0
            self.is_dirty = True
            return
        self.cards.pop(self.current_index)
        if self.current_index >= len(self.cards):
            self.current_index = len(self.cards) - 1
        self.is_dirty = True

    def discard_changes(self) -> None:
        """Restore the working copy to the last version confirmed on disk."""
        self.cards = [card.copy() for card in self.original_cards]
        if not self.cards:
            self.cards = [empty_card(1)]
        if self.current_index >= len(self.cards):
            self.current_index = len(self.cards) - 1
        self.is_dirty = False

    def change_selected_deck(self, step: int) -> bool:
        """Cycle through decks, but only when there are no pending changes."""
        if len(self.decks) <= 1 or self.is_dirty:
            return False
        current_index = self.decks.index(self.deck_name) if self.deck_name in self.decks else 0
        next_index = (current_index + step) % len(self.decks)
        return self.load_selected_deck(self.decks[next_index])

    def save_deck(
        self,
        question: str,
        answer: str,
        tip: str,
        tags_text: str,
    ) -> str:
        """
        Save the active deck by overwriting the real file with the working copy.
        """
        self.save_current_card_fields(question, answer, tip, tags_text)
        if not self.deck_name:
            LOGGER.warning("Cannot save deck without a selected deck name")
            return "name_error"
        if not self.cards_are_valid():
            LOGGER.warning("Cannot save deck '%s': one or more cards are invalid", self.deck_name)
            return "card_error"

        # Only here does the working copy become definitive and replace the real file.
        write_deck_file(self.cards, deck_file_path(self.deck_name))
        self.decks = load_deck_names()
        self.original_cards = [card.copy() for card in self.cards]
        self.is_dirty = False
        return "saved"

    def delete_current_deck(self) -> str:
        """Delete the active deck and, when possible, select the next available one."""
        if not self.deck_name:
            LOGGER.warning("Cannot delete deck: no active deck selected")
            return "delete_error"

        deleted_name = self.deck_name
        delete_deck(self.deck_name)
        self.decks = load_deck_names()
        self.original_cards = []
        self.cards = []
        self.current_index = 0
        self.deck_name = ""
        self.is_dirty = False

        if self.decks:
            self.load_selected_deck(self.decks[0])
        return deleted_name

    def cards_are_valid(self) -> bool:
        """Validate cards and realign ids before saving."""
        for index, card in enumerate(self.cards, start=1):
            if not card["question"] or not card["answer"]:
                return False
            card["id"] = index
        return True
