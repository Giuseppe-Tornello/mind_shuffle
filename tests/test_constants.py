from src.data.constants import Flashcard

# flake8: noqa: E501


TEST_DECKS_PATH = "tests/test_decks/"
VALID_DECK: list[Flashcard] = [
        {"question": "What is a Python list?", "answer": "An ordered and mutable collection of elements.", "tip": "Lists use square brackets.", "tags": ["python", "basics"], "id": 1},
        {"question": "How do you create a dictionary in Python?", "answer": "Using curly braces with key value pairs, for example {'a': 1}.", "tip": "The constructor dict() is another option.", "tags": ["python", "dict"], "id": 2},
        {"question": "What does len('flashcard') return?", "answer": "9", "tip": None, "tags": ["python", "strings"], "id": 3},  # type: ignore[typeddict-item]
        {"question": "What is the output type of range(5)?", "answer": "A range object.", "tip": "Convert it with list(range(5)) if needed.", "tags": ["python", "iteration"], "id": 4}
    ]
FLASHCARD_SAMPLE = Flashcard(
    question="What is a Python list?",
    answer="An ordered and mutable collection of elements.",
    tip="Lists use square brackets.",
    tags=["python", "basics"],
    id=-1)
INVALID_DECK: list[Flashcard] = [
        {"question": "What is a Python list?", "answer": "An ordered and mutable collection of elements.", "tip": "Lists use square brackets.", "tags": ["python", "basics"], "id": 4},
        {"question": "How do you create a dictionary in Python?", "answer": "Using curly braces with key value pairs, for example {'a': 1}.", "tip": "The constructor dict() is another option.", "tags": ["python", "dict"], "id": 2},
        {"question": "What does len('flashcard') return?", "answer": "9", "tip": None, "tags": ["python", "strings"], "id": 3},  # type: ignore[typeddict-item]
        {"question": "What is the output type of range(5)?", "answer": "A range object.", "tip": "Convert it with list(range(5)) if needed.", "tags": ["python", "iteration"], "id": 4}
    ]
