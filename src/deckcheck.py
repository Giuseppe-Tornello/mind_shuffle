import json
from .data.constants import CARD_ATTRIBUTES, OPTIONAL_ATTRIBUTES, JSON_ENCODING, DECKS_EXTENSION


def is_valid_deck(deck: list[dict]) -> bool:
    """checks if the deck is valid"""
    if deck is None:
        return False

    previous_id = -1
    mandatory_attributes = CARD_ATTRIBUTES - OPTIONAL_ATTRIBUTES
    for card in deck:
        wrong_attributes = set(card.keys()) != CARD_ATTRIBUTES

        # Checks if all attributes are null or empty, OPTIONAL_ATTRIBUTES excluded
        has_empty_values = not all(card[attr] for attr in mandatory_attributes)

        # current card id MUST be < than previous card
        if wrong_attributes or has_empty_values or card["id"] <= previous_id:
            return False

        previous_id = card["id"]

    return True


def is_valid_deck_file(path: str) -> bool:
    """opens file path and checks if deck is valid"""
    if not is_valid_deck_extension(path):
        return False

    with open(path, "r", encoding=JSON_ENCODING) as f:
        try:
            deck = json.load(f)
            if not isinstance(deck, list):
                return False
            return is_valid_deck(deck)

        except json.JSONDecodeError:
            return False


def is_valid_deck_extension(path: str) -> bool:
    if path.endswith(DECKS_EXTENSION):
        return True
    return False
