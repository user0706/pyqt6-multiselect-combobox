#!/usr/bin/env python3
# Demo: Switching output data role at runtime

from PyQt6.QtCore import Qt
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
    window.setWindowTitle("MultiSelectComboBox - Runtime Role Switch Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    info = QLabel("Output role: UserRole")
    text_label = QLabel("currentText():")
    data_label = QLabel("currentData():")

    combo = MultiSelectComboBox()
    combo.setDisplayDelimiter(", ")

    # Store different values under DisplayRole and UserRole to demonstrate switching
    from PyQt6.QtGui import QStandardItem
    from PyQt6.QtGui import QStandardItemModel

    model = QStandardItemModel()

    def add_item(text, code):
        it = QStandardItem(text)
        # Store a short code in DisplayRole and a dict in UserRole so the
        # difference is obvious when switching output roles.
        it.setData(code, int(Qt.ItemDataRole.DisplayRole))
        it.setData({"code": code}, int(Qt.ItemDataRole.UserRole))
        # Make the item user-checkable like MultiSelectComboBox.addItem does
        it.setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        )
        it.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        model.appendRow(it)

    for text, code in [("Apple", "APL"), ("Banana", "BAN"), ("Orange", "ORG")]:
        add_item(text, code)

    combo.setModel(model)
    combo.setOutputDataRole(Qt.ItemDataRole.UserRole)

    def refresh_labels():
        text_label.setText(f"currentText(): {combo.currentText()}")
        data_label.setText(f"currentData(): {combo.currentData()}")

    combo.selectionChanged.connect(lambda _: refresh_labels())

    def switch_to_display():
        combo.setOutputDataRole(Qt.ItemDataRole.DisplayRole)
        info.setText("Output role: DisplayRole")
        refresh_labels()

    def switch_to_user():
        combo.setOutputDataRole(Qt.ItemDataRole.UserRole)
        info.setText("Output role: UserRole")
        refresh_labels()

    btn_display = QPushButton("Use DisplayRole outputs")
    btn_display.clicked.connect(switch_to_display)

    btn_user = QPushButton("Use UserRole outputs")
    btn_user.clicked.connect(switch_to_user)

    layout.addWidget(combo)
    layout.addWidget(btn_display)
    layout.addWidget(btn_user)
    layout.addWidget(info)
    layout.addWidget(text_label)
    layout.addWidget(data_label)

    window.setCentralWidget(central)
    window.resize(560, 320)
    # Initialize labels before showing
    refresh_labels()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
