API Reference
=============

This section provides an overview of the primary methods and helpers exposed by the widget. For a narrative list with examples, also see :doc:`methodes <methodes>`.

Primary class
-------------
- ``pyqt6_multiselect_combobox.MultiSelectComboBox``

Key methods
-----------
- Selection and values: ``currentText()``, ``currentData()``, ``setCurrentText()``, ``getCurrentIndexes()``, ``setCurrentIndexes()``
- Helpers: ``selectAll()``, ``clearSelection()``, ``invertSelection()``, ``findText()``, ``findData()``
- Configuration: ``setOutputType()``, ``setDisplayType()``, ``setDisplayDelimiter()``, ``setSelectAllEnabled()``, ``setDuplicatesEnabled()``
- Roles: ``setOutputDataRole()``, ``getOutputDataRole()``
- Signals: ``selectionChanged(list)``

Note
----
Autodoc can be enabled later when the package module is accessible during Read the Docs builds.
