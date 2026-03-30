import json
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from src.data.constants import JSON_ENCODING
from src.deck_editor_storage import (
    add_card_to_deck,
    create_deck,
    deck_file_path,
    delete_card_from_deck,
    import_deck,
    read_deck_file,
    rename_deck,
    write_deck_file,
)
from tests.test_constants import FLASHCARD_SAMPLE, INVALID_DECK, VALID_DECK


def test_deck_file_path_uses_project_storage(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    assert (
        deck_file_path("test_deck") == tmp_path / "storage" / "decks" / "test_deck.json"
    )


def test_read_deck_file(tmp_path: Path) -> None:
    deck_path = tmp_path / "valid_deck.json"
    deck_path.write_text(json.dumps(VALID_DECK), encoding=JSON_ENCODING)

    assert read_deck_file(deck_path) == VALID_DECK
    assert read_deck_file(tmp_path / "missing.json") == []


def test_write_deck_file(tmp_path: Path) -> None:
    deck_path = tmp_path / "test_deck.json"
    write_deck_file(VALID_DECK, deck_path)

    assert deck_path.is_file() is True

    with deck_path.open("r", encoding=JSON_ENCODING) as deck_file:
        data = json.load(deck_file)

    assert data == VALID_DECK


def test_create_deck_writes_normalized_name(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    created_name = create_deck("  demo  ", VALID_DECK)

    assert created_name == "demo"
    assert deck_file_path("demo").is_file() is True


def test_create_deck_avoids_overwriting_existing_name(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    first_name = create_deck("demo", VALID_DECK)
    second_name = create_deck("demo", INVALID_DECK)

    assert first_name == "demo"
    assert second_name == "demo1"
    assert read_deck_file(deck_file_path(first_name)) == VALID_DECK
    assert read_deck_file(deck_file_path(second_name)) == INVALID_DECK


def test_import_deck_avoids_overwriting_existing_name(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    first_name = import_deck(VALID_DECK, "test_import")
    second_name = import_deck(VALID_DECK, "test_import")

    assert first_name == "test_import"
    assert second_name == "test_import1"
    assert deck_file_path(first_name).is_file() is True
    assert deck_file_path(second_name).is_file() is True
    assert import_deck(INVALID_DECK, "invalid_import") == ""


def test_rename_deck_rejects_existing_target(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)

    create_deck("source", VALID_DECK)
    create_deck("target", INVALID_DECK)

    assert rename_deck("source", "target") is False
    assert read_deck_file(deck_file_path("source")) == VALID_DECK
    assert read_deck_file(deck_file_path("target")) == INVALID_DECK


def test_delete_card_from_deck(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)
    create_deck("test_delete", VALID_DECK)

    assert find_id(4, deck_file_path("test_delete")) is True
    delete_card_from_deck(4, "test_delete")
    assert find_id(4, deck_file_path("test_delete")) is False

    create_deck("invalid_delete", INVALID_DECK)
    assert find_id(2, deck_file_path("invalid_delete")) is True
    delete_card_from_deck(2, "invalid_delete")
    assert find_id(2, deck_file_path("invalid_delete")) is True


def test_add_card_to_deck(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("src.deck_editor_storage.PROJECT_ROOT", tmp_path)
    create_deck("test_write", VALID_DECK)

    assert find_id(5, deck_file_path("test_write")) is False
    add_card_to_deck(FLASHCARD_SAMPLE, "test_write")
    assert find_id(5, deck_file_path("test_write")) is True

    create_deck("invalid_write", INVALID_DECK)
    assert find_id(2, deck_file_path("invalid_write")) is True
    add_card_to_deck(FLASHCARD_SAMPLE, "invalid_write")
    assert find_id(1, deck_file_path("invalid_write")) is True
    assert find_id(2, deck_file_path("invalid_write")) is False


def find_id(card_id: int, deck_path: Path) -> bool:
    with deck_path.open("r", encoding=JSON_ENCODING) as deck_file:
        data = json.load(deck_file)
    for item in data:
        if isinstance(item, dict) and item.get("id") == card_id:
            return True
    return False
