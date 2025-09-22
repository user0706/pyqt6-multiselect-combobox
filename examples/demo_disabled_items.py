from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from pyqt6_multiselect_combobox import MultiSelectComboBox
import sys


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    w = QWidget()
    w.setWindowTitle("MultiSelectComboBox – Disabled Items Demo")
    layout = QVBoxLayout(w)

    label = QLabel("Items with a lock icon (disabled) cannot be toggled by mouse/keyboard.\n"
                   "Programmatic selection is still possible via the button.")
    label.setWordWrap(True)
    layout.addWidget(label)

    combo = MultiSelectComboBox()
    combo.setDisplayType("text")

    # Add items, marking some as disabled
    combo.addItem("Enabled: Apple", data={"id": 1})
    combo.addItem("Disabled: Banana", data={"id": 2}, enabled=False)
    combo.addItem("Enabled: Cherry", data={"id": 3})
    combo.addItem("Disabled: Date", data={"id": 4}, enabled=False)

    layout.addWidget(combo)

    btn_prog = QPushButton("Programmatically select disabled items (Banana, Date)")

    def on_prog_click():
        # Demonstrate that programmatic changes still work
        # Find indices of disabled items by text
        indices = []
        for i in range(combo.model().rowCount()):
            t = combo.model().item(i).text()
            if "Disabled" in t:
                indices.append(i)
        combo.setCurrentIndexes(indices)

    btn_prog.clicked.connect(on_prog_click)
    layout.addWidget(btn_prog)

    w.resize(420, 200)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
