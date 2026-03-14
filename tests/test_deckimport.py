from src.deckimport import _convert_github_url_to_raw, get_deck_from_link
from src.data.constants import Flashcard

# flake8: noqa: E501

def test_convert_github_url_to_raw() -> None:
    to_parse = "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/valid_deck1.json"
    parsed = "https://raw.githubusercontent.com/Giuseppe-Tornello/mind_shuffle/refs/heads/P_tests/tests/test_decks/valid_deck1.json"
    print(_convert_github_url_to_raw(to_parse))
    print(parsed)
    assert _convert_github_url_to_raw(to_parse) == parsed
    assert _convert_github_url_to_raw("") == ""


def test_get_deck_from_link() -> None:
    valid_raw_url = "https://raw.githubusercontent.com/Giuseppe-Tornello/mind_shuffle/refs/heads/P_tests/tests/test_decks/valid_deck1.json"
    valid_deck: list[Flashcard] = [
        {"question": "What is a Python list?", "answer": "An ordered and mutable collection of elements.", "tip": "Lists use square brackets.", "tags": ["python", "basics"], "id": 1},
        {"question": "How do you create a dictionary in Python?", "answer": "Using curly braces with key value pairs, for example {'a': 1}.", "tip": "The constructor dict() is another option.", "tags": ["python", "dict"], "id": 2},
        {"question": "What does len('flashcard') return?", "answer": "9", "tip": None, "tags": ["python", "strings"], "id": 3},  # type: ignore[typeddict-item]
        {"question": "What is the output type of range(5)?", "answer": "A range object.", "tip": "Convert it with list(range(5)) if needed.", "tags": ["python", "iteration"], "id": 4}
    ]
    assert get_deck_from_link(valid_raw_url) == valid_deck

    valid_url = "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/valid_deck1.json"
    assert get_deck_from_link(valid_url) == valid_deck

    invalid_url_list: list[str] = [
        "https://this.url.does.not.exist/deck.json",
        "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/invalid_deck1.json",
        "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/invalid_deck2.html",
        "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/invalid_deck3.json",
    ]

    for invalid_url in invalid_url_list:
        assert get_deck_from_link(invalid_url) == []
