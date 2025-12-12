import requests
from .deckcheck import is_valid_deck, is_valid_deck_extension


def _convert_github_url_to_raw(url: str) -> str:
    if url.startswith("https://github.com/"):
        url = url.replace("github.com", "raw.githubusercontent.com", 1)
        url = url.replace("blob", "refs/heads", 1)
    return url


def get_deck_from_link(url: str) -> list:

    url = _convert_github_url_to_raw(url)
    EMPTY_DECK: list[dict] = []
    if not is_valid_deck_extension(url):
        return EMPTY_DECK

    response = requests.get(url, timeout=20)
    if response.status_code != 200:
        return EMPTY_DECK

    try:
        deck = response.json()
        if is_valid_deck(deck):
            return deck
        return EMPTY_DECK

    except requests.exceptions.JSONDecodeError:
        return EMPTY_DECK
