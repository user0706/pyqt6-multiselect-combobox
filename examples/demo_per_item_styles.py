#!/usr/bin/env python3
# Demo: Per-item fonts/colors via item data roles

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Per-Item Styles Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    label = QLabel("Per-item colors/fonts applied via model roles")

    # Build a model with custom roles for some rows
    model = QStandardItemModel()

    def add_item(text, color: str | None = None, bold: bool = False):
        it = QStandardItem(text)
        if color:
            it.setData(QBrush(QColor(color)), Qt.ItemDataRole.ForegroundRole)
        if bold:
            f = QFont()
            f.setBold(True)
            it.setData(f, Qt.ItemDataRole.FontRole)
        # Store text as UserRole payload as well
        it.setData(text, Qt.ItemDataRole.UserRole)
        model.appendRow(it)

    add_item("Default")
    add_item("Important (bold)", bold=True)
    add_item("Info (blue)", color="#1e88e5")
    add_item("Warning (orange)", color="#fb8c00")
    add_item("Error (red, bold)", color="#e53935", bold=True)

    combo = MultiSelectComboBox()
    combo.setModel(model)

    def on_selection_changed(values):
        label.setText(f"Selected: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    layout.addWidget(combo)
    layout.addWidget(label)

    window.setCentralWidget(central)
    window.resize(560, 280)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
