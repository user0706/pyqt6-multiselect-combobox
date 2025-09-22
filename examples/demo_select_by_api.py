#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

from pyqt6_multiselect_combobox import MultiSelectComboBox


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MultiSelectComboBox: Select by API")
        layout = QVBoxLayout(self)

        self.info = QLabel(
            "This demo shows explicit selection APIs:\n"
            "- setCurrentTexts([str, ...])\n"
            "- setCurrentDataValues([Any, ...])\n"
            "Items have custom data at Qt.UserRole."
        )
        layout.addWidget(self.info)

        self.combo = MultiSelectComboBox()
        self.combo.setDisplayType("text")
        # Add items with explicit data distinct from text
        texts = ["Apple", "Banana", "Cherry", "Date"]
        codes = ["APL", "BAN", "CHR", "DAT"]
        self.combo.addItems(texts, codes)
        layout.addWidget(self.combo)

        # Buttons to demonstrate usage
        by_text_btn = QPushButton("Select by texts: Apple, Cherry")
        by_text_btn.clicked.connect(lambda: self.combo.setCurrentTexts(["Apple", "Cherry"]))
        layout.addWidget(by_text_btn)

        by_data_btn = QPushButton("Select by data: BAN, DAT")
        by_data_btn.clicked.connect(lambda: self.combo.setCurrentDataValues(["BAN", "DAT"]))
        layout.addWidget(by_data_btn)

        clear_btn = QPushButton("Clear selection")
        clear_btn.clicked.connect(self.combo.clear)
        layout.addWidget(clear_btn)

        # Display current outputs for reference
        self.output_label = QLabel("")
        layout.addWidget(self.output_label)

        def on_changed(values):
            # output_type defaults to 'data' so this will show codes by default
            self.output_label.setText(f"selectionChanged: {values}")

        self.combo.selectionChanged.connect(on_changed)


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    w = Demo()
    w.resize(420, 200)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
