Changelog
=========

1.2.0 (2025-09-20)
------------------
- **Features**
  - Add QComboBox API parity and selection helpers in ``pyqt6_multiselect_combobox/multiselect_combobox.py``.
  - Add typing annotations and configurable output data role.
- **Fixes**
  - Ensure items are checkable and labels update correctly.
  - Reconnect model signals on ``setModel`` to keep UI in sync.
  - Make display joining robust for non-strings.
- **Performance**
  - Cache checked indices and coalesce UI updates for smoother behavior in ``pyqt6_multiselect_combobox/multiselect_combobox.py``.
- **Examples**
  - Add comprehensive demo scripts and assets: ``examples/demo.py``, ``examples/demo_signals_*``, ``examples/demo_select_all.py``, ``examples/demo_runtime_role_switch.py``, and more; plus ``assets/chevron-down.svg``.
- **Tests**
  - Add comprehensive test suite and coverage; expand ``tests/test_multiselect_combobox.py`` for new behaviors.
- **Docs**
  - Update ``README.md`` with CI and coverage badges and pyproject-based build/install notes.
- **Build/CI**
  - Migrate to ``pyproject.toml``; remove ``setup.py``.
  - Add PyPI publish workflow and enable Trusted Publishing via OIDC (``.github/workflows/publish.yml``).
  - Add tests and coverage workflow; update Codecov action; install Qt/OpenGL libs on Linux; adjust pip cache config (``.github/workflows/tests.yml``).
- **Maintenance**
  - Bump version to ``1.2.0`` in ``pyproject.toml``.
  - Update ``.gitignore``.

1.1.1
-----

1.1.0
-----
- Parity helpers and bulk update APIs.

1.0.0
-----
- Initial stable release.
