from pathlib import Path
import json

from src.deckcheck import is_valid_deck_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_deck_names() -> list[str]:
    """Return only decks whose files pass format validation."""
    deck_dir = PROJECT_ROOT / "storage" / "decks"
    deck_names: list[str] = []
    for deck_path in sorted(deck_dir.glob("*.json")):
        if is_valid_deck_file(str(deck_path)):
            deck_names.append(deck_path.stem)
    return deck_names


def load_deck_cards(deck_name: str) -> list[dict]:
    """Load a deck from disk and normalize each card for the editor."""
    raw_cards = load_raw_deck_cards(deck_name)
    cards: list[dict] = []
    for index, raw_card in enumerate(raw_cards, start=1):
        cards.append(normalize_card(raw_card, index))
    if not cards:
        cards = [empty_card(1)]
    return cards


def load_raw_deck_cards(deck_name: str) -> list[dict]:
    """Load raw deck contents without transforming cards for copy/import flows."""
    deck_path = deck_file_path(deck_name)
    with deck_path.open("r", encoding="utf-8") as deck_file:
        return json.load(deck_file)


def save_deck_cards(deck_name: str, cards: list[dict]) -> None:
    """Persist the entire deck exactly as kept by the editor session."""
    deck_path = deck_file_path(deck_name)
    with deck_path.open("w", encoding="utf-8") as deck_file:
        json.dump(cards, deck_file, ensure_ascii=False, indent=2)


def rename_deck(old_name: str, new_name: str) -> bool:
    """Rename a deck by saving a new copy first and then removing the old file."""
    normalized_new_name = new_name.strip()
    if not old_name or not normalized_new_name:
        return False
    cards = load_raw_deck_cards(old_name)
    save_deck_cards(normalized_new_name, cards)
    if old_name != normalized_new_name:
        delete_deck(old_name)
    return True


def delete_deck(deck_name: str) -> None:
    """Delete the deck file if it exists."""
    deck_path = deck_file_path(deck_name)
    if deck_path.exists():
        deck_path.unlink()


def deck_file_path(deck_name: str) -> Path:
    """Build the absolute path to the JSON file associated with the deck."""
    return PROJECT_ROOT / "storage" / "decks" / f"{deck_name}.json"


def normalize_card(raw_card: dict, card_id: int) -> dict:
    """Normalize a card loaded from JSON for UI and session usage."""
    return {
        "question": str(raw_card.get("question", "")).strip(),
        "answer": str(raw_card.get("answer", "")).strip(),
        "tip": raw_card.get("tip"),
        "tags": list(raw_card.get("tags") or []),
        "id": raw_card.get("id", card_id),
    }


def empty_card(card_id: int) -> dict:
    """Factory used by the editor for new cards or empty decks."""
    return {
        "question": "",
        "answer": "",
        "tip": None,
        "tags": [],
        "id": card_id,
    }
