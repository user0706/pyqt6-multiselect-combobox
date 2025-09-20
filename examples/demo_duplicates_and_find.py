#!/usr/bin/env python3
# Demo: Duplicate policy and find helpers

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
    window.setWindowTitle("MultiSelectComboBox - Duplicates & Find Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    info = QLabel("")

    combo = MultiSelectComboBox()
    combo.setDuplicatesEnabled(False)  # prevent duplicates

    # Add items; second 'Apple' should be skipped due to duplicate policy
    combo.addItem("Apple", "A1")
    combo.addItem("Banana", "B1")
    combo.addItem("Apple", "A2")  # same text, would be blocked if duplicates disabled

    def show_find_results():
        i_text = combo.findText("Banana")
        i_data = combo.findData("A1")
        info.setText(f"findText('Banana') => {i_text}; findData('A1') => {i_data}")

    btn_find = QPushButton("Show findText/findData results")
    btn_find.clicked.connect(show_find_results)

    layout.addWidget(combo)
    layout.addWidget(btn_find)
    layout.addWidget(info)

    window.setCentralWidget(central)
    window.resize(560, 240)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
