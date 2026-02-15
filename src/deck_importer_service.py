from pathlib import PurePosixPath
from urllib.parse import urlparse

from src import cardcreation
from src import deckimport


class DeckImporterService:
    """Logica di import di un mazzo remoto."""

    def import_from_url(self, url: str, deck_name: str) -> tuple[str, str]:
        """
        Importa un mazzo da URL e restituisce:
        - uno stato sintetico per la UI
        - il nome finale del mazzo, se disponibile
        """
        normalized_url = url.strip()
        if not normalized_url:
            return ("url_error", "")

        deck = deckimport.get_deck_from_link(normalized_url)
        if not deck:
            return ("invalid_deck", "")

        resolved_name = deck_name.strip() or self.name_from_url(normalized_url)
        if not resolved_name:
            return ("name_error", "")

        cardcreation.import_deck(deck, resolved_name)
        return ("success", resolved_name)

    def name_from_url(self, url: str) -> str:
        """Estrae un nome mazzo di fallback dal path finale dell'URL."""
        parsed = urlparse(url)
        filename = PurePosixPath(parsed.path).name
        if not filename.endswith(".json"):
            return ""
        return PurePosixPath(filename).stem
