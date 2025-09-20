#!/usr/bin/env python3
# Demo: Custom display delimiter and reading joined text

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Custom Delimiter Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label = QLabel("Joined text:")
    combo = MultiSelectComboBox()
    combo.setDisplayDelimiter(" | ")
    combo.addItems(["Red", "Green", "Blue"])  # text-only

    def on_selection_changed(values):
        label.setText(f"Joined text: {combo.currentText()}")

    combo.selectionChanged.connect(on_selection_changed)

    btn_select = QPushButton("Select Red and Blue")

    def do_select():
        combo.setCurrentText(["Red", "Blue"])  # list selection

    btn_select.clicked.connect(do_select)

    layout.addWidget(combo)
    layout.addWidget(btn_select)
    layout.addWidget(label)

    window.setCentralWidget(central_widget)
    window.resize(520, 240)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
