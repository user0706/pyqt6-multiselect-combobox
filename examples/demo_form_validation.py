#!/usr/bin/env python3
# Demo: Simple form validation requiring at least one selection

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
)
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Form Validation Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    instructions = QLabel("Pick at least one fruit, then click Submit")
    status = QLabel("")

    combo = MultiSelectComboBox()
    combo.addItems(["Apple", "Banana", "Orange", "Grape"])  # text-only

    submit = QPushButton("Submit")
    submit.setEnabled(False)

    def on_selection_changed(_):
        # Enable submit only if there is at least one selection
        submit.setEnabled(bool(combo.currentText()))
        status.setText("")

    combo.selectionChanged.connect(on_selection_changed)

    def on_submit():
        status.setText(f"Submitted values: {combo.currentData() or combo.currentText()}")

    submit.clicked.connect(on_submit)

    layout.addWidget(instructions)
    layout.addWidget(combo)
    layout.addWidget(submit)
    layout.addWidget(status)

    window.setCentralWidget(central)
    window.resize(520, 260)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
