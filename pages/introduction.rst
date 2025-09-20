Introduction
===========

PyQt6 MultiSelectComboBox is a custom widget that extends the idea of ``QComboBox`` to allow selecting multiple items. It focuses on:

- Performance with large item sets
- Clean, convenient APIs similar to ``QComboBox``
- Fine-grained control over output type (text or data) and data roles
- Optional tri-state "Select All" item
- Batch APIs for updating without flicker

Who is this for?
----------------
- Developers building PyQt6 apps who need a compact, discoverable multi-select UI.
- Teams wanting a lightweight dependency with strong defaults and good customization.

Key capabilities
----------------
- Multiple selection with checkable items
- Output control (``currentText()`` vs ``currentData()``) and configurable data role
- Bulk helpers: ``selectAll()``, ``clearSelection()``, ``invertSelection()``
- Programmatic selection via ``setCurrentText()`` (string or list)
- Parity helpers: ``findText()``, ``findData()``

Next steps
----------
- See :doc:`installation <installation>` to install the package.
- Jump to :doc:`usage_examples <usage_examples>` for common scenarios.
- Browse the :doc:`api_reference <api_reference>` for the API surface.
