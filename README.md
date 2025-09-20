# MultiSelectComboBox

![CI - Tests](https://github.com/user0706/pyqt6-multiselect-combobox/actions/workflows/tests.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/user0706/pyqt6-multiselect-combobox/graph/badge.svg)](https://app.codecov.io/gh/user0706/pyqt6-multiselect-combobox)

MultiSelectComboBox is a custom widget built using PyQt6 that provides a dropdown combo box allowing users to select multiple items. This widget is particularly useful in scenarios where users need to select multiple options from a list.

## Purpose
The primary purpose of MultiSelectComboBox is to offer a user-friendly interface for selecting multiple items from a list efficiently. It allows users to choose from a set of options and displays the selected items in a compact manner.

## Features
- **Multiple Selection**: Users can select multiple items from the dropdown list.
- **Customizable Display**: The widget allows customization of the display format for both the selected items and the dropdown items.
- **Output Control**: Users can control whether the output should be in the form of data or text.
- **Configurable Data Role**: Control which Qt data role is used for outputs via `setOutputDataRole()`/`getOutputDataRole()`; defaults to `Qt.ItemDataRole.UserRole`.
- **Display Delimiter**: Users can specify a custom delimiter to separate the displayed items.
- **Resizable**: The widget dynamically adjusts its size to accommodate the selected items.
- **User-friendly Interface**: The interface is designed to be intuitive, allowing users to easily select and deselect items.
 - **QComboBox API Parity**: Implements `currentText()`, `setCurrentText()` (string or list), `findText()`, `findData()`.
 - **Bulk Selection Helpers**: `selectAll()`, `clearSelection()`, `invertSelection()`.
 - **Optional "Select All" Item**: Tri-state pseudo-item at the top with `setSelectAllEnabled(True)`.
 - **Signals**: Emits `selectionChanged(list)` whenever selection changes.
 - **Duplicate Policy**: Control duplicates via `setDuplicatesEnabled(bool)`; enforced in `addItem`/`addItems`.
 - **Performance & Scaling**: Efficient with large item counts via a cached set of checked indices, coalesced UI refresh with `QTimer.singleShot(0, ...)`, and public batch APIs `beginUpdate()` / `endUpdate()`.

See all features in [documentation](https://pyqt6-multiselect-combobox.readthedocs.io/en/latest/).

## How to Use
To use the MultiSelectComboBox widget in your PyQt6 application, follow these steps:

1. **Installation**: Install the package using pip:
   ```
   pip install pyqt6-multiselect-combobox
   ```

   Or install from source (editable/development mode):
   ```bash
   git clone https://github.com/user0706/pyqt6-multiselect-combobox.git
   cd pyqt6-multiselect-combobox
   pip install -e .
   ```

   To build local distribution artifacts (requires the "build" package):
   ```bash
   python -m pip install --upgrade build
   python -m build  # creates dist/*.whl and dist/*.tar.gz using pyproject.toml
   ```

2. **Import**: Import the MultiSelectComboBox class into your Python code:
   ```python
   from pyqt6_multiselect_combobox import MultiSelectComboBox
   ```

3. **Initialization**: Create an instance of MultiSelectComboBox:
   ```python
   multi_select_combo_box = MultiSelectComboBox()
   ```

4. **Adding Items**: Add items to the dropdown list using `addItem()` or `addItems()` methods:
   ```python
   multi_select_combo_box.addItem("Item 1", "Data 1")
   multi_select_combo_box.addItem("Item 2", "Data 2")
   multi_select_combo_box.addItems(["Item 3", "Item 4"], ["Data 3", "Data 4"])
   ```

5. **Customization**: Customize the display format, output type, and display delimiter as needed:
   ```python
   multi_select_combo_box.setDisplayType("text")
   multi_select_combo_box.setOutputType("data")
   multi_select_combo_box.setDisplayDelimiter(", ")
   multi_select_combo_box.setSelectAllEnabled(True)  # optional tri-state 'Select All' at the top
   ```

6. **Event Handling**: Handle events such as item selection and deselection if required.

7. **Accessing Selected Data**: Retrieve the selected data using the `currentData()` method:
   ```python
   selected_data = multi_select_combo_box.currentData()
   ```

8. **Accessing Display Text**: Retrieve the un-elided joined display text using `currentText()`:
   ```python
   joined_text = multi_select_combo_box.currentText()
   ```

9. **Programmatic Selection**:
   ```python
   # select by joined string (uses display delimiter)
   multi_select_combo_box.setCurrentText("Apple, Banana")
   # or by list of strings (matches text or data)
   multi_select_combo_box.setCurrentText(["Apple", "Orange"]) 
   ```

10. **Bulk Selection Helpers**:
    ```python
   multi_select_combo_box.selectAll()
   multi_select_combo_box.clearSelection()
   multi_select_combo_box.invertSelection()
   ```

11. **Find Helpers**:
    ```python
   idx_text = multi_select_combo_box.findText("Banana")
   idx_data = multi_select_combo_box.findData("Data 2")
   ```

13. **Data/Text Roles and Output Role**

   - Methods that return values based on the configured type, such as `currentData()` and the `'data'` branch of `typeSelection(index, ...)`, read item data using the widget's configured output data role.
   - By default, the output data role is `Qt.ItemDataRole.UserRole`, which aligns with Qt idioms for storing custom item data.
   - You can change which role is used when reading data with:
     ```python
     from PyQt6.QtCore import Qt

     multi_select_combo_box.setOutputDataRole(Qt.ItemDataRole.UserRole)
     role = multi_select_combo_box.getOutputDataRole()
     ```
   - Note: `addItem(text, data)` and `addItems(texts, dataList)` store the provided `data` into `Qt.ItemDataRole.UserRole`. If you switch the output role, ensure your items have data populated at that role (e.g., by setting it yourself on the underlying model items).

   - The helper `typeSelection(index, type_variable, expected_type='data')` returns:
     - `item.data(getOutputDataRole())` when `type_variable == expected_type` (default is `'data'`).
     - `item.text()` otherwise.

12. **Listen to Selection Changes**:
    ```python
   def on_selection_changed(values):
       print("Selected values:", values)

   multi_select_combo_box.selectionChanged.connect(on_selection_changed)
   ```

## Example
```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from pyqt6_multiselect_combobox import MultiSelectComboBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MultiSelectComboBox Example")
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        multi_select_combo_box = MultiSelectComboBox()
        multi_select_combo_box.addItems(["Apple", "Banana", "Orange"])
        
        layout.addWidget(multi_select_combo_box)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
```

## Examples
A set of runnable demos is provided under the `examples/` directory:

- `examples/demo.py` — Minimal demo showing basic usage and live selection updates.
  ```bash
  python examples/demo.py
  ```

- `examples/demo_select_all.py` — Demonstrates the optional tri-state "Select All" item.
  ```bash
  python examples/demo_select_all.py
  ```

- `examples/demo_data_role.py` — Shows returning values via data roles with `currentData()` vs `currentText()`.
  ```bash
  python examples/demo_data_role.py
  ```

- `examples/demo_objects.py` — Adds custom Python objects (e.g., dataclasses) as item data and reads them back.
  ```bash
  python examples/demo_objects.py
  ```

- `examples/demo_programmatic_selection.py` — Programmatically selects items using `setCurrentText()` (string and list forms).
  ```bash
  python examples/demo_programmatic_selection.py
  ```

- `examples/demo_batch_update.py` — Uses `beginUpdate()`/`endUpdate()` with bulk selection helpers.
  ```bash
  python examples/demo_batch_update.py
  ```

### Styling Examples

- `examples/demo_custom_style.py` — Dark theme using palette + style sheet for combo, popup, and scrollbars.
  ```bash
  python examples/demo_custom_style.py
  ```

- `examples/demo_custom_style_light.py` — Light theme variant with hover/focus borders.
  ```bash
  python examples/demo_custom_style_light.py
  ```

- `examples/demo_custom_style_hover_icon.py` — Custom arrow icon plus hover/focus styles. Uses `assets/chevron-down.svg`.
  ```bash
  python examples/demo_custom_style_hover_icon.py
  ```

- `examples/demo_per_item_styles.py` — Per-item colors/fonts via model roles (`ForegroundRole`, `FontRole`).
  ```bash
  python examples/demo_per_item_styles.py
  ```

## Screenshots / GIFs

Screenshots and short GIFs demonstrating the widget in action are welcome! If you have nice captures, please submit a PR adding them under a new `assets/` directory and link them here. Example placeholders:

<!--
![Basic usage](assets/basic-usage.png)
![Selection demo](assets/selection-demo.gif)
-->

## Additional Notes
- **Compatibility**: MultiSelectComboBox is compatible with PyQt6.
- **Duplicate Policy**: When duplicates are disabled (`setDuplicatesEnabled(False)`), `addItem`/`addItems` will skip adding any item whose text OR data matches an existing option. This check ignores the optional "Select All" item.
- **Feedback and Contributions**: Feedback and contributions are welcome. Feel free to open an issue or submit a pull request on [GitHub](https://github.com/user0706/pyqt6-multiselect-combobox).
- **License**: This package is provided under the MIT License.

## Performance and Scaling

When using thousands of items, repeatedly scanning the entire model on every change can be expensive. The widget includes several optimizations to keep interactions smooth:

- Cached checked indices: Maintains a set of checked rows to avoid O(n) scans on every `dataChanged`.
- Coalesced updates: Defers UI refresh work with `QTimer.singleShot(0, ...)` so multiple rapid changes are batched into one `updateText()`/signal emission cycle.
- Model structure handling: Listens to `rowsInserted`, `rowsRemoved`, and `modelReset` to rebuild caches only when necessary.
- Public batching API: Use `beginUpdate()` / `endUpdate()` to coalesce large batch operations (e.g., bulk selecting/adding items) into a single refresh.

Example: batch set selection with a single refresh

```python
combo.beginUpdate()
try:
    # Perform many changes without incurring multiple refreshes
    combo.clearSelection()
    combo.setCurrentIndexes([1, 5, 9])  # or any number of programmatic toggles
finally:
    combo.endUpdate()  # triggers one coalesced update
```

## Testing & Coverage
This repo includes a pytest suite. To run with coverage using `pytest-cov`:

```bash
pip install pytest pytest-cov
python -m pytest  # or: pytest
```

Coverage configuration is provided via `pytest.ini`. It reports terminal summary and writes an XML report to `coverage.xml`.

For more detailed usage and customization options, refer to the [documentation](https://pyqt6-multiselect-combobox.readthedocs.io/en/latest/).