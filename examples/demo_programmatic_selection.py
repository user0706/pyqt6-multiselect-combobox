#!/usr/bin/env python3
# Demo: Programmatic selection via setCurrentText (string and list forms)

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Programmatic Selection Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label = QLabel("Selected:")
    combo = MultiSelectComboBox()
    combo.addItems(["Apple", "Banana", "Orange", "Grape"])  # text-only

    def on_selection_changed(values):
        label.setText(f"Selected: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    btn_by_string = QPushButton("Select 'Apple, Banana' (by joined string)")
    btn_by_list = QPushButton("Select ['Orange', 'Grape'] (by list)")

    def select_by_string():
        combo.setCurrentText("Apple, Banana")  # uses current display delimiter

    def select_by_list():
        combo.setCurrentText(["Orange", "Grape"])  # list matches text or data

    btn_by_string.clicked.connect(select_by_string)
    btn_by_list.clicked.connect(select_by_list)

    layout.addWidget(combo)
    layout.addWidget(btn_by_string)
    layout.addWidget(btn_by_list)
    layout.addWidget(label)

    window.setCentralWidget(central_widget)
    window.resize(520, 260)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
