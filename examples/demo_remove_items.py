#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

from pyqt6_multiselect_combobox import MultiSelectComboBox


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MultiSelectComboBox: removeItem / removeItems")
        layout = QVBoxLayout(self)

        self.info = QLabel(
            "This demo shows how removeItem(index) and removeItems(indexes) work.\n"
            "Select All is enabled to demonstrate tri-state re-sync."
        )
        layout.addWidget(self.info)

        self.combo = MultiSelectComboBox()
        self.combo.setDisplayType("text")
        self.combo.setSelectAllEnabled(True)
        # Add items
        self.combo.addItems(["Alpha", "Beta", "Gamma", "Delta"])  # model rows: 0(SA),1,2,3,4
        layout.addWidget(self.combo)

        # Status label to show current selection and SA state
        self.status = QLabel("")
        layout.addWidget(self.status)

        # Controls
        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)

        btn_select_all = QPushButton("Select All options")
        btn_select_all.clicked.connect(self.combo.selectAll)
        btn_row.addWidget(btn_select_all)

        btn_clear = QPushButton("Clear selection")
        btn_clear.clicked.connect(self.combo.clear)
        btn_row.addWidget(btn_clear)

        btn_remove_first = QPushButton("Remove first option (idx 1)")
        btn_remove_first.clicked.connect(lambda: self.combo.removeItem(1))
        layout.addWidget(btn_remove_first)

        btn_remove_bulk = QPushButton("Remove options idx [1, 3]")
        btn_remove_bulk.clicked.connect(lambda: self.combo.removeItems([1, 3]))
        layout.addWidget(btn_remove_bulk)

        def on_changed(values):
            # Show selection list and Select All state
            sa_state = "N/A"
            if self.combo.isSelectAllEnabled() and self.combo.model().rowCount() > 0:
                sa = self.combo.model().item(0)
                if sa and sa.data() == "__select_all__":
                    st = sa.data(Qt.ItemDataRole.CheckStateRole)
                    if st == Qt.CheckState.Checked:
                        sa_state = "checked"
                    elif st == Qt.CheckState.PartiallyChecked:
                        sa_state = "partially checked"
                    else:
                        sa_state = "unchecked"
            self.status.setText(f"selectionChanged: {values} | Select All: {sa_state}")

        self.combo.selectionChanged.connect(on_changed)


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    w = Demo()
    w.resize(480, 260)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
