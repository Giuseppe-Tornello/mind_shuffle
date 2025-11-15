import json
import os

def card_from_strings(question:str, answer:str, tip:str|None, tags:list[str]) -> dict:
    card = {
        "question": question,
        "answer": answer,
        "tip": tip,
        "tags": tags,
        "id" : None
    }
    return card


def write_card_to_deck(card, deck_name:str) -> None:
    path = "./data/decks/" + deck_name + ".json"

    if not os.path.exists(path):
        deck = []

    else:
        with open(path, "r", encoding="utf-8") as f:
            try:
                deck = json.load(f)
                head = deck[len(deck)-1]
                next_id = head.get('id') + 1
            
            except json.JSONDecodeError:
                deck = []
                next_id = 0
    card.update({'id': next_id})
    deck.append(card)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=4)

