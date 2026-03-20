from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
import requests
from src import cardcreation

from src.deck_creator_service import DeckCreatorService
from src.deck_importer_service import DeckImporterService
from src.ui.question_session import QuestionSession


def test_create_deck_writes_normalized_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("src.deck_creator_service.PROJECT_ROOT", tmp_path)
    decks_dir = tmp_path / "storage" / "decks"
    decks_dir.mkdir(parents=True)

    created_name = DeckCreatorService().create_deck("  demo  ", cards=[{"question": "Q", "answer": "A"}])

    assert created_name == "demo"
    assert (decks_dir / "demo.json").exists()


def test_import_from_url_returns_invalid_deck_on_request_error(monkeypatch: MonkeyPatch) -> None:
    def raise_timeout(*_args: object, **_kwargs: object) -> None:
        raise requests.Timeout("network timeout")

    monkeypatch.setattr("src.deckimport.requests.get", raise_timeout)

    result, deck_name = DeckImporterService().import_from_url(
        "https://example.com/deck.json",
        "",
    )

    assert result == "invalid_deck"
    assert deck_name == ""


def test_import_deck_writes_under_project_root(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    decks_dir = tmp_path / "storage" / "decks"
    decks_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("src.cardcreation.DECKS_PATH", f"{decks_dir}/")

    monkeypatch.setattr("src.cardcreation.is_valid_deck", lambda _: True)

    cardcreation.import_deck(
        [{"question": "Q", "answer": "A", "tip": "", "tags": [], "id": 0}],
        "remote_deck",
    )

    assert (decks_dir / "remote_deck.json").exists()


def test_question_session_tracks_score_once_per_question() -> None:
    session = QuestionSession(cards=[{"question": "Q1", "answer": "A1", "tip": "", "tags": [], "id": 0}])

    assert session.register_answer(is_correct=True) is True
    assert session.register_answer(is_correct=False) is False
    assert session.correct_answers == 1
    assert session.wrong_answers == 0
