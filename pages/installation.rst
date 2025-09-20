Installation
============

Requirements
------------
- Python 3.8+
- PyQt6 6.6+

Install from PyPI
-----------------
.. code-block:: bash

   pip install pyqt6-multiselect-combobox

Install from source (development)
---------------------------------
.. code-block:: bash

   git clone https://github.com/user0706/pyqt6-multiselect-combobox.git
   cd pyqt6-multiselect-combobox
   pip install -e .

Building wheels/sdist locally
-----------------------------
.. code-block:: bash

   python -m pip install --upgrade build
   python -m build

Troubleshooting
---------------
- Ensure a working Qt backend is available when running examples.
- For headless CI, avoid actually creating a full GUI or use ``QT_QPA_PLATFORM=offscreen``.
