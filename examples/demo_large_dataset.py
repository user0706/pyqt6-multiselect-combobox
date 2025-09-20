#!/usr/bin/env python3
# Demo: Large dataset and responsiveness

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
    window.setWindowTitle("MultiSelectComboBox - Large Dataset Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    status = QLabel("Ready")

    combo = MultiSelectComboBox()

    # Populate with a large number of items
    items = [f"Item {i:04d}" for i in range(1, 2001)]
    combo.addItems(items)

    def batch_select_sample():
        status.setText("Batch selecting a sample…")
        combo.beginUpdate()
        try:
            combo.clearSelection()
            # Select a spread of items using list-of-text API
            sample = [f"Item {i:04d}" for i in (1, 50, 100, 500, 1000, 1500, 1999)]
            combo.setCurrentText(sample)
        finally:
            combo.endUpdate()
        status.setText("Done")

    btn_batch = QPushButton("Batch: Select sample items")
    btn_batch.clicked.connect(batch_select_sample)

    layout.addWidget(combo)
    layout.addWidget(btn_batch)
    layout.addWidget(status)

    window.setCentralWidget(central_widget)
    window.resize(560, 380)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
