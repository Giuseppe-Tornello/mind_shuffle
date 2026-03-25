from src.deck_manager_session import DeckManagerSession
from src.deck_editor_storage import create_deck, delete_deck, load_deck_names


def test_has_decks_and_accessors():
    dms = DeckManagerSession("")
    assert dms.has_decks() is True
    name = dms.current_deck_name()
    assert name in load_deck_names()
    cards = dms.current_deck_cards()
    assert isinstance(cards, list)
    assert dms.current_deck_card_count() == len(cards)


def test_rename_with_empty_name_returns_empty():
    dms = DeckManagerSession("")
    result = dms.rename_current_deck("")
    assert result == ""