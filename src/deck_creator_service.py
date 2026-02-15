import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DeckCreatorService:
    """Logica di creazione di un mazzo vuoto."""

    def normalize_name(self, deck_name: str) -> str:
        """Normalizza il nome del mazzo prima del salvataggio."""
        return deck_name.strip()

    def create_deck(self, deck_name: str, cards: list[dict] | None = None) -> str:
        """Crea un mazzo e restituisce il nome normalizzato del file creato."""
        normalized_name = self.normalize_name(deck_name)
        if not normalized_name:
            return ""
        deck_path = PROJECT_ROOT / "storage" / "decks" / f"{normalized_name}.json"
        with deck_path.open("w", encoding="utf-8") as deck_file:
            json.dump(cards or [], deck_file, ensure_ascii=False, indent=2)
        return normalized_name
