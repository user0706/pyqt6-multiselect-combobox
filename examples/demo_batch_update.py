#!/usr/bin/env python3
# Demo: Batch operations with beginUpdate()/endUpdate() and selection helpers

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
    window.setWindowTitle("MultiSelectComboBox - Batch Update Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label = QLabel("Selected:")
    combo = MultiSelectComboBox()
    combo.addItems([f"Item {i}" for i in range(1, 21)])

    def on_selection_changed(values):
        label.setText(f"Selected: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    btn_select_all = QPushButton("Select All")
    btn_clear = QPushButton("Clear Selection")
    btn_invert = QPushButton("Invert Selection")
    btn_batch = QPushButton("Batch: Clear then Select 1, 5, 9")

    btn_select_all.clicked.connect(combo.selectAll)
    btn_clear.clicked.connect(combo.clearSelection)
    btn_invert.clicked.connect(combo.invertSelection)

    def do_batch():
        combo.beginUpdate()
        try:
            combo.clearSelection()
            # If the widget exposes setCurrentIndexes, use it; otherwise simulate by setCurrentText(list)
            try:
                combo.setCurrentIndexes([0, 4, 8])
            except AttributeError:
                combo.setCurrentText(["Item 1", "Item 5", "Item 9"])
        finally:
            combo.endUpdate()

    btn_batch.clicked.connect(do_batch)

    layout.addWidget(combo)
    layout.addWidget(btn_select_all)
    layout.addWidget(btn_clear)
    layout.addWidget(btn_invert)
    layout.addWidget(btn_batch)
    layout.addWidget(label)

    window.setCentralWidget(central_widget)
    window.resize(520, 340)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
