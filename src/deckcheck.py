from .data.constants import CARD_ATTRIBUTES, OPTIONAL_ATTRIBUTES


def check_deck(deck: list[dict]) -> bool:
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
        if wrong_attributes or has_empty_values and card["id"] <= previous_id:
            return False

        previous_id = card["id"]

    return True
