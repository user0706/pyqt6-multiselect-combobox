# MultiSelectComboBox

MultiSelectComboBox is a custom widget built using PyQt6 that provides a dropdown combo box allowing users to select multiple items. This widget is particularly useful in scenarios where users need to select multiple options from a list.

## Purpose
The primary purpose of MultiSelectComboBox is to offer a user-friendly interface for selecting multiple items from a list efficiently. It allows users to choose from a set of options and displays the selected items in a compact manner.

## Features
- **Multiple Selection**: Users can select multiple items from the dropdown list.
- **Customizable Display**: The widget allows customization of the display format for both the selected items and the dropdown items.
- **Output Control**: Users can control whether the output should be in the form of data or text.
- **Display Delimiter**: Users can specify a custom delimiter to separate the displayed items.
- **Resizable**: The widget dynamically adjusts its size to accommodate the selected items.
- **User-friendly Interface**: The interface is designed to be intuitive, allowing users to easily select and deselect items.

See all features in [documentation](https://pyqt6-multiselect-combobox.readthedocs.io/en/latest/).

## How to Use
To use the MultiSelectComboBox widget in your PyQt6 application, follow these steps:

1. **Installation**: Install the package using pip:
   ```
   pip install pyqt6-multiselect-combobox
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
   ```

6. **Event Handling**: Handle events such as item selection and deselection if required.

7. **Accessing Selected Data**: Retrieve the selected data using the `currentData()` method:
   ```python
   selected_data = multi_select_combo_box.currentData()
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

## Additional Notes
- **Compatibility**: MultiSelectComboBox is compatible with PyQt6.
- **Feedback and Contributions**: Feedback and contributions are welcome. Feel free to open an issue or submit a pull request on [GitHub](https://github.com/user0706/pyqt6-multiselect-combobox).
- **License**: This package is provided under the MIT License.

For more detailed usage and customization options, refer to the [documentation](https://pyqt6-multiselect-combobox.readthedocs.io/en/latest/).