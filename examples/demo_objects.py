#!/usr/bin/env python3
# Demo: Storing custom Python objects as item data and reading them back

from dataclasses import dataclass, asdict
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from pyqt6_multiselect_combobox import MultiSelectComboBox


@dataclass
class Fruit:
    name: str
    code: str
    calories: int


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Custom Objects Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    info_text = QLabel("currentText(): []")
    info_data = QLabel("currentData(): []")

    combo = MultiSelectComboBox()
    combo.setOutputDataRole(Qt.ItemDataRole.UserRole)  # default

    # Add items with text + Python object data
    combo.addItem("Apple", Fruit("Apple", "APL", 95))
    combo.addItem("Banana", Fruit("Banana", "BAN", 105))
    combo.addItem("Orange", Fruit("Orange", "ORG", 62))

    def refresh():
        info_text.setText(f"currentText(): {combo.currentText()}")
        info_data.setText(f"currentData(): {combo.currentData()}")

    combo.selectionChanged.connect(lambda _: refresh())

    # Helper button to show a JSON-friendly projection of selected objects
    btn_dump = QPushButton("Dump selected objects as dicts")

    def dump_as_dicts():
        objs = combo.currentData() or []
        info_data.setText(f"as dicts: {[asdict(o) if hasattr(o, '__dataclass_fields__') else o for o in objs]}")

    btn_dump.clicked.connect(dump_as_dicts)

    layout.addWidget(combo)
    layout.addWidget(info_text)
    layout.addWidget(info_data)
    layout.addWidget(btn_dump)

    window.setCentralWidget(central)
    window.resize(640, 320)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
