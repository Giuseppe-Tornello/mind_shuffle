from src.data.constants import Flashcard


def normalize_question_cards(cards: object) -> list[Flashcard]:
    """Normalize raw card-like objects for question/review flows."""
    if not isinstance(cards, list):
        return []

    normalized_cards: list[Flashcard] = []
    for raw_card in cards:
        if not isinstance(raw_card, dict):
            continue

        question = raw_card.get("question")
        answer = raw_card.get("answer")
        tip = raw_card.get("tip", "")
        if not isinstance(question, str) or not isinstance(answer, str):
            continue
        if not isinstance(tip, str):
            tip = ""

        question = question.strip()
        answer = answer.strip()
        tip = tip.strip()
        if not question or not answer:
            continue

        normalized_cards.append({
            "question": question,
            "answer": answer,
            "tip": tip,
            "tags": [],
            "id": 0,
        })

    return normalized_cards
