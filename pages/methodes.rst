Methods
=========================

This class defines a custom combo box widget that enables multi-select functionality. Users can select multiple items from a dropdown list, which are then displayed in a comma-separated format in the combo box's line edit area.

setOutputType Method
--------------------

This method sets the output type for the combo box. It accepts either 'data' or 'text' as the output type. If an invalid output type is provided, it raises a ValueError.

**Usage Example:**

.. code-block:: python
    
    combo_box.setOutputType("data")

setDisplayType Method
---------------------

This method sets the display type for the combo box. It accepts either 'data' or 'text' as the display type. If an invalid display type is provided, it raises a ValueError.

**Usage Example:**

.. code-block:: python
    
    combo_box.setDisplayType("text")

setDisplayDelimiter Method
--------------------------

This method sets the display delimiter for the combo box. It allows customization of the delimiter, with options to include spaces before and after the delimiter.

**Usage Example:**

.. code-block:: python
    
    combo_box.setDisplayDelimiter("; ", space_after=True, space_before=False)

updateText Method
-----------------

This method updates the displayed text in the combo box based on the selected items. It formats the selected items into a comma-separated string and displays them in the line edit area.

**Usage Example:**

.. code-block:: python
    
    combo_box.updateText()

addItem Method
--------------

This method adds an item to the combo box. It takes the text to display and an optional associated data.

**Usage Example:**

.. code-block:: python
    
    combo_box.addItem("Item 1", "Data 1")

addItems Method
---------------

This method adds multiple items to the combo box. It accepts lists of texts and associated data, adding them to the combo box accordingly.

**Usage Example:**

.. code-block:: python
    
    combo_box.addItems(["Item 1", "Item 2", "Item 3"], ["Data 1", "Data 2", "Data 3"])

currentData Method
------------------

This method retrieves the currently selected data from the combo box.

**Usage Example:**

.. code-block:: python
    
    selected_data = combo_box.currentData()
    # Output used to look like: ["Data 1", "Data 3"]

setCurrentIndexes Method
------------------------

This method sets the selected items based on the provided indexes.

**Usage Example:**

.. code-block:: python
    
    combo_box.setCurrentIndexes([0, 2])

getCurrentIndexes Method
------------------------

This method retrieves the indexes of the currently selected items.

**Usage Example:**

.. code-block:: python
    
    selected_indexes = combo_box.getCurrentIndexes()
    # Output used to look like: [0, 2]

setPlaceholderText Method
-------------------------

This method sets the placeholder text for the combo box.

**Usage Example:**

.. code-block:: python
    
    combo_box.setPlaceholderText("Select items...")

getCurrentOptions Method
------------------------

This method retrieves the currently selected options along with their associated data.

**Usage Example:**

.. code-block:: python
    
    options = combo_box.getCurrentOptions()
    # Output used to look like: [("Item 1", "Data 1"), ("Item 3", "Data 3")]

getPlaceholderText Method
-------------------------

This method retrieves the placeholder text currently set for the combo box.

**Usage Example:**

.. code-block:: python
    
    placeholder_text = combo_box.getPlaceholderText()
    # Output used to look like: "Select items..."

setDuplicatesEnabled Method
----------------------------

This method sets whether duplicates are allowed in the combo box.

**Usage Example:**

.. code-block:: python
    
    combo_box.setDuplicatesEnabled(True)

isDuplicatesEnabled Method
---------------------------

This method checks if duplicates are allowed in the combo box.

**Usage Example:**

.. code-block:: python
    
    duplicates_allowed = combo_box.isDuplicatesEnabled()
    # Output used to look like: True