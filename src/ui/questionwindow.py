from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QSizePolicy, QPushButton
from .ui_constants import QUESTION_WIN_SIZE, PLACEHOLDER_TXT, ENTER_BUTTON


class QuestionWindow(QWidget):
    def __init__(self, window_title: str, question: str):
        super().__init__()

        self.setWindowTitle(window_title)
        self.resize(QUESTION_WIN_SIZE[0], QUESTION_WIN_SIZE[1])

        layout = QVBoxLayout()

        # --- Read only box ---
        self.readonly_box = QTextEdit()
        self.readonly_box.setReadOnly(True)
        self.readonly_box.setText(question)
        self.readonly_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- Editable box ---
        self.user_box = QTextEdit()
        self.user_box.setPlaceholderText(PLACEHOLDER_TXT)
        self.user_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- ENTER button ---
        self.button = QPushButton(ENTER_BUTTON)
        self.button.setDefault(True)
        self.button.clicked.connect(self.on_submit)  # pylint: disable=no-member

        layout.addWidget(self.readonly_box)
        layout.addWidget(self.user_box)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def get_answer(self) -> str:
        return self.user_box.toPlainText()

    def on_submit(self):
        """Prints answer and closes QuestionWindow."""
        answer = self.get_answer()
        print("User answer: ", answer)
        self.close()


# USAGE SAMPLE: (keep until this module is not implemented in main)
# pylint: disable=pointless-string-statement
"""
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)

    text = "aòlsalklasakskasmasaskalksal"

    QuestionWindow = QuestionWindow("Window name", text)
    QuestionWindow.show()

    sys.exit(app.exec())
"""
