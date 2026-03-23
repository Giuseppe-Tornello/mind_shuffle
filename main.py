"""Main application entry point."""
# pylint: disable=too-many-public-methods

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.events import Key
from textual.widget import Widget
from textual.widgets import ListView, Select, Static

from src.data.constants import Flashcard

from src.ui import ui_constants
from src.ui.deck_creator import DeckCreator
from src.ui.deck_editor import DeckEditor
from src.ui.deck_manager import DeckManager
from src.ui.deck_manager_actions import DeckManagerActions
from src.ui.home_view import HomeView
from src.ui.deck_importer import DeckImporter
from src.ui.deck_selector import DeckSelector
from src.ui.question_menu import QuestionMenu
from src.ui.show_results import ShowResults
from src.ui.side_menu import SideMenu


STATIC_WIDGET_BUILDERS = {
    "home": HomeView,
    "deck_selector": DeckSelector,
    "deck_manager": DeckManager,
    "deck_creator": DeckCreator,
    "deck_editor": DeckEditor,
    "deck_importer": DeckImporter,
}


def unknown_content_widget(content_type: str) -> Static:
    return Static(ui_constants.UNKNOWN_CONTENT_TYPE.format(type_name=content_type))


def normalize_question_cards(cards: object) -> list[Flashcard]:
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

        normalized_cards.append({
            "question": question,
            "answer": answer,
            "tip": tip,
            "tags": [],
            "id": 0,
        })

    return normalized_cards


def menu_widget(data: dict[str, object]) -> Widget:
    content_type = str(data["type"])
    if content_type == "text":
        return Static(str(data["content"]))
    if content_type == "question_menu":
        return QuestionMenu(normalize_question_cards(data.get("cards", [])))

    widget_builder = STATIC_WIDGET_BUILDERS.get(content_type)
    if widget_builder is None:
        return unknown_content_widget(content_type)
    return widget_builder()


