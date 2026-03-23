from src.data.constants import Flashcard


class QuestionSession:
    """State and logic for the training session."""

    def __init__(self, cards: list[Flashcard] | None = None) -> None:
        self.cards: list[Flashcard] = [
            {
                "question": card["question"],
                "answer": card["answer"],
                "tip": card["tip"],
                "tags": card["tags"],
                "id": card["id"],
            }
            for card in cards
        ] if cards else []
        self.current_index = 0
        self.answer_visible = False
        self._score = {"correct": 0, "wrong": 0}
        self.user_answers: dict[int, str] = {}
        self.evaluated_questions: dict[int, bool] = {}
        self.results_requested = False

    @property
    def correct_answers(self) -> int:
        return self._score["correct"]

    @property
    def wrong_answers(self) -> int:
        return self._score["wrong"]

    def has_cards(self) -> bool:
        return bool(self.cards)

    def current_card(self) -> Flashcard:
        return self.cards[self.current_index]

    def current_answer_text(self) -> str:
        return self.user_answers.get(self.current_index, "")

    def save_user_answer(self, value: str) -> None:
        self.user_answers[self.current_index] = value

    def reveal_answer(self) -> None:
        self.answer_visible = True

    def previous_question(self) -> None:
        if not self.cards:
            return
        self.current_index = (self.current_index - 1) % len(self.cards)
        self.answer_visible = False

    def next_question(self) -> None:
        if not self.cards:
            return
        self.current_index = (self.current_index + 1) % len(self.cards)
        self.answer_visible = False

    def current_question_answered(self) -> bool:
        return self.evaluated_questions.get(self.current_index, False)

    def register_answer(self, is_correct: bool) -> bool:
        if self.current_question_answered():
            return False

        if is_correct:
            self._score["correct"] += 1
        else:
            self._score["wrong"] += 1
        self.evaluated_questions[self.current_index] = True
        return True

    def all_answered(self) -> bool:
        return len(self.evaluated_questions) == len(self.cards)

    def mark_results_requested(self) -> bool:
        if self.results_requested:
            return False
        self.results_requested = True
        return True
