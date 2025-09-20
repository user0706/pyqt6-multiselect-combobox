#!/usr/bin/env python3
# Demo: Light theme styling via Qt Style Sheets and palette

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from pyqt6_multiselect_combobox import MultiSelectComboBox


LIGHT_STYLESHEET = """
QComboBox {
    background-color: #ffffff;
    color: #222222;
    border: 1px solid #cfcfcf;
    border-radius: 6px;
    padding: 4px 8px;
}
QComboBox:hover {
    border-color: #999999;
}
QComboBox:focus {
    border-color: #3d6dad;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #cfcfcf;
}
QAbstractItemView {
    background-color: #ffffff;
    color: #222222;
    selection-background-color: #3d6dad;
    selection-color: #ffffff;
    outline: 0;
    border: 1px solid #cfcfcf;
}
"""


def main():
    app = QApplication([])

    # Light palette
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#f7f7f7"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#222222"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#222222"))
    app.setPalette(pal)

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Light Styling Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    label = QLabel("Styled (light) MultiSelectComboBox")

    combo = MultiSelectComboBox()
    combo.addItems(["Apple", "Banana", "Orange", "Grape", "Mango", "Pear"])  # text-only
    combo.setStyleSheet(LIGHT_STYLESHEET)

    def on_selection_changed(values):
        label.setText(f"Light style selection: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    layout.addWidget(combo)
    layout.addWidget(label)

    window.setCentralWidget(central)
    window.resize(520, 260)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
