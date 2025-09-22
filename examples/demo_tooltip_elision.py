import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    w = QWidget()
    w.setWindowTitle("MultiSelectComboBox – Tooltip on Elided Text")
    layout = QVBoxLayout(w)

    info = QLabel(
        "Resize the window narrow, select multiple items, and hover the combo to\n"
        "see the full selection as a tooltip while the display text is elided."
    )
    layout.addWidget(info)

    combo = MultiSelectComboBox()
    combo.setDisplayType("text")
    combo.setPlaceholderText("Pick items…")
    # Default: tooltip sync is enabled
    # combo.setElideToolTipEnabled(True)

    # Add long-ish items to demonstrate elision
    items = [
        "Washington",
        "Massachusetts",
        "North Carolina",
        "South Carolina",
        "Pennsylvania",
        "New Hampshire",
        "Rhode Island",
        "Connecticut",
        "Mississippi",
        "California",
    ]
    combo.addItems(items)

    # Make the widget relatively narrow to force elision sooner
    combo.resize(140, combo.height())

    layout.addWidget(combo)

    # Preselect a few to show effect immediately
    combo.setCurrentText(["Massachusetts", "Rhode Island", "Connecticut"])  # by text

    w.resize(360, 140)
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
