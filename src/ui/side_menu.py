from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Label

from src.ui import ui_constants


class SideMenu(Widget, can_focus=True):
    """Widget dedicato esclusivamente al menu laterale."""

    class MenuChosen(Message):
        """Evento emesso quando l'utente seleziona una voce del menu."""

        def __init__(self, menu_name: str, focus_content: bool = False) -> None:
            super().__init__()
            self.menu_name = menu_name
            self.focus_content = focus_content

    def __init__(self) -> None:
        super().__init__()
        self.menu_names = list(ui_constants.MENU_PAGES.keys())
        self.current_index = 0
        self.styles.width = 26
        self.styles.height = "1fr"

    def compose(self) -> ComposeResult:
        with Vertical(id="sidebar"):
            yield Label(ui_constants.MENU_TITLE, id="menu_title")
            with Vertical(id="menu"):
                for index, menu_name in enumerate(self.menu_names):
                    yield Button(
                        menu_name,
                        id=f"menu_item_{index}",
                        name=menu_name,
                        classes="menu-item",
                    )

    def on_mount(self) -> None:
        self.focus_current()
        self._refresh_highlight()
        self.post_message(self.MenuChosen(self.current_menu_name(), focus_content=False))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if not event.button.has_class("menu-item") or event.button.name is None:
            return
        self.current_index = self.menu_names.index(event.button.name)
        self._refresh_highlight()
        self.focus_current()
        self.post_message(self.MenuChosen(event.button.name, focus_content=True))

    def move_selection(self, step: int) -> None:
        if not self.menu_names:
            return
        self.current_index = (self.current_index + step) % len(self.menu_names)
        self._refresh_highlight()
        self.focus_current()

    def focus_current(self) -> None:
        self._menu_button(self.current_index).focus()

    def current_menu_name(self) -> str:
        return self.menu_names[self.current_index]

    def activate_current(self) -> None:
        self.post_message(self.MenuChosen(self.current_menu_name(), focus_content=True))

    def _refresh_highlight(self) -> None:
        for index, _ in enumerate(self.menu_names):
            button = self._menu_button(index)
            button.set_class(index == self.current_index, "-active")

    def _menu_button(self, index: int) -> Button:
        return self.query_one(f"#menu_item_{index}", Button)
