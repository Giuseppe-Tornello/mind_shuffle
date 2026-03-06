import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DeckCreatorService:
    """Logic for creating an empty deck."""

    def normalize_name(self, deck_name: str) -> str:
        """Normalize the deck name before saving."""
        return deck_name.strip()

    def create_deck(self, deck_name: str, cards: list[dict] | None = None) -> str:
        """Create a deck and return the normalized file name."""
        normalized_name = self.normalize_name(deck_name)
        if not normalized_name:
            return ""
        deck_path = PROJECT_ROOT / "storage" / "decks" / f"{normalized_name}.json"
        with deck_path.open("w", encoding="utf-8") as deck_file:
            json.dump(cards or [], deck_file, ensure_ascii=False, indent=2)
        return normalized_name
