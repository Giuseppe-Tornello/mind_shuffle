from src.deckimport import _convert_github_url_to_raw, get_deck_from_link
from src.data.constants import Flashcard
from tests.test_constants import VALID_DECK

# flake8: noqa: E501

def test_convert_github_url_to_raw() -> None:
    to_parse = "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/valid_deck1.json"
    parsed = "https://raw.githubusercontent.com/Giuseppe-Tornello/mind_shuffle/refs/heads/P_tests/tests/test_decks/valid_deck1.json"
    print(_convert_github_url_to_raw(to_parse))
    print(parsed)
    assert isinstance(_convert_github_url_to_raw(to_parse),str) is True
    assert _convert_github_url_to_raw(to_parse) == parsed
    assert _convert_github_url_to_raw("") == ""


def test_get_deck_from_link() -> None:
    valid_raw_url = "https://raw.githubusercontent.com/Giuseppe-Tornello/mind_shuffle/refs/heads/P_tests/tests/test_decks/valid_deck1.json"
    assert get_deck_from_link(valid_raw_url) == VALID_DECK

    valid_url = "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/valid_deck1.json"
    assert get_deck_from_link(valid_url) == VALID_DECK

    invalid_url_list: list[str] = [
        "https://this.url.does.not.exist/deck.json",
        "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/invalid_deck1.json",
        "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/invalid_deck2.html",
        "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/invalid_deck3.json",
    ]

    for invalid_url in invalid_url_list:
        assert isinstance(get_deck_from_link(invalid_url),list)
        assert get_deck_from_link(invalid_url) == []
