#!/usr/bin/env python3
# Demo: View virtualization (uniform item sizes + batched layout)

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QSpinBox,
    QCheckBox,
)
from pyqt6_multiselect_combobox import MultiSelectComboBox


def main():
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("MultiSelectComboBox - View Virtualization Demo")

    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    combo = MultiSelectComboBox()

    # Populate with a large number of items to make scrolling noticeable
    items = [f"Item {i:05d}" for i in range(1, 10001)]
    combo.addItems(items)

    # Controls for tuning
    controls_row = QHBoxLayout()

    chk_uniform = QCheckBox("Uniform item sizes")
    chk_uniform.setChecked(True)
    chk_uniform.toggled.connect(combo.setUniformItemSizesEnabled)

    lbl_batch = QLabel("Batch size:")
    spn_batch = QSpinBox()
    spn_batch.setRange(0, 5000)
    spn_batch.setValue(combo.getViewBatchSize())

    def apply_batch():
        size = int(spn_batch.value())
        combo.setViewBatchSize(size)

    btn_apply = QPushButton("Apply batch size")
    btn_apply.clicked.connect(apply_batch)

    # Helpers
    btn_disable_batch = QPushButton("Disable batching")
    btn_disable_batch.clicked.connect(lambda: (spn_batch.setValue(0), combo.setViewBatchSize(0)))

    controls_row.addWidget(chk_uniform)
    controls_row.addSpacing(12)
    controls_row.addWidget(lbl_batch)
    controls_row.addWidget(spn_batch)
    controls_row.addWidget(btn_apply)
    controls_row.addWidget(btn_disable_batch)
    controls_row.addStretch(1)

    layout.addWidget(QLabel("Try scrolling and adjusting options below to see performance effects."))
    layout.addLayout(controls_row)
    layout.addWidget(combo)

    window.setCentralWidget(central_widget)
    window.resize(700, 480)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
