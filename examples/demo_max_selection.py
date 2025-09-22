from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import sys

from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    w = QWidget()
    w.setWindowTitle("MultiSelectComboBox - Max Selection Demo")
    layout = QVBoxLayout(w)

    info = QLabel(
        "This demo sets a maximum of 2 selections.\n"
        "Try selecting more than 2 items using mouse or keyboard.\n"
        "A tooltip will inform you when the limit is reached."
    )
    info.setWordWrap(True)

    combo = MultiSelectComboBox()
    combo.setPlaceholderText("Pick up to 2 fruits")
    combo.addItems(["Apple", "Banana", "Cherry", "Date", "Elderberry"])  # 5 items
    combo.setSelectAllEnabled(True)
    combo.setFilterEnabled(True)
    combo.setDisplayType("text")
    combo.setMaxSelectionCount(2)

    layout.addWidget(info)
    layout.addWidget(combo)

    w.resize(420, 180)
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
