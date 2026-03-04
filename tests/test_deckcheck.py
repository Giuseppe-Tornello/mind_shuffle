from src.deckcheck import is_valid_deck_extension


def test_is_valid_deck_extension() -> None:
    right_str = "/path/to/file/ending/with.json"
    wrong_str = "/path/to/file/ending/with.png"
    assert type(is_valid_deck_extension(right_str)) is bool
    assert is_valid_deck_extension(right_str) is True

    assert type(is_valid_deck_extension(wrong_str)) is bool
    assert is_valid_deck_extension(wrong_str) is False
