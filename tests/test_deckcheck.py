from src.deckcheck import is_valid_deck_extension, is_valid_deck_file


def test_is_valid_deck_extension() -> None:
    right_str = "/path/to/file/ending/with.json"
    wrong_str = "/path/to/file/ending/with.png"
    assert isinstance(is_valid_deck_extension(right_str), bool)
    assert is_valid_deck_extension(right_str) is True

    assert isinstance(is_valid_deck_extension(wrong_str), bool)
    assert is_valid_deck_extension(wrong_str) is False


def test_is_valid_deck_file() -> None:
    TEST_DECKS_PATH = "tests/test_decks/"
    valid_deck_names = ["valid_deck1.json", "valid_deck2.json"]
    invalid_deck_names = [
        "invalid_deck1.json",
        "invalid_deck2.html",
        "invalid_deck3.json",
        "invalid_deck4.json",
        "invalid_deck5.json",
        ]

    for valid in valid_deck_names:
        temp_deck_path = TEST_DECKS_PATH + valid
        assert isinstance(is_valid_deck_file(temp_deck_path), bool)
        assert is_valid_deck_file(temp_deck_path) is True

    for invalid in invalid_deck_names:
        temp_deck_path = TEST_DECKS_PATH + invalid
        assert isinstance(is_valid_deck_file(temp_deck_path), bool)
        assert is_valid_deck_file(temp_deck_path) is False
