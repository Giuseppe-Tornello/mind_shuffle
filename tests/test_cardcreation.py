from src.cardcreation import read_json, write_json, _deck_name_to_path, card_from_strings
from src.data.constants import Flashcard, JSON_ENCODING, DECKS_PATH, DECKS_EXTENSION
from tests.test_constants import TEST_DECKS_PATH, VALID_DECK, FLASHCARD_SAMPLE
import json
from os import path, remove


def test_deck_name_to_path():
    deck_name = "test_deck"
    attended_output = str(DECKS_PATH + deck_name + DECKS_EXTENSION)
    assert _deck_name_to_path(deck_name) == attended_output


def test_card_from_strings():
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
