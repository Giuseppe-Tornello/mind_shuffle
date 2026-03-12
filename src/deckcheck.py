from json import load, JSONDecodeError
from .data.constants import CARD_ATTRIBUTES, OPTIONAL_ATTRIBUTES, JSON_ENCODING, DECKS_EXTENSION, Flashcard


def is_valid_deck(deck: list[Flashcard]) -> bool:
    """checks if the deck is valid"""
    if len(deck) == 0:
        return False

    previous_id = 0
    mandatory_attributes = CARD_ATTRIBUTES - OPTIONAL_ATTRIBUTES
    for card in deck:
        wrong_attributes = set(card.keys()) != CARD_ATTRIBUTES
        if wrong_attributes:
            return False

        # Checks if all attributes are null or empty, OPTIONAL_ATTRIBUTES excluded
        has_empty_values = not all(card[attr] for attr in mandatory_attributes)  # type: ignore[literal-required]

        # current card id MUST be < than previous card
        if has_empty_values or card["id"] <= previous_id:
            return False

        previous_id = card["id"]

    return True


def is_valid_deck_file(path: str) -> bool:
    """opens file path and checks if deck is valid"""
    if not is_valid_deck_extension(path):
        return False

    try:
        with open(path, "r", encoding=JSON_ENCODING) as f:
            deck = load(f)
            if not isinstance(deck, list):
                return False
            return is_valid_deck(deck)

    except (FileNotFoundError, OSError):
        return False

    except JSONDecodeError:
        return False


def is_valid_deck_extension(path: str) -> bool:
    return path.endswith(DECKS_EXTENSION)