class MainApp(App):
    """Main app with routing, layout, and focus management."""

    CSS_PATH = str(Path(__file__).resolve().parent / "src" / "ui" / "style.tcss")
    BINDINGS = [
        ("ctrl+left", "focus_sidebar", "Sidebar"),
        ("ctrl+right", "focus_content", "Content"),
        ("ctrl+up", "block_previous", "Previous In Block"),
        ("ctrl+down", "block_next", "Next In Block"),
        ("ctrl+delete", "focus_sidebar", "Focus Sidebar"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.active_block = "sidebar"

    def compose(self) -> ComposeResult:
        with Horizontal(id="main"):
            yield SideMenu()
            with Container(id="content"):
                with VerticalScroll(id="content_scroll"):
                    yield Static(ui_constants.SELECT_MENU_ITEM, id="content_placeholder")

    def on_side_menu_menu_chosen(self, event: SideMenu.MenuChosen) -> None:
        self.show_screen(event.menu_name, focus_content=event.focus_content)

    def on_question_menu_go_home(self, _: QuestionMenu.GoHome) -> None:
        self.show_home()

    def on_question_menu_show_results_requested(
        self,
        event: QuestionMenu.ShowResultsRequested,
    ) -> None:
        self.show_widget(
            ShowResults(
                correct_answers=event.correct_answers,
                wrong_answers=event.wrong_answers,
            )
        )

    def on_show_results_go_home(self, _: ShowResults.GoHome) -> None:
        self.show_home()

    def on_deck_selector_deck_chosen(self, event: DeckSelector.DeckChosen) -> None:
        self.show_widget(QuestionMenu(event.cards))

    def on_deck_editor_create_deck_requested(
        self,
        _: DeckEditor.CreateDeckRequested,
    ) -> None:
        if self._navigation_blocked("deck_creator"):
            return
        self.show_widget(DeckCreator())

    def on_deck_creator_deck_created(self, event: DeckCreator.DeckCreated) -> None:
        self.show_widget(DeckEditor(initial_deck_name=event.deck_name))

    def on_deck_creator_back_requested(self, event: DeckCreator.BackRequested) -> None:
        self.show_widget(DeckManagerActions(event.deck_name) if event.deck_name else DeckManager())

    def on_deck_manager_create_deck_requested(
        self,
        _: DeckManager.CreateDeckRequested,
    ) -> None:
        self.show_widget(DeckCreator())

    def on_deck_manager_import_deck_requested(
        self,
        _: DeckManager.ImportDeckRequested,
    ) -> None:
        self.show_widget(DeckImporter())

    def on_deck_manager_open_deck_actions_requested(
        self,
        event: DeckManager.OpenDeckActionsRequested,
    ) -> None:
        self.show_widget(DeckManagerActions(event.deck_name))

    def on_deck_manager_actions_back_requested(
        self,
        _: DeckManagerActions.BackRequested,
    ) -> None:
        self.show_widget(DeckManager())

    def on_deck_manager_actions_duplicate_deck_requested(
        self,
        event: DeckManagerActions.DuplicateDeckRequested,
    ) -> None:
        self.show_widget(
            DeckCreator(
                initial_deck_name=event.suggested_name,
                initial_cards=event.cards,
                back_deck_name=event.source_deck_name,
            )
        )

    def on_deck_manager_actions_edit_deck_requested(
        self,
        event: DeckManagerActions.EditDeckRequested,
    ) -> None:
        self.show_widget(DeckEditor(initial_deck_name=event.deck_name))

    def on_deck_editor_back_requested(
        self,
        event: DeckEditor.BackRequested,
    ) -> None:
        self.show_widget(DeckManagerActions(event.deck_name) if event.deck_name else DeckManager())

    def show_home(self) -> None:
        self.show_screen(ui_constants.HOME, focus_content=False)

    def show_screen(self, menu_name: str, focus_content: bool = True) -> None:
        if self._navigation_blocked(menu_name):
            return

        if menu_name == ui_constants.EXIT:
            self.exit()
            return

        content_data = ui_constants.MENU_PAGES.get(menu_name)
        if content_data is None:
            self.show_widget(unknown_content_widget(menu_name), focus_content=focus_content)
            return

        self.show_widget(menu_widget(content_data), focus_content=focus_content)

    def show_widget(self, content_widget: Widget, focus_content: bool = True) -> None:
        content_widget.styles.width = "1fr"
        content_widget.styles.height = "1fr" if isinstance(content_widget, HomeView) else "auto"
        content_area = self.content_area()
        content_area.remove_children()
        content_area.mount(content_widget)
        self._schedule_focus(focus_content)

    def action_focus_sidebar(self) -> None:
        self.sidebar().focus_current()
        self.active_block = "sidebar"

    def action_focus_content(self) -> None:
        focusables = self.get_content_focusables()
        if not focusables:
            self.action_focus_sidebar()
            return
        focusables[0].focus()
        self.active_block = "content"

    def action_block_next(self) -> None:
        self.move_focus_in_block(step=1)

    def action_block_previous(self) -> None:
        self.move_focus_in_block(step=-1)

    def on_key(self, event: Key) -> None:
        key = event.key
        is_ctrl = "ctrl+" in key or bool(getattr(event, "ctrl", False))

        if is_ctrl and self.matches_direction(key, "left"):
            self.action_focus_sidebar()
            event.stop()
            return
        if is_ctrl and self.matches_direction(key, "right"):
            self.action_focus_content()
            event.stop()
            return

        if self.active_block == "sidebar":
            if self.matches_direction(key, "up"):
                self.move_sidebar_selection(step=-1)
                event.stop()
                return
            if self.matches_direction(key, "down"):
                self.move_sidebar_selection(step=1)
                event.stop()
                return
            if key == "enter":
                self.sidebar().activate_current()
                event.stop()
                return

        if self.should_move_with_key(key, "up", is_ctrl):
            self.action_block_previous()
            event.stop()
            return
        if self.should_move_with_key(key, "down", is_ctrl):
            self.action_block_next()
            event.stop()

    def _navigation_blocked(self, menu_name: str) -> bool:
        current_content = self.current_content_widget()
        if current_content is None or menu_name == ui_constants.EDIT_DECK:
            return False

        has_unsaved_changes = getattr(current_content, "has_unsaved_changes", None)
        if not callable(has_unsaved_changes) or not has_unsaved_changes():
            return False

        warning_callback = getattr(current_content, "warn_unsaved_changes", None)
        if callable(warning_callback):
            warning_callback()
        self.call_after_refresh(self.action_focus_content)
        return True

    def _schedule_focus(self, focus_content: bool) -> None:
        if focus_content:
            self.call_after_refresh(self.action_focus_content)
            return
        self.call_after_refresh(self.action_focus_sidebar)
        self.call_later(self.action_focus_sidebar)

    def content_area(self) -> VerticalScroll:
        return self.query_one("#content_scroll", VerticalScroll)

    def current_content_widget(self) -> Widget | None:
        content_area = self.content_area()
        return next(iter(content_area.children), None)

    def sidebar(self) -> SideMenu:
        return self.query_one(SideMenu)

    def get_content_focusables(self) -> list[Widget]:
        focusables: list[Widget] = []
        for widget in self.content_area().query("*"):
            if not getattr(widget, "can_focus", False):
                continue
            if isinstance(widget, VerticalScroll):
                continue
            if getattr(widget, "disabled", False):
                continue
            focusables.append(widget)
        return focusables

    def move_focus_in_block(self, step: int) -> None:
        if self.active_block == "sidebar":
            self.move_sidebar_selection(step)
            return

        focusables = self.get_content_focusables()
        if not focusables:
            self.action_focus_sidebar()
            return

        current = self.screen.focused
        if current in focusables:
            current_index = focusables.index(current)
        else:
            # If focus is not on a known widget, restart from the beginning or end
            # depending on the requested direction.
            current_index = -1 if step > 0 else 0
        next_index = (current_index + step) % len(focusables)
        focusables[next_index].focus()
        self.active_block = "content"

    def move_sidebar_selection(self, step: int) -> None:
        self.sidebar().move_selection(step)
        self.active_block = "sidebar"

    def matches_direction(self, key: str, direction: str) -> bool:
        return key == direction or key.endswith(direction)

    def should_move_with_key(self, key: str, direction: str, is_ctrl: bool) -> bool:
        focused = self.screen.focused
        if not is_ctrl and self.content_widget_uses_direction_key(focused, direction):
            return False
        return (is_ctrl and self.matches_direction(key, direction)) or (
            not is_ctrl and self.active_block == "content" and key == direction
        )

    def content_widget_uses_direction_key(
        self,
        focused: Widget | None,
        direction: str,
    ) -> bool:
        if focused is None or direction not in {"up", "down"}:
            return False
        if isinstance(focused, (Select, ListView)):
            return True
        return focused.__class__.__name__ == "SelectOverlay"


def main() -> None:
    MainApp().run()


if __name__ == "__main__":
    main()
