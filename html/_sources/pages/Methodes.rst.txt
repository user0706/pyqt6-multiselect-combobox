Methodes
========

setOutputType
-------------

This method sets the output type for the combo box, allowing the user to specify whether the selected data or text should be returned when querying for the current selection.

**Usage Example:**

.. code-block:: python

    # Setting the output type to 'data'
    multi_select_combo_box.setOutputType("data")

setDisplayType
-------------

It sets the display type for the combo box, determining whether the items' data or text should be displayed in the combo box's line edit area.

**Usage Example:**

.. code-block:: python

    # Setting the display type to 'text'
    multi_select_combo_box.setDisplayType("text")

setDisplayDelimiter
-------------------

This method allows customization of the delimiter used to separate displayed items in the combo box, with optional parameters to include spaces before and after the delimiter.

**Usage Example:**

.. code-block:: python

    # Setting the display delimiter to ','
    multi_select_combo_box.setDisplayDelimiter(",", space_after=True, space_before=False)

getOutputType
-------------

It retrieves the current output type set for the combo box, indicating whether data or text will be returned when querying for the current selection.

**Usage Example:**

.. code-block:: python

    # Getting the current output type
    output_type = multi_select_combo_box.getOutputType()

getDisplayType
--------------

This method retrieves the current display type set for the combo box, indicating whether the items' data or text is displayed in the combo box's line edit area.

**Usage Example:**

.. code-block:: python

    # Getting the current display type
    display_type = multi_select_combo_box.getDisplayType()

getDisplayDelimiter
--------------------

It retrieves the current display delimiter set for the combo box, which is used to separate displayed items in the combo box.

**Usage Example:**

.. code-block:: python

    # Getting the current display delimiter
    delimiter = multi_select_combo_box.getDisplayDelimiter()

updateText
-----------

This method updates the displayed text in the combo box's line edit area based on the selected items, taking into account the display type and delimiter settings.

**Usage Example:**

.. code-block:: python

    # Updating the displayed text
    multi_select_combo_box.updateText()

addItem
-------

It adds a single item to the combo box, with options to specify both the displayed text and associated data for the item.

**Usage Example:**

.. code-block:: python

    # Adding an item with text only
    multi_select_combo_box.addItem("Item 1")

addItems
--------

This method adds multiple items to the combo box, taking lists of texts and optional associated data as input.

**Usage Example:**

.. code-block:: python

    # Adding multiple items with texts only
    multi_select_combo_box.addItems(["Item 3", "Item 4", "Item 5"])

currentData
------------

It retrieves the currently selected data from the combo box, returning a list of the selected items' data based on the current output type setting.

**Usage Example:**

.. code-block:: python

    # Getting the currently selected data
    selected_data = multi_select_combo_box.currentData()