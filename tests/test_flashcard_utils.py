from src.data.flashcard_utils import normalize_question_cards
from src.data.constants import Flashcard
from tests.test_constants import VALID_DECK

NORMALIZED_DECK: list[Flashcard] = [
        {"question": "What is a Python list?", "answer": "An ordered and mutable collection of elements.", "tip": "Lists use square brackets.", "tags": [], "id": 0},
    ]

def test_normalize_question_cards_output():
    assert normalize_question_cards(NORMALIZED_DECK) == list(NORMALIZED_DECK)

def test_normalize_question_cards_not_a_list():
    assert normalize_question_cards("not_a_list") == []

def test_normalize_question_cards_list_with_dict():
    assert normalize_question_cards([{}]) == []


def test_normalize_question_cards_list_with_no_dict():
    assert normalize_question_cards([[]]) == []
