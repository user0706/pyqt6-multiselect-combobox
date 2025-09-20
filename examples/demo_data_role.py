#!/usr/bin/env python3
# Demo: Using data role outputs (currentData) vs text

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Data Role Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label_text = QLabel("currentText():")
    label_data = QLabel("currentData():")

    combo = MultiSelectComboBox()
    combo.setSelectAllEnabled(False)

    # Add items with text + associated data
    combo.addItem("Apple", {"id": 1, "code": "APL"})
    combo.addItem("Banana", {"id": 2, "code": "BAN"})
    combo.addItem("Orange", {"id": 3, "code": "ORG"})

    # Optionally demonstrate switching output role (defaults to UserRole)
    combo.setOutputDataRole(Qt.ItemDataRole.UserRole)

    def on_selection_changed(values):
        # values depends on output role when using helper APIs; show both text and data explicitly
        label_text.setText(f"currentText(): {combo.currentText()}")
        label_data.setText(f"currentData(): {combo.currentData()}")

    combo.selectionChanged.connect(on_selection_changed)

    layout.addWidget(combo)
    layout.addWidget(label_text)
    layout.addWidget(label_data)

    window.setCentralWidget(central_widget)
    window.resize(520, 240)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
