from src.ui import ui_constants


class MainAppController:
    """Non-UI routing logic for MainApp."""

    def __init__(self) -> None:
        self.menu_config = ui_constants.MENU_PAGES

    def get_content_data(self, menu_name: str) -> dict | None:
        return self.menu_config.get(menu_name)

    def should_exit(self, menu_name: str) -> bool:
        return menu_name == ui_constants.EXIT

    def should_block_navigation(
        self,
        current_content: object | None,
        menu_name: str,
        edit_menu_name: str,
    ) -> bool:
        # The controller does not depend on concrete UI classes:
        # it only uses a small duck-typed protocol.
        if current_content is None:
            return False
        has_unsaved_changes = getattr(current_content, "has_unsaved_changes", None)
        if not callable(has_unsaved_changes):
            return False
        return menu_name != edit_menu_name and has_unsaved_changes()

    def warn_unsaved_changes(self, current_content: object | None) -> None:
        if current_content is None:
            return
        warning_callback = getattr(current_content, "warn_unsaved_changes", None)
        if callable(warning_callback):
            warning_callback()
