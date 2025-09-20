#!/usr/bin/env python3
# Demo: Advanced signal patterns with selectionChanged(list)

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
)
from pyqt6_multiselect_combobox import MultiSelectComboBox


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MultiSelectComboBox - Signals (Advanced)")

        central = QWidget(self)
        layout = QVBoxLayout(central)

        self.combo = MultiSelectComboBox()
        self.combo.addItems(["Apple", "Banana", "Orange", "Grape", "Mango"])  # text-only

        # Labels to show different processing of the same signal
        self.as_text = QLabel("As text: []")
        self.as_count = QLabel("Count: 0")

        # Connect signal to multiple slots
        self.combo.selectionChanged.connect(self.update_text)
        self.combo.selectionChanged.connect(self.update_count)

        # Buttons to demonstrate temporary disconnect/reconnect and batch updates
        self.btn_disconnect = QPushButton("Temporarily disconnect update_text")
        self.btn_reconnect = QPushButton("Reconnect update_text")
        self.btn_batch = QPushButton("Batch: Clear then select Banana, Mango (no extra signal spam)")

        self.btn_disconnect.clicked.connect(self.disconnect_update_text)
        self.btn_reconnect.clicked.connect(self.reconnect_update_text)
        self.btn_batch.clicked.connect(self.do_batch_update)

        layout.addWidget(self.combo)
        layout.addWidget(self.as_text)
        layout.addWidget(self.as_count)
        layout.addWidget(self.btn_disconnect)
        layout.addWidget(self.btn_reconnect)
        layout.addWidget(self.btn_batch)
        self.setCentralWidget(central)

    @pyqtSlot(list)
    def update_text(self, values: list):
        # One slot renders the list as joined text
        self.as_text.setText(f"As text: {', '.join(map(str, values))}")

    @pyqtSlot(list)
    def update_count(self, values: list):
        # Another slot just shows the count
        self.as_count.setText(f"Count: {len(values)}")

    def disconnect_update_text(self):
        try:
            self.combo.selectionChanged.disconnect(self.update_text)
            self.as_text.setText("As text: (disconnected)")
        except TypeError:
            # Already disconnected
            pass

    def reconnect_update_text(self):
        try:
            self.combo.selectionChanged.connect(self.update_text)
            # Immediately refresh label with current state
            self.update_text(self.combo.currentData() or [])
        except TypeError:
            # Already connected
            pass

    def do_batch_update(self):
        # Demonstrate coalescing updates via beginUpdate/endUpdate
        self.combo.beginUpdate()
        try:
            self.combo.clearSelection()
            self.combo.setCurrentText(["Banana", "Mango"])  # one final signal after endUpdate()
        finally:
            self.combo.endUpdate()


def main():
    app = QApplication([])
    w = Window()
    w.resize(560, 320)
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
