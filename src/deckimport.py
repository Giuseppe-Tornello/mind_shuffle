import requests
from .data.constants import Flashcard
from .deckcheck import is_valid_deck, is_valid_deck_extension


def _convert_github_url_to_raw(url: str) -> str:
    if url.startswith("https://github.com/"):
        url = url.replace("github.com", "raw.githubusercontent.com", 1)
        url = url.replace("blob", "refs/heads", 1)
    return url


def get_deck_from_link(url: str) -> list[Flashcard]:
    EMPTY_DECK: list[Flashcard] = []
    if not is_valid_deck_extension(url):
        return EMPTY_DECK

    url = _convert_github_url_to_raw(url)

    try:
        response = requests.get(url, timeout=10)
        deck = response.json()
        if not is_valid_deck(deck):
            return EMPTY_DECK
        return deck
    except requests.RequestException:
        return EMPTY_DECK
