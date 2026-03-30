from src.deckcheck import (
    Flashcard,
    is_valid_deck,
    is_valid_deck_extension,
    is_valid_deck_file,
)
from tests.test_constants import TEST_DECKS_PATH, VALID_DECK


def test_is_valid_deck_extension() -> None:
    right_str = "/path/to/file/ending/with.json"
    wrong_str = "/path/to/file/ending/with.png"
    assert isinstance(is_valid_deck_extension(right_str), bool)
    assert is_valid_deck_extension(right_str) is True

    assert isinstance(is_valid_deck_extension(wrong_str), bool)
    assert is_valid_deck_extension(wrong_str) is False


def test_is_valid_deck_file() -> None:
    valid_deck = "valid_deck1.json"
    invalid_deck_names = [
        "invalid_deck1.json",  # has two id as '1'
        "invalid_deck2.html",  # has wrong file extension
        "invalid_deck3.json",  # invalid json
        "invalid_deck4.json",  # not a list
        "invalid_deck5.json",  # does not exist
    ]

    temp_deck_path = TEST_DECKS_PATH + valid_deck
    assert isinstance(is_valid_deck_file(temp_deck_path), bool)
    assert is_valid_deck_file(temp_deck_path) is True

    for invalid in invalid_deck_names:
        temp_deck_path = TEST_DECKS_PATH + invalid
        assert isinstance(is_valid_deck_file(temp_deck_path), bool)
        assert is_valid_deck_file(temp_deck_path) is False


def test_is_valid_deck() -> None:

    assert isinstance(is_valid_deck(VALID_DECK), bool)
    assert is_valid_deck(VALID_DECK) is True

    invalid_deck0: list[Flashcard] = []
    invalid_deck1: list[Flashcard] = [
        {
            "id": 1,
            "question": "Question 1",
            "answer": "Answer 1",
            "tags": ["tag1"],
            "tip": "tip",
        },
        {
            "id": 1,
            "question": "Question 2",
            "answer": "Answer 2",
            "tags": ["tag2"],
            "tip": "",
        },
        # id is <= than the previous card
    ]

    invalid_deck2: list[Flashcard] = [
        {
            "id": 1,
            "question": "Question 1",
            "answer": "Answer 1",
            "tags": ["tag1"],
            "tip": "tip",
        },
        {"id": 2, "question": "Question 2", "answer_bla": "Answer 2", "tags": ["tag2"], "tip": ""},  # type: ignore[typeddict-item,typeddict-unknown-key] # noqa: E501
        # answer_bla is not permitted
    ]

    invalid_deck3: list[Flashcard] = [
        {
            "id": 1,
            "question": "Question 1",
            "answer": "Answer 1",
            "tags": ["tag1"],
            "tip": "tip",
        },
        {
            "id": 2,
            "question": "Question 2",
            "answer": "",
            "tags": ["tag2"],
            "tip": "",
        },  # answer is empty
    ]

    invalid_decks: list[list[Flashcard]] = [
        invalid_deck0,
        invalid_deck1,
        invalid_deck2,
        invalid_deck3,
    ]

    for invalid in invalid_decks:
        assert isinstance(is_valid_deck(invalid), bool)
        assert is_valid_deck(invalid) is False
