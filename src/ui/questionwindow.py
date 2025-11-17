import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout,
    QSizePolicy, QPushButton
)


class QuestionWindow(QWidget):
    def __init__(self, windowTitle: str, readonlyText: str):
        super().__init__()

        self.setWindowTitle(windowTitle)
        self.resize(600, 400)

        layout = QVBoxLayout()

        # --- Read only box ---
        self.readonly_box = QTextEdit()
        self.readonly_box.setReadOnly(True)
        self.readonly_box.setText(readonlyText)
        self.readonly_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- Editable box ---
        self.user_box = QTextEdit()
        self.user_box.setPlaceholderText("Write here...")
        self.user_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- ENTER button ---
        self.button = QPushButton("Enter")
        self.button.setDefault(True)
        self.button.clicked.connect(self.on_submit)

        layout.addWidget(self.readonly_box)
        layout.addWidget(self.user_box)
        layout.addWidget(self.button)

        self.setLayout(layout)


    def get_answer(self) -> str:
        return self.user_box.toPlainText()


    def on_submit(self):
        """Prints answer and closes QuestionWindow."""
        answer = get_answer(self)
        print("User answer: ", answer)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    text = "aòlsalklasakskasmasaskalksal"

    QuestionWindow = QuestionWindow("Window name", text)
    QuestionWindow.show()

    sys.exit(app.exec())
