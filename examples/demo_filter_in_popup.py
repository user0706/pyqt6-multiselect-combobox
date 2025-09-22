#!/usr/bin/env python3
# Demo: in-popup filter for MultiSelectComboBox

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox — In-Popup Filter Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label = QLabel("Selected: []")
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    combo = MultiSelectComboBox()
    combo.setSelectAllEnabled(True)
    combo.setFilterEnabled(True)  # enable the in-popup search/filter

    # Populate with a moderately large set to demonstrate filtering convenience
    fruits = [
        "Apple", "Apricot", "Avocado", "Banana", "Blackberry", "Blueberry",
        "Cherry", "Coconut", "Cranberry", "Date", "Dragonfruit", "Durian",
        "Fig", "Grape", "Grapefruit", "Guava", "Kiwi", "Lemon", "Lime",
        "Lychee", "Mango", "Melon", "Nectarine", "Orange", "Papaya",
        "Peach", "Pear", "Pineapple", "Plum", "Pomegranate", "Raspberry",
        "Strawberry", "Tangerine", "Watermelon",
    ]
    combo.addItems(fruits)

    def on_selection_changed(values):
        label.setText(f"Selected: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    # Controls row: toggle filter on/off + show popup button
    controls = QHBoxLayout()
    btn_toggle = QPushButton("Toggle Filter")
    btn_show = QPushButton("Show Popup")

    def on_toggle():
        combo.setFilterEnabled(not combo.isFilterEnabled())
        btn_toggle.setText("Disable Filter" if combo.isFilterEnabled() else "Enable Filter")

    def on_show_popup():
        combo.showPopup()

    btn_toggle.clicked.connect(on_toggle)
    btn_show.clicked.connect(on_show_popup)

    controls.addWidget(btn_toggle)
    controls.addWidget(btn_show)
    controls.addStretch(1)

    layout.addWidget(combo)
    layout.addLayout(controls)
    layout.addWidget(label)

    window.setCentralWidget(central_widget)
    window.resize(460, 260)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
