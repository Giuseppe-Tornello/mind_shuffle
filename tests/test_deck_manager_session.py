import time

from src.deck_editor_storage import create_deck, delete_deck, load_deck_names
from src.deck_manager_session import DeckManagerSession


def _unique_name(prefix: str = "test_deck_") -> str:
    return f"{prefix}{time.time_ns()}"


def test_has_decks_and_accessors():
    name = create_deck(
        _unique_name(),
        cards=[{"question": "Q", "answer": "A", "tip": "", "tags": [], "id": 1}],
    )
    try:
        dms = DeckManagerSession("")
        assert dms.has_decks() is True
        current = dms.current_deck_name()
        assert current in load_deck_names()
        cards = dms.current_deck_cards()
        assert isinstance(cards, list)
        assert dms.current_deck_card_count() == len(cards)
    finally:
        delete_deck(name)


def test_rename_with_empty_name_returns_empty():
    name = create_deck(
        _unique_name(),
        cards=[{"question": "Q", "answer": "A", "tip": "", "tags": [], "id": 1}],
    )
    try:
        dms = DeckManagerSession(name)
        result = dms.rename_current_deck("")
        assert result == ""
    finally:
        delete_deck(name)


def test_rename_with_name():
    name = create_deck(
        _unique_name("orig_"),
        cards=[{"question": "Q", "answer": "A", "tip": "", "tags": [], "id": 1}],
    )
    try:
        dms = DeckManagerSession(name)
        new_name = _unique_name("renamed_")
        result = dms.rename_current_deck(new_name)
        assert result == new_name
        assert new_name in load_deck_names()
        assert name not in load_deck_names()
    finally:
        delete_deck(name)
        delete_deck(new_name)


def test_delete_current_deck():
    name = create_deck(
        _unique_name(),
        cards=[{"question": "Q", "answer": "A", "tip": "", "tags": [], "id": 1}],
    )
    try:
        dms = DeckManagerSession(name)
        result = dms.delete_current_deck()
        assert result == name
        assert name not in load_deck_names()
    finally:
        delete_deck(name)
