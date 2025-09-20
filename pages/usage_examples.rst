Usage Examples
==============

Basic usage
-----------
.. code-block:: python

   from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
   from pyqt6_multiselect_combobox import MultiSelectComboBox

   class MainWindow(QMainWindow):
       def __init__(self):
           super().__init__()
           self.setWindowTitle("MultiSelectComboBox Example")

           central_widget = QWidget()
           layout = QVBoxLayout(central_widget)

           combo = MultiSelectComboBox()
           combo.addItems(["Apple", "Banana", "Orange"])
           combo.setSelectAllEnabled(True)

           layout.addWidget(combo)
           self.setCentralWidget(central_widget)

   if __name__ == "__main__":
       app = QApplication([])
       window = MainWindow()
       window.show()
       app.exec()

Programmatic selection
----------------------
.. code-block:: python

   combo.setCurrentText("Apple, Banana")  # joined string (uses display delimiter)
   combo.setCurrentText(["Apple", "Orange"])  # list of strings

Bulk selection helpers
----------------------
.. code-block:: python

   combo.selectAll()
   combo.clearSelection()
   combo.invertSelection()

Working with data roles
-----------------------
.. code-block:: python

   from PyQt6.QtCore import Qt

   combo.setOutputDataRole(Qt.ItemDataRole.UserRole)
   role = combo.getOutputDataRole()

Signals
-------
.. code-block:: python

   def on_selection_changed(values):
       print("Selected values:", values)

   combo.selectionChanged.connect(on_selection_changed)

More examples
-------------
See the repository ``examples/`` folder for runnable scripts covering styling, batch updates, and more.
