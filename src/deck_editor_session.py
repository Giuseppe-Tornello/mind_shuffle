import json

from src.deck_editor_storage import (
    delete_deck,
    empty_card,
    load_deck_cards,
    load_deck_names,
    save_deck_cards,
)


class DeckEditorSession:
    """Stato e logica dell'editor mazzi."""

    def __init__(self, initial_deck_name: str = "") -> None:
        self.initial_deck_name = initial_deck_name
        self.decks = load_deck_names()
        self.deck_name = ""
        self.original_cards: list[dict] = []
        self.cards: list[dict] = []
        self.current_index = 0
        self.is_dirty = False

    def has_unsaved_changes(self) -> bool:
        return self.is_dirty

    def has_decks(self) -> bool:
        return bool(self.decks)

    def selected_or_first_deck(self) -> str:
        """Preferisce il mazzo richiesto dal caller, altrimenti usa il primo disponibile."""
        if self.initial_deck_name in self.decks:
            return self.initial_deck_name
        if self.decks:
            return self.decks[0]
        return ""

    def load_selected_deck(self, deck_name: str) -> bool:
        """Carica il mazzo reale e ne prepara una working copy modificabile in memoria."""
        try:
            loaded_cards = load_deck_cards(deck_name)
        except (OSError, json.JSONDecodeError):
            return False
        self.original_cards = [card.copy() for card in loaded_cards]
        self.cards = [card.copy() for card in loaded_cards]
        self.deck_name = deck_name
        self.current_index = 0
        self.is_dirty = False
        return True

    def current_card(self) -> dict:
        if not self.cards:
            return empty_card(1)
        return self.cards[self.current_index]

    def progress(self) -> tuple[int, int]:
        if not self.cards:
            return (0, 0)
        return (self.current_index + 1, len(self.cards))

    def go_to_card(self, card_number: int) -> bool:
        """Posiziona l'editor su una carta specifica usando numerazione 1-based."""
        if not self.cards:
            return False
        if card_number < 1 or card_number > len(self.cards):
            return False
        self.current_index = card_number - 1
        return True

    def save_current_card_fields(
        self,
        question: str,
        answer: str,
        tip: str,
        tags_text: str,
    ) -> None:
        # La UI passa stringhe grezze; la sessione si occupa di normalizzarle
        # nel formato persistito su disco.
        if not self.cards:
            return
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        self.cards[self.current_index] = {
            "question": question.strip(),
            "answer": answer.strip(),
            "tip": tip.strip() or None,
            "tags": tags,
            "id": self.cards[self.current_index].get("id", self.current_index + 1),
        }

    def previous_card(self) -> None:
        if not self.cards:
            return
        self.current_index = (self.current_index - 1) % len(self.cards)

    def next_card(self) -> None:
        if not self.cards:
            return
        self.current_index = (self.current_index + 1) % len(self.cards)

    def add_card(self) -> None:
        """Aggiunge una carta vuota e la rende quella attiva."""
        self.cards.append(empty_card(len(self.cards) + 1))
        self.current_index = len(self.cards) - 1
        self.is_dirty = True

    def remove_current_card(self) -> None:
        """Rimuove la carta attiva dalla working copy senza toccare il file reale."""
        if not self.cards:
            return
        if len(self.cards) == 1:
            self.cards = [empty_card(1)]
            self.current_index = 0
            self.is_dirty = True
            return
        self.cards.pop(self.current_index)
        if self.current_index >= len(self.cards):
            self.current_index = len(self.cards) - 1
        self.is_dirty = True

    def discard_changes(self) -> None:
        """Ripristina la working copy all'ultima versione confermata su disco."""
        self.cards = [card.copy() for card in self.original_cards]
        if not self.cards:
            self.cards = [empty_card(1)]
        if self.current_index >= len(self.cards):
            self.current_index = len(self.cards) - 1
        self.is_dirty = False

    def change_selected_deck(self, step: int) -> bool:
        """Scorre ciclicamente i mazzi, ma solo se non ci sono modifiche pendenti."""
        if len(self.decks) <= 1 or self.is_dirty:
            return False
        current_index = self.decks.index(self.deck_name) if self.deck_name in self.decks else 0
        next_index = (current_index + step) % len(self.decks)
        return self.load_selected_deck(self.decks[next_index])

    def save_deck(
        self,
        question: str,
        answer: str,
        tip: str,
        tags_text: str,
    ) -> str:
        """
        Salva il mazzo attivo sovrascrivendo il file reale con la working copy.
        """
        self.save_current_card_fields(question, answer, tip, tags_text)
        if not self.deck_name:
            return "name_error"
        if not self.cards_are_valid():
            return "card_error"

        # Solo qui la working copy diventa definitiva e sovrascrive il file reale.
        save_deck_cards(self.deck_name, self.cards)
        self.decks = load_deck_names()
        self.original_cards = [card.copy() for card in self.cards]
        self.is_dirty = False
        return "saved"

    def delete_current_deck(self) -> str:
        """Elimina il mazzo attivo e, se possibile, seleziona il successivo disponibile."""
        if not self.deck_name:
            return "delete_error"

        deleted_name = self.deck_name
        delete_deck(self.deck_name)
        self.decks = load_deck_names()
        self.original_cards = []
        self.cards = []
        self.current_index = 0
        self.deck_name = ""
        self.is_dirty = False

        if self.decks:
            self.load_selected_deck(self.decks[0])
        return deleted_name

    def cards_are_valid(self) -> bool:
        """Valida le carte e riallinea gli id prima del salvataggio."""
        for index, card in enumerate(self.cards, start=1):
            if not card["question"] or not card["answer"]:
                return False
            card["id"] = index
        return True
