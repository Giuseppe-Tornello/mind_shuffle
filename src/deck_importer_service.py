import logging
from pathlib import PurePosixPath
from urllib.parse import urlparse

import requests

from src.data.constants import Flashcard
from src.deckcheck import is_valid_deck, is_valid_deck_extension
from src.deck_editor_storage import import_deck


LOGGER = logging.getLogger(__name__)


class DeckImporterService:
    """Logic for importing a remote deck."""

    def import_from_url(self, url: str, deck_name: str) -> tuple[str, str]:
        """
        Import a deck from a URL and return:
        - a compact UI status code
        - the final deck name, when available
        """
        normalized_url = url.strip()
        if not normalized_url:
            return ("url_error", "")

        deck = self.get_deck_from_link(normalized_url)
        if not deck:
            return ("invalid_deck", "")

        resolved_name = deck_name.strip() or self.name_from_url(normalized_url)
        if not resolved_name:
            return ("name_error", "")

        imported_name = import_deck(deck, resolved_name)
        if not imported_name:
            return ("invalid_deck", "")
        return ("success", imported_name)

    def name_from_url(self, url: str) -> str:
        """Extract a fallback deck name from the final URL path."""
        parsed = urlparse(url)
        filename = PurePosixPath(parsed.path).name
        if not filename.endswith(".json"):
            return ""
        return PurePosixPath(filename).stem

    def get_deck_from_link(self, url: str) -> list[Flashcard]:
        """Download a remote deck and validate its JSON structure."""
        empty_deck: list[Flashcard] = []
        if not is_valid_deck_extension(url):
            LOGGER.warning("Rejected deck import from non-json url: %s", url)
            return empty_deck

        raw_url = self._convert_github_url_to_raw(url)
        try:
            response = requests.get(raw_url, timeout=10)
            response.raise_for_status()
            deck = response.json()
        except (requests.RequestException, ValueError):
            return empty_deck

        if not isinstance(deck, list) or not is_valid_deck(deck):
            return empty_deck
        return deck

    def _convert_github_url_to_raw(self, url: str) -> str:
        """Convert a GitHub blob URL into its raw counterpart."""
        if url.startswith("https://github.com/"):
            url = url.replace("github.com", "raw.githubusercontent.com", 1)
            url = url.replace("blob", "refs/heads", 1)
        return url
