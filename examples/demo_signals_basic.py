#!/usr/bin/env python3
# Demo: Basic signal usage with selectionChanged(list)

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from pyqt6_multiselect_combobox import MultiSelectComboBox


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MultiSelectComboBox - Signals (Basic)")

        central = QWidget(self)
        layout = QVBoxLayout(central)

        self.info = QLabel("Waiting for selection…")

        self.combo = MultiSelectComboBox()
        self.combo.setSelectAllEnabled(True)
        self.combo.addItems(["Apple", "Banana", "Orange", "Grape"])  # text-only

        # Connect the built-in signal to a slot method
        self.combo.selectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.combo)
        layout.addWidget(self.info)
        self.setCentralWidget(central)

    @pyqtSlot(list)
    def on_selection_changed(self, values: list):
        # values will be the selection as a list following widget's configured output role
        self.info.setText(f"selectionChanged -> {values}")


def main():
    app = QApplication([])
    w = Window()
    w.resize(520, 240)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
