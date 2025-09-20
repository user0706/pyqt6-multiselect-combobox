#!/usr/bin/env python3
# Demo: Custom arrow icon with hover/focus styles

from pathlib import Path
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from pyqt6_multiselect_combobox import MultiSelectComboBox


def make_stylesheet(arrow_path: str) -> str:
    return f"""
QComboBox {{
    background-color: #ffffff;
    color: #222222;
    border: 1px solid #cfcfcf;
    border-radius: 6px;
    padding: 4px 8px;
}}
QComboBox:hover {{
    border-color: #999999;
}}
QComboBox:focus {{
    border-color: #3d6dad;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #cfcfcf;
}}
QComboBox::down-arrow {{
    image: url("{arrow_path}");
    width: 14px; height: 14px;
    margin-right: 6px;
}}
QAbstractItemView {{
    background-color: #ffffff;
    color: #222222;
    selection-background-color: #3d6dad;
    selection-color: #ffffff;
    outline: 0;
    border: 1px solid #cfcfcf;
}}
"""


def main():
    app = QApplication([])

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#f7f7f7"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#222222"))
    app.setPalette(pal)

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Hover/Focus & Arrow Icon Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    label = QLabel("Custom arrow + hover/focus styles")

    combo = MultiSelectComboBox()
    combo.addItems(["Apple", "Banana", "Orange", "Grape"])  # text-only

    # Compute absolute path to the chevron icon in assets/
    root = Path(__file__).resolve().parents[1]
    arrow = root / "assets" / "chevron-down.svg"
    combo.setStyleSheet(make_stylesheet(str(arrow)))

    def on_selection_changed(values):
        label.setText(f"Selection: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    layout.addWidget(combo)
    layout.addWidget(label)

    window.setCentralWidget(central)
    window.resize(520, 240)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
