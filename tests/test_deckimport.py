import requests
from _pytest.monkeypatch import MonkeyPatch

from src.deck_importer_service import DeckImporterService
from tests.test_constants import VALID_DECK


class _ResponseStub:
    def __init__(self, payload: object, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

    def json(self) -> object:
        return self._payload


def test_convert_github_url_to_raw() -> None:
    service = DeckImporterService()
    to_parse = "https://github.com/Giuseppe-Tornello/mind_shuffle/blob/P_tests/tests/test_decks/valid_deck1.json"
    parsed = "https://raw.githubusercontent.com/Giuseppe-Tornello/mind_shuffle/refs/heads/P_tests/tests/test_decks/valid_deck1.json"  # noqa: E501

    assert (
        service._convert_github_url_to_raw(to_parse)  # pylint: disable=protected-access
        == parsed
    )
    assert (
        service._convert_github_url_to_raw("") == ""  # pylint: disable=protected-access
    )


def test_get_deck_from_link_returns_valid_deck(monkeypatch: MonkeyPatch) -> None:
    service = DeckImporterService()

    def fake_get(*_args: object, **_kwargs: object) -> _ResponseStub:
        return _ResponseStub(VALID_DECK)

    monkeypatch.setattr("src.deck_importer_service.requests.get", fake_get)

    valid_raw_url = "https://example.com/valid_deck.json"
    assert service.get_deck_from_link(valid_raw_url) == VALID_DECK

    valid_url = "https://github.com/example/repo/blob/main/valid_deck.json"
    assert service.get_deck_from_link(valid_url) == VALID_DECK


def test_get_deck_from_link_rejects_invalid_inputs(monkeypatch: MonkeyPatch) -> None:
    service = DeckImporterService()

    def raise_timeout(*_args: object, **_kwargs: object) -> None:
        raise requests.Timeout("network timeout")

    monkeypatch.setattr("src.deck_importer_service.requests.get", raise_timeout)

    invalid_url_list = [
        "https://example.com/deck.html",
        "https://example.com/deck.json",
    ]

    assert service.get_deck_from_link(invalid_url_list[0]) == []
    assert service.get_deck_from_link(invalid_url_list[1]) == []


def test_get_deck_from_link_rejects_invalid_deck_payload(
    monkeypatch: MonkeyPatch,
) -> None:
    service = DeckImporterService()

    def fake_get(*_args: object, **_kwargs: object) -> _ResponseStub:
        return _ResponseStub([{"question": "missing required fields"}])

    monkeypatch.setattr("src.deck_importer_service.requests.get", fake_get)

    assert service.get_deck_from_link("https://example.com/invalid_deck.json") == []
