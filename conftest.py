"""Compatibilita' locale per l'opzione --cov quando pytest-cov non e' installato."""

import importlib.util


def pytest_addoption(parser) -> None:
    if importlib.util.find_spec("pytest_cov") is not None:
        return
    parser.addoption(
        "--cov",
        action="append",
        default=[],
        help="No-op compatibility option when pytest-cov is unavailable.",
    )
