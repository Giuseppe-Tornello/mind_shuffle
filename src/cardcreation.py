import json
import os


def card_from_strings(question:str, answer:str, tip:str|None, tags:list[str]) -> dict:
    """creates a flash card from the args"""

    card = {
        "question": question,
        "answer": answer,
        "tip": tip,
        "tags": tags,
        "id" : None
    }
    return card



