import requests
from urllib.parse import urlparse

from src.deckcheck import is_valid_deck, is_valid_deck_extension


def _convert_github_url_to_raw(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc != "github.com":
        return url

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 5 and parts[2] == "blob":
        owner, repo, _, branch = parts[:4]
        raw_path = "/".join(parts[4:])
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{raw_path}"
    return url


def get_deck_from_link(url: str) -> list:
    url = _convert_github_url_to_raw(url)
    EMPTY_DECK: list[dict] = []
    if not is_valid_deck_extension(url):
        return EMPTY_DECK

    try:
        response = requests.get(url, timeout=20)
    except requests.RequestException:
        return EMPTY_DECK

    if response.status_code != 200:
        return EMPTY_DECK

    try:
        deck = response.json()
        if is_valid_deck(deck):
            return deck
        return EMPTY_DECK

    except ValueError:
        return EMPTY_DECK
