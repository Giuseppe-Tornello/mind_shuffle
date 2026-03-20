from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from src.deck_editor_session import DeckEditorSession
from src.deck_editor_storage import create_deck, deck_file_path
from tests.test_constants import VALID_DECK


def test_newly_created_empty_deck_can_be_loaded_and_saved(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    deck_name = create_deck("demo", [])
    session = DeckEditorSession(initial_deck_name=deck_name)

    assert session.selected_or_first_deck() == "demo"
    assert session.load_selected_deck(deck_name) is True
    assert session.deck_name == "demo"
    assert session.save_deck("Q", "A", "", "") == "saved"


def test_load_selected_deck_fails_for_corrupted_json(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    broken_path = deck_file_path("broken")
    broken_path.parent.mkdir(parents=True, exist_ok=True)
    broken_path.write_text("{bad json", encoding="utf-8")

    session = DeckEditorSession(initial_deck_name="broken")

    assert session.load_selected_deck("broken") is False
    assert session.deck_name == ""
    assert session.cards == []


def test_load_selected_deck_keeps_valid_cards(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    create_deck("valid", VALID_DECK)
    session = DeckEditorSession(initial_deck_name="valid")

    assert session.load_selected_deck("valid") is True
    assert len(session.cards) == len(VALID_DECK)
