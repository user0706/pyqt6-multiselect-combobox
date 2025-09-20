FAQ
===

Why don't I see any items when I open the combo?
-----------------------------------------------
- Ensure you've called ``addItem`` / ``addItems`` and that the widget is added to a visible parent/layout.

How do I read values as data instead of text?
---------------------------------------------
- Use ``currentData()`` and configure which role is read with ``setOutputDataRole()``.

How can I programmatically choose items?
----------------------------------------
- Use ``setCurrentText()`` with either a joined string (using the configured display delimiter) or a list of strings.

Can I disable duplicate options?
--------------------------------
- Yes, call ``setDuplicatesEnabled(False)`` to prevent adding items with duplicate text or data.
