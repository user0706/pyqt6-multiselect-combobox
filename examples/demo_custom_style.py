#!/usr/bin/env python3
# Demo: Custom styling via Qt Style Sheets and palette

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from pyqt6_multiselect_combobox import MultiSelectComboBox


DARK_STYLESHEET = """
/* Style the combo box (closed state) */
QComboBox {
    background-color: #2b2b2b;
    color: #f0f0f0;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 4px 8px;
}

/* Arrow button */
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #555;
}

/* Arrow icon area */
QComboBox::down-arrow {
    image: none; /* You can provide your own icon here */
    width: 0; height: 0; /* hide default */
}

/* The popup list view */
QAbstractItemView {
    background-color: #333;
    color: #f0f0f0;
    selection-background-color: #3d6dad;
    selection-color: #ffffff;
    outline: 0;
    border: 1px solid #555;
}

/* Scrollbar styling for the popup */
QScrollBar:vertical {
    background: #2b2b2b;
    width: 10px;
    margin: 2px 0 2px 0;
}
QScrollBar::handle:vertical {
    background: #555;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0; /* hide arrows */
}
"""


def main():
    app = QApplication([])

    # Optional: dark-ish palette for the window
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#f0f0f0"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#2b2b2b"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#f0f0f0"))
    app.setPalette(pal)

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Custom Styling Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    label = QLabel("Styled MultiSelectComboBox with dark theme")

    combo = MultiSelectComboBox()
    combo.setSelectAllEnabled(True)
    combo.addItems(["Apple", "Banana", "Orange", "Grape", "Mango", "Pear"])  # text-only

    # Apply stylesheet: targets the QComboBox and its popup
    combo.setStyleSheet(DARK_STYLESHEET)

    def on_selection_changed(values):
        label.setText(f"Styled selection: {values}")

    combo.selectionChanged.connect(on_selection_changed)

    layout.addWidget(combo)
    layout.addWidget(label)

    window.setCentralWidget(central_widget)
    window.resize(520, 260)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
