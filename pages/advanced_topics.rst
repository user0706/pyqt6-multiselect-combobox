Advanced Topics
===============

Performance and scaling
-----------------------
- Cached checked indices to avoid O(n) scans on every change.
- Coalesced UI updates using ``QTimer.singleShot(0, ...)``.
- Public batching API: ``beginUpdate()`` / ``endUpdate()`` to aggregate many changes into a single refresh.

Duplicate policy
----------------
- ``setDuplicatesEnabled(bool)`` controls whether adding items with duplicate text or data is allowed.

Select All item
---------------
- Enable a tri-state pseudo-item at the top via ``setSelectAllEnabled(True)``.
- Handy for large datasets where toggling all items is common.

Styling
-------
- Customize popup, scrollbars, and the arrow icon via stylesheets and palettes.
- See repository examples under ``examples/`` for dark/light themes and custom icons.
