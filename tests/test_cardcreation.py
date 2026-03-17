from src.cardcreation import read_json, write_json, _deck_name_to_path, card_from_strings, import_deck, delete_card
from src.data.constants import JSON_ENCODING, DECKS_PATH, DECKS_EXTENSION
from tests.test_constants import TEST_DECKS_PATH, VALID_DECK, FLASHCARD_SAMPLE, INVALID_DECK
import json
from os import path, remove


def test_deck_name_to_path() -> None:
    deck_name = "test_deck"
    attended_output = str(DECKS_PATH + deck_name + DECKS_EXTENSION)
    assert _deck_name_to_path(deck_name) == attended_output


def test_card_from_strings() -> None:
    assert card_from_strings("What is a Python list?", "An ordered and mutable collection of elements.", "Lists use square brackets.", ["python", "basics"]) == FLASHCARD_SAMPLE


def test_read_json() -> None:
    assert read_json(TEST_DECKS_PATH + "valid_deck1.json") == VALID_DECK
    assert read_json(TEST_DECKS_PATH + "non_existant_deck.json") == []


def test_write_json() -> None:
    deck_path = TEST_DECKS_PATH + "test_deck.json"
    write_json(VALID_DECK, deck_path)

    assert path.isfile(deck_path) is True

    with open(deck_path, "r", encoding=JSON_ENCODING) as f:
        data = json.load(f)

    assert data == VALID_DECK
    remove(deck_path)


def test_import_deck() -> None:
    deck_name = "test"
    import_deck(VALID_DECK, deck_name)
    deck_path = _deck_name_to_path(deck_name)

    assert path.isfile(deck_path) is True

    with open(deck_path, "r", encoding=JSON_ENCODING) as f:
        data = json.load(f)
    assert data == VALID_DECK

    deck_name2 = "test1"
    deck_path2 = _deck_name_to_path(deck_name2)
    assert path.isfile(deck_path2) is False

    import_deck(VALID_DECK, deck_name)
    assert path.isfile(deck_path2) is True

    with open(deck_path, "r", encoding=JSON_ENCODING) as f:
        data = json.load(f)
    assert data == VALID_DECK

    remove(deck_path)
    remove(deck_path2)

    import_deck(INVALID_DECK, deck_name)
    assert path.isfile(deck_path) is False


def test_delete_card() -> None:
    deck_name = "test"
    import_deck(VALID_DECK, deck_name)
    deck_path = _deck_name_to_path(deck_name)

    def find_id(id: int, d_path: str):
        with open(d_path, "r", encoding=JSON_ENCODING) as f:
            data = json.load(f)
        for item in data:
            if isinstance(item, dict) and item.get('id') == id:
                return True
        return False

    assert find_id(4, deck_path) is True
    delete_card(4, deck_name)
    assert find_id(4, deck_path) is False

    remove(deck_path)
