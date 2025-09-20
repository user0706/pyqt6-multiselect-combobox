PyQt6 MultiSelectComboBox
=========================

PyQt6 MultiSelectComboBox is a drop-in widget that brings multi-selection to a familiar ``QComboBox``-like interface. It supports performant selection with thousands of items, batch updates, an optional "Select All" item, and a friendly API.

Quick links: `PyPI <https://pypi.org/project/pyqt6-multiselect-combobox/>`_ · `GitHub <https://github.com/user0706/pyqt6-multiselect-combobox>`_ · `Issues <https://github.com/user0706/pyqt6-multiselect-combobox/issues>`_

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Install

      .. code-block:: bash

         pip install pyqt6-multiselect-combobox

   .. grid-item-card:: Minimal usage

      .. code-block:: python

         from pyqt6_multiselect_combobox import MultiSelectComboBox
         combo = MultiSelectComboBox()
         combo.addItems(["Apple", "Banana", "Orange"])
         combo.setSelectAllEnabled(True)

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   pages/introduction
   pages/installation
   pages/usage_examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   pages/api_reference
   pages/methodes

.. toctree::
   :maxdepth: 2
   :caption: Advanced

   pages/advanced_topics

.. toctree::
   :maxdepth: 1
   :caption: Community

   pages/contributing
   pages/faq

.. toctree::
   :maxdepth: 1
   :caption: Changelog

   pages/changelog
