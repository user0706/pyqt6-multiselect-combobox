from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
import sys

from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    w = QWidget()
    w.setWindowTitle("MultiSelectComboBox - Summary display demo")
    layout = QVBoxLayout(w)

    info = QLabel("""
This demo shows optional summarization of selected items.

- Leading mode with threshold=2: shows first 2, then "… +N more"
- Count mode with threshold=0: always shows "N selected"
    """.strip())
    layout.addWidget(info)

    # Leading mode example
    combo_leading = MultiSelectComboBox()
    combo_leading.setPlaceholderText("Pick fruits…")
    combo_leading.setDisplayType("text")
    combo_leading.addItems(["Apple", "Banana", "Cherry", "Date", "Elderberry"])  # 5 items
    combo_leading.setSummaryMode("leading")
    combo_leading.setSummaryThreshold(2)  # show up to 2, then summarize
    combo_leading.setCurrentIndexes([0, 1, 2])
    layout.addWidget(QLabel("Leading mode (threshold=2)"))
    layout.addWidget(combo_leading)

    # Count mode example
    combo_count = MultiSelectComboBox()
    combo_count.setPlaceholderText("Pick letters…")
    combo_count.setDisplayType("text")
    combo_count.addItems(["A", "B", "C", "D"])  # 4 items
    combo_count.setSummaryMode("count")
    combo_count.setSummaryThreshold(0)  # always summarize
    combo_count.setCurrentIndexes([0, 1, 2])
    layout.addWidget(QLabel("Count mode (threshold=0)"))
    layout.addWidget(combo_count)

    # Custom format example
    combo_custom = MultiSelectComboBox()
    combo_custom.setPlaceholderText("Pick numbers…")
    combo_custom.setDisplayType("text")
    combo_custom.addItems(["One", "Two", "Three", "Four"])  # 4 items
    combo_custom.setSummaryMode("leading")
    combo_custom.setSummaryThreshold(1)
    combo_custom.setSummaryFormat(leading="{shown} and {more} others")
    combo_custom.setCurrentIndexes([0, 1, 2, 3])
    layout.addWidget(QLabel("Custom leading format (threshold=1)"))
    layout.addWidget(combo_custom)

    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
