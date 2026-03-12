"""Constants used throughout the code"""
from typing import TypedDict

USER_PATH = "storage/user/"
DECKS_PATH = "storage/decks/"
DECKS_EXTENSION = ".json"
CARD_ATTRIBUTES = {"question", "answer", "tip", "tags", "id"}
OPTIONAL_ATTRIBUTES = {"tip"}
JSON_ENCODING = "utf-8"


class Flashcard(TypedDict):
    question: str
    answer: str
    tip: str
    tags: list[str]
    id: int
