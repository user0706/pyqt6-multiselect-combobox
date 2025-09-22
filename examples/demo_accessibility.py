#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Accessibility (A11y) demo for MultiSelectComboBox.

This example showcases:
- Accessible names on the combo and its line edit (e.g., "3 items selected.")
- ARIA-like hints exposed via tooltips/status tips for the Select All pseudo-item and regular options.

Run:
    python examples/demo_accessibility.py
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow, QStatusBar
from PyQt6.QtCore import Qt

from pyqt6_multiselect_combobox import MultiSelectComboBox


def build_ui():
    w = QMainWindow()
    central = QWidget()
    layout = QVBoxLayout(central)

    lbl = QLabel("Accessibility demo: hover and navigate the combo box to see hints.\n"
                 "Use Up/Down to navigate; press Space/Enter to toggle selections.")
    lbl.setWordWrap(True)

    combo = MultiSelectComboBox()
    combo.setPlaceholderText("Pick some fruits")
    combo.setSelectAllEnabled(True)
    combo.addItems(["Apple", "Banana", "Cherry", "Date", "Elderberry"])  # data defaults to text

    # Pre-select a couple to demonstrate accessible names summary
    combo.setCurrentIndexes([1, 3])

    # Optional: connect selectionChanged to update a label with accessible summary
    summary = QLabel()

    def update_summary(_):
        summary.setText(f"Accessible name: {combo.accessibleName()}\n"
                        f"Line edit accessible name: {combo.lineEdit().accessibleName()}")

    combo.selectionChanged.connect(update_summary)
    update_summary([])

    layout.addWidget(lbl)
    layout.addWidget(combo)
    layout.addWidget(summary)

    # Status bar to display status tips on hover
    status = QStatusBar()
    w.setStatusBar(status)

    w.setCentralWidget(central)
    w.setWindowTitle("MultiSelectComboBox – Accessibility Demo")
    w.resize(480, 240)

    # Print out the current tooltips for demonstration in console as well
    m = combo.model()
    if m is not None:
        print("Select All tooltip:", (m.item(0).toolTip() if m.rowCount() > 0 else None))
        for row in range(1, m.rowCount()):
            it = m.item(row)
            if it is not None:
                print(f"Row {row} ('{it.text()}') tooltip:", it.toolTip())

    return w


def main(argv=None):
    argv = argv or sys.argv
    app = QApplication.instance() or QApplication(argv)
    win = build_ui()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
