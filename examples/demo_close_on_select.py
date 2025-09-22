import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from pyqt6_multiselect_combobox import MultiSelectComboBox


def build_widget(close_on_select: bool) -> QWidget:
    w = QWidget()
    layout = QVBoxLayout(w)

    title = QLabel(f"Close on select: {'ON' if close_on_select else 'OFF'}")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    combo = MultiSelectComboBox()
    combo.addItems(["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"])  # sample items
    combo.setSelectAllEnabled(True)
    combo.setDisplayType("text")
    combo.setPlaceholderText("Pick fruits…")
    combo.setCloseOnSelect(close_on_select)
    layout.addWidget(combo)

    info = QLabel(
        "Open the dropdown and click an item.\n"
        "When Close on select is ON, the popup should close immediately\n"
        "after the click (both for items and the 'Select All' row)."
    )
    info.setWordWrap(True)
    layout.addWidget(info)

    # Convenience: button to open the popup for quick manual checks
    btn = QPushButton("Open Popup")
    btn.clicked.connect(combo.showPopup)
    layout.addWidget(btn)

    return w


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    root = QWidget()
    root.setWindowTitle("MultiSelectComboBox – Close on Select Demo")
    lay = QVBoxLayout(root)

    lay.addWidget(build_widget(close_on_select=True))
    lay.addWidget(build_widget(close_on_select=False))

    root.resize(420, 300)
    root.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
