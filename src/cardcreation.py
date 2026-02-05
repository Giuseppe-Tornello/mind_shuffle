import json
from pathlib import Path

from src.data.constants import DECKS_EXTENSION, DECKS_PATH, JSON_ENCODING

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _deck_name_to_path(name: str) -> Path:
    """formats the deck name into a full project-root-relative path"""
    return PROJECT_ROOT / DECKS_PATH / f"{name}{DECKS_EXTENSION}"


def card_from_strings(question: str, answer: str, tip: str | None, tags: list[str]) -> dict:
    """creates a flash card from the args"""

    card = {
        "question": question,
        "answer": answer,
        "tip": tip,
        "tags": tags,
        "id": None
    }
    return card


def write_card(card: dict, deck_name: str) -> None:
    """writes the choice card to the specified deck"""

    path = _deck_name_to_path(deck_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        deck = []
        next_id = 0

    else:
        with path.open("r", encoding=JSON_ENCODING) as f:
            try:
                deck = json.load(f)
                head = deck[len(deck) - 1]
                next_id = head.get("id") + 1

            except json.JSONDecodeError:
                # if the deck is not correctly formatted it's overwritten
                deck = []
                next_id = 0

    card.update({'id': next_id})
    deck.append(card)

    with path.open("w", encoding=JSON_ENCODING) as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)


def delete_card(card_id: int, deck_name: str) -> None:
    """deletes the specified card from a deck"""

    path = _deck_name_to_path(deck_name)

    if not path.exists():
        return

    with path.open("r", encoding=JSON_ENCODING) as f:
        try:
            deck = json.load(f)
        except json.JSONDecodeError:
            return

    for i, card in enumerate(deck, start=0):
        if card.get('id') == card_id:
            deck.pop(i)
            break

    with path.open("w", encoding=JSON_ENCODING) as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)


def import_deck(deck: list[dict], deck_name: str) -> None:
    """
    imports a whole deck locally. its intended use its related to
    remotely downloaded json files. it does not overwrite already existing decks
    with the same name.
    """

    path = _deck_name_to_path(deck_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    i = 0

    while path.exists():
        # needed to avoid overwriting other already locally existing decks
        i += 1
        path = _deck_name_to_path(deck_name + str(i))

    with path.open("w", encoding=JSON_ENCODING) as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)
