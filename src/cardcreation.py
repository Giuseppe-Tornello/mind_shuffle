from json import load, dump, JSONDecodeError
from os import path
from .data.constants import JSON_ENCODING, DECKS_PATH, DECKS_EXTENSION


def _deck_name_to_path(name: str) -> str:
    """formats the deck name into a full relative path"""
    return DECKS_PATH + name + DECKS_EXTENSION


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

    if not path.exists(path):
        deck = []
        next_id = 0

    else:
        with open(path, "r", encoding=JSON_ENCODING) as f:
            try:
                deck = load(f)
                head = deck[len(deck) - 1]
                next_id = head.get("id") + 1

            except JSONDecodeError:
                # if the deck is not correctly formatted it's overwritten
                deck = []
                next_id = 0

    card.update({'id': next_id})
    deck.append(card)

    with open(path, "w", encoding=JSON_ENCODING) as f:
        dump(deck, f, ensure_ascii=False, indent=2)


def delete_card(card_id: int, deck_name: str) -> None:
    """deletes the specified card from a deck"""

    path = _deck_name_to_path(deck_name)

    if not path.exists(path):
        return

    with open(path, "r", encoding=JSON_ENCODING) as f:
        try:
            deck = load(f)
        except JSONDecodeError:
            return

    for i, card in enumerate(deck, start=0):
        if card.get('id') == card_id:
            deck.pop(i)
            break

    with open(path, "w", encoding=JSON_ENCODING) as f:
        dump(deck, f, ensure_ascii=False, indent=2)


def import_deck(deck: list[dict], deck_name: str) -> None:
    """
    imports a whole deck locally. its intended use its related to
    remotely downloaded json files. it does not overwrite already existing decks
    with the same name.
    """

    path = _deck_name_to_path(deck_name)
    i = 0

    while path.exists(path):
        # needed to avoid overwriting other already locally existing decks
        i += 1
        path = _deck_name_to_path(deck_name + str(i))

    with open(path, "w", encoding=JSON_ENCODING) as f:
        dump(deck, f, ensure_ascii=False, indent=2)
