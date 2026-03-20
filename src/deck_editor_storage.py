import json
import logging
from json import JSONDecodeError
from pathlib import Path

from src.data.constants import Flashcard, JSON_ENCODING, JSON_INDENT
from src.deckcheck import is_valid_deck, is_valid_deck_file


LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DeckFileError(Exception):
    """Raised when a deck file cannot be safely loaded."""


def deck_directory() -> Path:
    """Return the folder containing persisted decks."""
    return PROJECT_ROOT / "storage" / "decks"


def normalize_deck_name(deck_name: str) -> str:
    """Normalize deck names before reading or writing files."""
    return deck_name.strip()


def deck_exists(deck_name: str) -> bool:
    """Check whether the deck file exists on disk."""
    normalized_name = normalize_deck_name(deck_name)
    if not normalized_name:
        return False
    return deck_file_path(normalized_name).exists()


def resolve_available_deck_name(deck_name: str) -> str:
    """Return a deck name that does not collide with an existing file."""
    normalized_name = normalize_deck_name(deck_name)
    if not normalized_name:
        return ""

    resolved_name = normalized_name
    suffix = 0
    while deck_exists(resolved_name):
        suffix += 1
        resolved_name = f"{normalized_name}{suffix}"
    return resolved_name


def load_deck_names() -> list[str]:
    """Return only decks whose files pass format validation."""
    deck_names: list[str] = []
    for deck_path in sorted(deck_directory().glob("*.json")):
        if is_valid_deck_file(str(deck_path)):
            deck_names.append(deck_path.stem)
    return deck_names


def load_deck_cards(deck_name: str) -> list[dict]:
    """Load a deck from disk and normalize each card for the editor."""
    raw_cards = read_deck_file(deck_file_path(deck_name), strict=True)
    cards: list[dict] = []
    for index, raw_card in enumerate(raw_cards, start=1):
        cards.append(normalize_card(raw_card, index))
    if not cards:
        cards = [empty_card(1)]
    return cards


def create_deck(deck_name: str, cards: list[dict] | None = None) -> str:
    """Create a deck file using a non-conflicting normalized name."""
    resolved_name = resolve_available_deck_name(deck_name)
    if not resolved_name:
        return ""
    write_deck_file(cards or [], deck_file_path(resolved_name))
    return resolved_name


def import_deck(deck: list[Flashcard], deck_name: str) -> str:
    """Persist an imported deck without overwriting an existing deck name."""
    if not normalize_deck_name(deck_name) or not is_valid_deck(deck):
        return ""

    resolved_name = resolve_available_deck_name(deck_name)
    write_deck_file(deck, deck_file_path(resolved_name))
    return resolved_name


def add_card_to_deck(card: dict, deck_name: str) -> None:
    """Append a card to the specified deck, assigning the next sequential id."""
    normalized_name = normalize_deck_name(deck_name)
    if not normalized_name:
        return

    deck = read_deck_file(deck_file_path(normalized_name))
    next_id = 1
    if is_valid_deck(deck):
        next_id = int(deck[-1].get("id", 0)) + 1
    else:
        deck = []

    card_to_save = dict(card)
    card_to_save["id"] = next_id
    deck.append(card_to_save)
    write_deck_file(deck, deck_file_path(normalized_name))


def delete_card_from_deck(card_id: int, deck_name: str) -> None:
    """Delete the specified card from a persisted deck."""
    normalized_name = normalize_deck_name(deck_name)
    if not normalized_name:
        return

    deck = read_deck_file(deck_file_path(normalized_name))
    if not is_valid_deck(deck):
        LOGGER.exception("Cannot delete card from deck named '%s'", normalized_name)
        return

    for index, card in enumerate(deck):
        if card.get("id") == card_id:
            deck.pop(index)
            break

    write_deck_file(deck, deck_file_path(normalized_name))


def rename_deck(old_name: str, new_name: str) -> bool:
    """Rename a deck by saving a new copy first and then removing the old file."""
    normalized_old_name = normalize_deck_name(old_name)
    normalized_new_name = normalize_deck_name(new_name)
    if not normalized_old_name or not normalized_new_name:
        return False
    if normalized_old_name == normalized_new_name:
        return True
    if deck_exists(normalized_new_name):
        return False

    cards = read_deck_file(deck_file_path(normalized_old_name))
    write_deck_file(cards, deck_file_path(normalized_new_name))
    delete_deck(normalized_old_name)
    return True


def delete_deck(deck_name: str) -> None:
    """Delete the deck file if it exists."""
    deck_path = deck_file_path(deck_name)
    if deck_path.exists():
        deck_path.unlink()


def deck_file_path(deck_name: str) -> Path:
    """Build the absolute path to the JSON file associated with the deck."""
    normalized_name = normalize_deck_name(deck_name)
    return deck_directory() / f"{normalized_name}.json"


def read_deck_file(path: str | Path, strict: bool = False) -> list[dict]:
    """Read deck JSON from disk, optionally failing loudly on malformed files."""
    deck_path = Path(path)
    try:
        with deck_path.open("r", encoding=JSON_ENCODING) as deck_file:
            data = json.load(deck_file)
            if isinstance(data, list):
                return data
            if strict:
                raise DeckFileError(f"Deck file does not contain a list: {deck_path}")
            return []
    except (FileNotFoundError, OSError, JSONDecodeError):
        if strict:
            raise DeckFileError(f'Unable to read file in path "{deck_path}"') from None
        LOGGER.exception('Unable to read file in path "%s"', deck_path)
        return []


def write_deck_file(deck: list[dict], path: str | Path) -> None:
    """Write deck JSON to disk using the project encoding and indentation."""
    deck_path = Path(path)
    deck_path.parent.mkdir(parents=True, exist_ok=True)
    with deck_path.open("w", encoding=JSON_ENCODING) as deck_file:
        json.dump(deck, deck_file, ensure_ascii=False, indent=JSON_INDENT)


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
