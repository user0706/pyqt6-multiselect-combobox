#!/usr/bin/env python3
"""
Demo: Clear button in the line edit clears selection.

- Shows a MultiSelectComboBox with a few items and placeholder text.
- The internal QLineEdit has its native clear button enabled.
- Clicking the clear button (x icon) will clear the selection and update the label.
"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Clear Button Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    info = QLabel("Use the clear (x) button in the field to clear selection.")
    combo = MultiSelectComboBox()
    combo.setPlaceholderText("Pick fruits")
    combo.setSelectAllEnabled(True)
    combo.addItems(["Apple", "Banana", "Orange", "Grape", "Mango"])  # text-only

    status = QLabel("Selected: []")

    def on_changed(values):
        status.setText(f"Selected: {values}")

    combo.selectionChanged.connect(on_changed)

    # Also include a button that calls the public clear() API
    btn_clear = QPushButton("Clear via API")
    btn_clear.clicked.connect(combo.clear)

    layout.addWidget(info)
    layout.addWidget(combo)
    layout.addWidget(btn_clear)
    layout.addWidget(status)

    window.setCentralWidget(central)
    window.resize(480, 220)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
