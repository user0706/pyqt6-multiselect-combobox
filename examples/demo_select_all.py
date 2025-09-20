#!/usr/bin/env python3
# Demo: Select All tri-state behavior

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Select All Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label = QLabel("Selected:")
    combo = MultiSelectComboBox()
    combo.setSelectAllEnabled(True)
    combo.addItems(["Apple", "Banana", "Orange", "Grape"])  # text-only

    def on_selection_changed(values):
        label.setText(f"Selected: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    layout.addWidget(combo)
    layout.addWidget(label)

    window.setCentralWidget(central_widget)
    window.resize(420, 200)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
