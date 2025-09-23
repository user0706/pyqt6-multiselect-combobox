#!/usr/bin/env python3
# Demo: Toggle coalescing (lazy text recompute) on/off and observe behavior

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest

from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - Coalescing Demo")

    central = QWidget()
    layout = QVBoxLayout(central)

    status_row = QHBoxLayout()
    status_label = QLabel("Coalescing: on | Pending update: False")

    combo = MultiSelectComboBox()
    combo.addItems([f"Item {i}" for i in range(1, 11)])
    combo.setDisplayType("text")

    def refresh_status():
        status_label.setText(
            f"Coalescing: {'on' if combo.isCoalescingEnabled() else 'off'} | "
            f"Pending update: {combo.isUpdateCoalesced()}"
        )

    # Keep status fresh
    timer = QTimer()
    timer.setInterval(20)
    timer.timeout.connect(refresh_status)
    timer.start()

    # Buttons to toggle coalescing
    btn_enable = QPushButton("Enable coalescing")
    btn_disable = QPushButton("Disable coalescing")

    def enable():
        combo.setCoalescingEnabled(True)
        refresh_status()

    def disable():
        combo.setCoalescingEnabled(False)
        refresh_status()

    btn_enable.clicked.connect(enable)
    btn_disable.clicked.connect(disable)

    # Buttons to trigger updates
    btn_select_all = QPushButton("Select All")
    btn_clear = QPushButton("Clear Selection")
    btn_toggle_first = QPushButton("Toggle first item")
    btn_burst_toggle = QPushButton("Burst toggle x21")

    btn_select_all.clicked.connect(combo.selectAll)
    btn_clear.clicked.connect(combo.clearSelection)

    def toggle_first():
        if combo.model().rowCount() > 0:
            it = combo.model().item(0)
            state = it.data(Qt.ItemDataRole.CheckStateRole)
            new_state = (
                Qt.CheckState.Unchecked
                if state == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            it.setData(new_state, Qt.ItemDataRole.CheckStateRole)
        # Show status immediately after scheduling; coalesced update will clear it
        refresh_status()

    def burst_toggle():
        # Rapidly toggle first item multiple times to keep pending state visible.
        # Use an odd count so the selection actually changes at the end,
        # ensuring selectionChanged emits and the "Selected:" label updates.
        for _ in range(21):
            toggle_first()
        # Allow deferred coalesced update (singleShot(0)) to fire and update UI/labels
        QApplication.processEvents()
        QTest.qWait(10)
        QApplication.processEvents()

    btn_toggle_first.clicked.connect(toggle_first)
    btn_burst_toggle.clicked.connect(burst_toggle)

    # Display selection changes
    selection_label = QLabel("Selected: []")

    def on_changed(values):
        selection_label.setText(f"Selected: {values}")
        refresh_status()

    combo.selectionChanged.connect(on_changed)

    # Layout
    status_row.addWidget(btn_enable)
    status_row.addWidget(btn_disable)
    layout.addWidget(combo)
    layout.addLayout(status_row)
    layout.addWidget(btn_select_all)
    layout.addWidget(btn_clear)
    layout.addWidget(btn_toggle_first)
    layout.addWidget(btn_burst_toggle)
    layout.addWidget(status_label)
    layout.addWidget(selection_label)

    window.setCentralWidget(central)
    window.resize(560, 360)
    window.show()

    refresh_status()
    app.exec()


if __name__ == "__main__":
    main()
