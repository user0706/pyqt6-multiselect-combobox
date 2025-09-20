from typing import Any, Iterable, List, Optional, Tuple

from PyQt6.QtWidgets import QComboBox, QStyledItemDelegate
from PyQt6.QtGui import QStandardItem, QPalette, QFontMetrics
from PyQt6.QtCore import Qt, QEvent, pyqtSignal, QObject, QTimerEvent, QTimer


class MultiSelectComboBox(QComboBox):
    """
    A custom combo box widget that allows for multi-select functionality.

    This widget provides the ability to select multiple items from a dropdown list and display them in a comma-separated format in the combo box's line edit area.
    """

    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):  # pragma: no cover (cosmetic GUI sizing)
            size = super().sizeHint(option, index)
            # HiDPI-aware height based on font metrics with a small padding
            try:
                metrics = option.fontMetrics  # type: ignore[attr-defined]
            except Exception:
                metrics = QFontMetrics(option.font)
            padding = 6
            size.setHeight(metrics.height() + padding)
            return size

    # Emitted when the selection set changes. Emits list of currently selected values
    # based on output type (text or data), similar to currentData().
    selectionChanged = pyqtSignal(list)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.placeholderText = ""
        self.display_delimiter = ", "
        self.output_type = "data"
        self.display_type = "data"
        self.duplicatesEnabled = True
        self._lastSelectionSnapshot = []
        self._inBulkUpdate = False
        self._selectAllEnabled = False
        self._selectAllText = "Select All"
        # Cache of checked rows for performance on large models
        self._checkedRows: set[int] = set()
        # Coalesced update scheduling flag
        self._updateScheduled: bool = False

        # Output data role used when reading item data (e.g., for currentData())
        # Defaults to Qt.ItemDataRole.UserRole to align with Qt idioms.
        self._outputDataRole: Qt.ItemDataRole = Qt.ItemDataRole.UserRole

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        palette = self.lineEdit().palette()
        palette.setBrush(
            QPalette.ColorRole.Base, palette.brush(QPalette.ColorRole.Button)
        )
        self.lineEdit().setPalette(palette)

        self.setItemDelegate(MultiSelectComboBox.Delegate())
        self.setOutputType("data")
        self.setDisplayType("text")
        self.setDisplayDelimiter(",")

        # Connect to current model's signals
        self._connectModelSignals(self.model())
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False
        self.view().viewport().installEventFilter(self)
        self.view().installEventFilter(self)  # for key handling when popup open

        # Whether selecting an item should close the popup (configurable)
        self._closeOnSelect = False

        # Reentrancy guard for updateText
        self._updatingText = False

        # Initialize caches
        self._rebuildCheckedCache()

    def setOutputType(self, output_type: str) -> None:
        """Set the output type for the combo box.

        Args:
            output_type (str): The output type, either 'data' or 'text'.

        Raises:
            ValueError: If output_type is neither 'data' nor 'text'.
        """
        if output_type in ["data", "text"]:
            self.output_type = output_type
        else:
            raise ValueError("Output type must be 'data' or 'text'")

    def setDisplayType(self, display_type: str) -> None:
        """Set the display type for the combo box.

        Args:
            display_type (str): The display type, either 'data' or 'text'.

        Raises:
            ValueError: If display_type is neither 'data' nor 'text'.
        """
        if display_type in ["data", "text"]:
            self.display_type = display_type
        else:
            raise ValueError("Display type must be 'data' or 'text'")

    def getOutputType(self) -> str:
        """Get the current output type.

        Returns:
            str: The current output type, either 'data' or 'text'.
        """
        return self.output_type

    def getDisplayType(self) -> str:
        """Get the current display type.

        Returns:
            str: The current display type, either 'data' or 'text'.
        """
        return self.display_type

    def setDisplayDelimiter(self, delimiter: str, space_after: bool = True, space_before: bool = False) -> None:
        """Set the display delimiter for the combo box.

        Args:
            delimiter (str): The delimiter to use.
            space_after (bool): Whether to add a space after the delimiter. Default is True.
            space_before (bool): Whether to add a space before the delimiter. Default is False.
        """
        # If the provided delimiter already contains leading/trailing spaces,
        # respect it as-is and ignore spacing flags.
        if delimiter != delimiter.strip():
            self.display_delimiter = delimiter
            return
        suffix = " " if space_after else ""
        prefix = " " if space_before else ""
        self.display_delimiter = prefix + delimiter + suffix

    def getDisplayDelimiter(self) -> str:
        """Get the current display delimiter.

        Returns:
            str: The current display delimiter.
        """
        return self.display_delimiter

    def resizeEvent(self, event) -> None:
        """Resize event handler.

        Args:
            event: The resize event.
        """
        self.updateText()
        super().resizeEvent(event)

    # Ensure we stay wired to whichever model is attached to the combo box
    def setModel(self, model) -> None:  # type: ignore[override]
        """Override to reconnect signals when a custom model is set at runtime."""
        try:
            old = self.model()
        except Exception:
            old = None
        if old is not None:
            self._disconnectModelSignals(old)
        super().setModel(model)
        self._connectModelSignals(self.model())
        # Rebuild caches and refresh UI to reflect the new model state
        self._rebuildCheckedCache()
        self._performCoalescedUpdate()

    def _connectModelSignals(self, m) -> None:
        try:
            m.dataChanged.connect(self._onModelDataChanged)
        except Exception:
            pass
        try:
            m.rowsInserted.connect(self._onRowsInserted)
        except Exception:
            pass
        try:
            m.rowsRemoved.connect(self._onRowsRemoved)
        except Exception:
            pass
        try:
            m.modelReset.connect(self._onModelReset)
        except Exception:
            # Some models may not expose modelReset the same way; ignore
            pass

    def _disconnectModelSignals(self, m) -> None:
        # Best-effort disconnect to avoid duplicate connections
        try:
            m.dataChanged.disconnect(self._onModelDataChanged)
        except Exception:
            pass
        try:
            m.rowsInserted.disconnect(self._onRowsInserted)
        except Exception:
            pass
        try:
            m.rowsRemoved.disconnect(self._onRowsRemoved)
        except Exception:
            pass
        try:
            m.modelReset.disconnect(self._onModelReset)
        except Exception:
            pass

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Event filter to handle mouse button release events.

        Args:
            obj: The object emitting the event.
            event: The event being emitted.

        Returns:
            bool: True if the event was handled, False otherwise.
        """
        if obj == self.lineEdit() and event.type() == QEvent.Type.MouseButtonRelease:
            if self.closeOnLineEditClick:
                self.hidePopup()
            else:
                self.showPopup()
            return True
        # Keyboard support when popup is open: Space/Enter toggles highlighted row
        if obj in (self.view(), self.view().viewport()) and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                index = self.view().currentIndex()
                if index.isValid():
                    row = index.row()
                    if self._selectAllEnabled and row == 0:
                        sa_item = self.model().item(0)
                        state = sa_item.data(Qt.ItemDataRole.CheckStateRole)
                        if state in (Qt.CheckState.Unchecked, Qt.CheckState.PartiallyChecked):
                            self.selectAll()
                        else:
                            self.clearSelection()
                    else:
                        item = self.model().itemFromIndex(index)
                        state = item.data(Qt.ItemDataRole.CheckStateRole)
                        new_state = Qt.CheckState.Unchecked if state == Qt.CheckState.Checked else Qt.CheckState.Checked
                        item.setData(new_state, Qt.ItemDataRole.CheckStateRole)
                        self._syncSelectAllState()
                        self._emitSelectionIfChanged()
                    if self._closeOnSelect:
                        # Close the QComboBox popup and ensure the view is hidden
                        self.hidePopup()
                        self._forceHidePopupView()
                    return True
        if obj == self.view().viewport() and event.type() == QEvent.Type.MouseButtonRelease:
            index = self.view().indexAt(event.position().toPoint())
            if not index.isValid():
                return False
            row = index.row()
            if self._selectAllEnabled and row == 0:
                # Toggle tri-state 'Select All'
                sa_item = self.model().item(0)
                state = sa_item.data(Qt.ItemDataRole.CheckStateRole)
                if state in (Qt.CheckState.Unchecked, Qt.CheckState.PartiallyChecked):
                    self.selectAll()
                else:
                    self.clearSelection()
                if self._closeOnSelect:
                    # Close the QComboBox popup and ensure the view is hidden
                    self.hidePopup()
                    self._forceHidePopupView()
                return True
            else:
                item = self.model().itemFromIndex(index)
                state = item.data(Qt.ItemDataRole.CheckStateRole)
                new_state = Qt.CheckState.Unchecked if state == Qt.CheckState.Checked else Qt.CheckState.Checked
                item.setData(new_state, Qt.ItemDataRole.CheckStateRole)
                # Update Select All state and emit selection change
                self._syncSelectAllState()
                self._emitSelectionIfChanged()
                if self._closeOnSelect:
                    self.hidePopup()
                return True
        return False

    def showPopup(self) -> None:
        """Show the combo box popup.
        """
        super().showPopup()
        self.closeOnLineEditClick = True

    def hidePopup(self) -> None:
        """Hide the combo box popup.
        """
        super().hidePopup()
        self.startTimer(100)

    def _forceHidePopupView(self) -> None:
        """Ensure the internal view used for the popup is hidden immediately."""
        try:
            v = self.view()
            v.hide()
            if v.viewport() is not None:
                v.viewport().hide()
        except Exception:
            pass

    def timerEvent(self, event: QTimerEvent) -> None:
        """Timer event handler.

        Args:
            event: The timer event.
        """
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def typeSelection(self, index: int, type_variable: str, expected_type: str = "data") -> Any:
        """Get the selected item's data (for the configured role) or text.

        Args:
            index (int): The index of the item.
            type_variable (str): The type variable to retrieve ('data' or 'text').
            expected_type (str): The expected type. Default is 'data'.

        Returns:
            Any: The selected item's data (read using getOutputDataRole()) or the
                item's text (str) depending on the requested type.
        
        Note:
            When returning data, the value is read using the currently configured
            output data role (see setOutputDataRole/getOutputDataRole). By default,
            this is Qt.ItemDataRole.UserRole. This differs from Qt's display role
            and aligns with QStandardItem.setData default role semantics.
        """
        if type_variable == expected_type:
            return self.model().item(index).data(int(self._outputDataRole))
        return self.model().item(index).text()

    def updateText(self) -> None:
        """Update the displayed text based on selected items.
        """
        if self._updatingText:
            return
        self._updatingText = True
        try:
            display_type = self.getDisplayType()
            delimiter = self.getDisplayDelimiter()
            # Build texts using cached checked rows to avoid scanning full model
            rows = sorted(r for r in self._checkedRows if self._isOptionRow(r))
            texts = [self.typeSelection(i, display_type) for i in rows]

            if texts:
                text = delimiter.join(str(t) for t in texts)
            else:
                text = self.placeholderText if hasattr(self, 'placeholderText') else ""

            # Also set native placeholder for better styling when empty
            if not texts:
                self.lineEdit().setPlaceholderText(self.placeholderText)

            metrics = QFontMetrics(self.lineEdit().font())
            elidedText = metrics.elidedText(
                text, Qt.TextElideMode.ElideRight, self.lineEdit().width()
            )
            # Block signals during programmatic update to avoid re-entrancy
            self.lineEdit().blockSignals(True)
            try:
                self.lineEdit().setText(elidedText)
            finally:
                self.lineEdit().blockSignals(False)
        finally:
            self._updatingText = False

    def addItem(self, text: str, data: Optional[Any] = None) -> None:
        """Add an item to the combo box.

        Args:
            text (str): The text to display.
            data (Optional[Any]): The associated data. Default is None.
        """
        # Enforce duplicates policy: when disabled, prevent adding an item
        # that duplicates by text OR by data (strictest interpretation).
        if not self.isDuplicatesEnabled():
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                existing = self.model().item(i)
                existing_default = existing.data()
                existing_user = existing.data(int(Qt.ItemDataRole.UserRole))
                if existing.text() == text or existing_default == (data or text) or existing_user == (data or text):
                    return

        item = QStandardItem()
        item.setText(text)
        # Store provided data in both the default role and UserRole to maintain
        # backward compatibility with item.data() and to align with Qt idioms.
        item.setData(data or text)  # default role (matches previous behavior)
        item.setData(data or text, int(Qt.ItemDataRole.UserRole))
        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        )
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)
        self._syncSelectAllState()

    def addItems(self, texts: List[str], dataList: Optional[List[Optional[Any]]] = None) -> None:
        """Add multiple items to the combo box.

        Args:
            texts (List[str]): A list of texts to display.
            dataList (Optional[List[Optional[Any]]]): A list of associated data. Default is None.
        """
        dataList = dataList or [None] * len(texts)
        for text, data in zip(texts, dataList):
            self.addItem(text, data)
        self._syncSelectAllState()

    def currentData(self) -> List[Any]:
        """Get the currently selected data.

        Returns:
            List[Any]: A list of currently selected data (read using getOutputDataRole()).
        """
        output_type = self.getOutputType()
        rows = sorted(r for r in self._checkedRows if self._isOptionRow(r))
        return [self.typeSelection(i, output_type) for i in rows]

    def setCurrentIndexes(self, indexes: List[int]) -> None:
        """Set the selected items based on the provided indexes.

        Args:
            indexes (List[int]): A list of indexes to select.
        """
        self._beginBulkUpdate()
        try:
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                self.model().item(i).setData(
                    Qt.CheckState.Checked if i in indexes else Qt.CheckState.Unchecked,
                    Qt.ItemDataRole.CheckStateRole,
                )
        finally:
            self._endBulkUpdate()

    def getCurrentIndexes(self) -> List[int]:
        """Get the indexes of the currently selected items.

        Returns:
            List[int]: A list of indexes of selected items.
        """
        return sorted(r for r in self._checkedRows if self._isOptionRow(r))

    def setPlaceholderText(self, text: str) -> None:
        """Set the placeholder text for the combo box.

        Args:
            text (str): The placeholder text.
        """
        self.placeholderText = text
        # Use native placeholder styling too
        self.lineEdit().setPlaceholderText(text)
        self.updateText()

    def showEvent(self, event) -> None:
        """Show event handler.

        Args:
            event: The show event.
        """
        super().showEvent(event)
        self._scheduleCoalescedUpdate()
        self._syncSelectAllState()
    
    def setCloseOnSelect(self, enabled: bool) -> None:
        """Set whether the popup should close after selecting/toggling an item.

        Args:
            enabled (bool): If True, the popup closes upon selection.
        """
        self._closeOnSelect = bool(enabled)

    def isCloseOnSelect(self) -> bool:
        """Return whether the popup closes after selecting/toggling an item."""
        return self._closeOnSelect

    def getCurrentOptions(self) -> List[Tuple[str, Any]]:
        """Get the currently selected options along with their associated data.

        Returns:
            List[Tuple[str, Any]]: A list of tuples (text, data) for the currently
                selected options. Data is read using getOutputDataRole().
        """
        res = []
        for i in range(self._firstOptionRow(), self.model().rowCount()):
            if self.model().item(i).data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked:
                res.append((self.model().item(i).text(), self.model().item(i).data(int(self._outputDataRole))))
        return res
    
    def getPlaceholderText(self) -> str:
        """Get the placeholder text currently set for the combo box.

        Returns:
            str: The placeholder text.
        """
        return self.placeholderText
    
    def setDuplicatesEnabled(self, enabled: bool) -> None:
        """Set whether duplicates are allowed in the combo box.

        Args:
            enabled (bool): Whether duplicates are allowed.
        """
        self.duplicatesEnabled = enabled

    def isDuplicatesEnabled(self) -> bool:
        """Check if duplicates are allowed in the combo box.

        Returns:
            bool: True if duplicates are allowed, False otherwise.
        """
        return self.duplicatesEnabled

    # --- QComboBox API parity additions ---
    def currentText(self) -> str:  # type: ignore[override]
        """Get the joined display text of all selected items.

        Returns:
            str: The full, non-elided text shown in the line edit, joined with the
                current display delimiter. If no items are selected, returns the
                placeholder text (if set) or an empty string.
        """
        display_type = self.getDisplayType()
        delimiter = self.getDisplayDelimiter()
        rows = sorted(r for r in self._checkedRows if self._isOptionRow(r))
        parts = [self.typeSelection(i, display_type) for i in rows]
        if parts:
            return delimiter.join(str(p) for p in parts)
        return self.placeholderText if hasattr(self, 'placeholderText') else ""

    def setCurrentText(self, value: Iterable[str] | str) -> None:  # type: ignore[override]
        """Select items matching the provided value.

        Args:
            value (Iterable[str] | str): Either a string joined by the current
                display delimiter or an iterable of strings. Each entry is matched
                against item text; if not found, it is compared to item data
                stored at Qt.UserRole.

        Returns:
            None
        """
        if isinstance(value, str):
            # Split using display delimiter as a heuristic
            parts = [p.strip() for p in value.split(self.getDisplayDelimiter()) if p.strip()]
        else:
            try:
                parts = [str(v) for v in value]
            except Exception:
                parts = []

        to_select = set(parts)
        self._beginBulkUpdate()
        try:
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                item = self.model().item(i)
                match = item.text() in to_select or str(item.data(int(Qt.ItemDataRole.UserRole))) in to_select
                item.setData(
                    Qt.CheckState.Checked if match else Qt.CheckState.Unchecked,
                    Qt.ItemDataRole.CheckStateRole,
                )
        finally:
            self._endBulkUpdate()

    def findText(self, text: str, flags: Qt.MatchFlag = Qt.MatchFlag.MatchExactly) -> int:  # type: ignore[override]
        """Find the index of the first item whose text matches.

        Args:
            text (str): The text pattern to search for.
            flags (Qt.MatchFlag): Match options (e.g., MatchExactly, MatchContains,
                MatchCaseSensitive). Defaults to MatchExactly.

        Returns:
            int: The index of the first matching item, or -1 if not found. If the
                optional "Select All" item is enabled, indices include that row.
        """
        for i in range(self._firstOptionRow(), self.model().rowCount()):
            item_text = self.model().item(i).text()
            if self._matchText(item_text, text, flags):
                return i
        return -1

    def findData(self, data: Any, role: int = int(Qt.ItemDataRole.UserRole)) -> int:  # helper similar to QComboBox
        """Find the index of the first item whose data matches the given value.

        Args:
            data (Any): The data value to search for.
            role (int): Data role to use for comparison (defaults to Qt.UserRole).

        Returns:
            int: The index of the first matching item, or -1 if not found. If the
                optional "Select All" item is enabled, indices include that row.
        """
        for i in range(self._firstOptionRow(), self.model().rowCount()):
            if self.model().item(i).data(role) == data:
                return i
        return -1

    # --- Bulk selection helpers ---
    def selectAll(self) -> None:
        """Select all items.

        Returns:
            None
        """
        self._beginBulkUpdate()
        try:
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                self.model().item(i).setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
        finally:
            self._endBulkUpdate()

    def clearSelection(self) -> None:
        """Clear the selection of all items.

        Returns:
            None
        """
        self._beginBulkUpdate()
        try:
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                self.model().item(i).setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        finally:
            self._endBulkUpdate()

    def invertSelection(self) -> None:
        """Invert the selection state of all items.

        Returns:
            None
        """
        self._beginBulkUpdate()
        try:
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                item = self.model().item(i)
                state = item.data(Qt.ItemDataRole.CheckStateRole)
                item.setData(
                    Qt.CheckState.Unchecked if state == Qt.CheckState.Checked else Qt.CheckState.Checked,
                    Qt.ItemDataRole.CheckStateRole,
                )
        finally:
            self._endBulkUpdate()

    # --- Optional 'Select All' pseudo-item ---
    def setSelectAllEnabled(self, enabled: bool, text: str = "Select All") -> None:
        """Enable or disable the optional tri-state "Select All" item.

        Args:
            enabled (bool): Whether to enable the pseudo-item.
            text (str): The display text for the pseudo-item. Defaults to
                "Select All".

        Returns:
            None
        """
        self._selectAllEnabled = enabled
        self._selectAllText = text
        if enabled:
            if self.model().rowCount() == 0 or self.model().item(0) is None or self.model().item(0).data() != "__select_all__":
                sa = QStandardItem()
                sa.setText(self._selectAllText)
                sa.setData("__select_all__")
                sa.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
                sa.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
                self.model().insertRow(0, sa)
        else:
            # Remove select all if present
            if self.model().rowCount() > 0 and self.model().item(0) and self.model().item(0).data() == "__select_all__":
                self.model().removeRow(0)
        self._syncSelectAllState()
        self.updateText()

    def isSelectAllEnabled(self) -> bool:
        """Check if the optional "Select All" pseudo-item is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return self._selectAllEnabled

    # --- Internal helpers ---
    def _firstOptionRow(self) -> int:
        return 1 if self._selectAllEnabled and self.model().rowCount() > 0 and self.model().item(0) and self.model().item(0).data() == "__select_all__" else 0

    def _syncSelectAllState(self) -> None:
        if not self._selectAllEnabled:
            return
        if self.model().rowCount() == 0:
            return
        sa = self.model().item(0)
        if sa is None or sa.data() != "__select_all__":
            return
        total = self.model().rowCount() - self._firstOptionRow()
        if total <= 0:
            sa.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            return
        checked = len([r for r in self._checkedRows if self._isOptionRow(r)])
        if checked == 0:
            sa.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        elif checked == total:
            sa.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
        else:
            sa.setData(Qt.CheckState.PartiallyChecked, Qt.ItemDataRole.CheckStateRole)

    def _emitSelectionIfChanged(self) -> None:
        current = self.currentData()
        if current != self._lastSelectionSnapshot:
            self._lastSelectionSnapshot = list(current)
            self.selectionChanged.emit(list(current))

    def _onModelDataChanged(self, topLeft, bottomRight, roles=None) -> None:
        # Any change might affect display text/selection
        if self._inBulkUpdate:
            return
        # Update cache only for affected rows when check state changes; otherwise just refresh text
        roles = roles or []
        check_role_changed = (not roles) or (Qt.ItemDataRole.CheckStateRole in roles)
        if check_role_changed:
            for row in range(topLeft.row(), bottomRight.row() + 1):
                if not self._isOptionRow(row):
                    continue
                item = self.model().item(row)
                if item is None:
                    continue
                state = item.data(Qt.ItemDataRole.CheckStateRole)
                if state == Qt.CheckState.Checked:
                    self._checkedRows.add(row)
                else:
                    self._checkedRows.discard(row)
        # Coalesce expensive UI updates
        self._scheduleCoalescedUpdate()

    def _beginBulkUpdate(self) -> None:
        self._inBulkUpdate = True

    def _endBulkUpdate(self) -> None:
        self._inBulkUpdate = False
        self._rebuildCheckedCache()
        # For explicit bulk operations, perform the coalesced update immediately
        # to preserve synchronous behavior expected by tests and callers.
        self._performCoalescedUpdate()

    def _matchText(self, item_text: str, pattern: str, flags: Qt.MatchFlag) -> bool:
        # Implement a subset: MatchExactly, MatchContains, MatchFixedString, MatchCaseSensitive
        case_sensitive = bool(flags & Qt.MatchFlag.MatchCaseSensitive)
        if not case_sensitive:
            item_cmp = item_text.lower()
            patt_cmp = pattern.lower()
        else:
            item_cmp = item_text
            patt_cmp = pattern

        if flags & Qt.MatchFlag.MatchContains:
            return patt_cmp in item_cmp
        # Default to exact match
        return item_cmp == patt_cmp

    # --- Configurable output data role ---
    def setOutputDataRole(self, role: Qt.ItemDataRole) -> None:
        """Set the Qt data role used when reading item data for outputs.

        This affects methods like currentData(), getCurrentOptions(), and the
        'data' branch of typeSelection(). By default, the role is
        Qt.ItemDataRole.UserRole.

        Note:
            This does not change how data is written by addItem/addItems, which
            store provided data in Qt.UserRole. If you want to use a different
            role for outputs, ensure your items have data stored at that role.
        """
        self._outputDataRole = role

    def getOutputDataRole(self) -> Qt.ItemDataRole:
        """Get the Qt data role used when reading item data for outputs."""
        return self._outputDataRole

    # --- Performance helpers ---
    def _isOptionRow(self, row: int) -> bool:
        return row >= self._firstOptionRow()

    def _rebuildCheckedCache(self) -> None:
        self._checkedRows.clear()
        start = self._firstOptionRow()
        for i in range(start, self.model().rowCount()):
            item = self.model().item(i)
            if item is not None and item.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked:
                self._checkedRows.add(i)

    def _onRowsInserted(self, parent, start: int, end: int) -> None:
        # Rebuild cache as rows shift; then schedule update
        if self._inBulkUpdate:
            return
        self._rebuildCheckedCache()
        self._scheduleCoalescedUpdate()

    def _onRowsRemoved(self, parent, start: int, end: int) -> None:
        # Rebuild cache as rows shift; then schedule update
        if self._inBulkUpdate:
            return
        self._rebuildCheckedCache()
        self._scheduleCoalescedUpdate()

    def _onModelReset(self) -> None:
        # Model structure changed drastically
        if self._inBulkUpdate:
            return
        self._rebuildCheckedCache()
        self._scheduleCoalescedUpdate()

    def _scheduleCoalescedUpdate(self) -> None:
        if self._updateScheduled:
            return
        self._updateScheduled = True
        QTimer.singleShot(0, self._performCoalescedUpdate)

    def _performCoalescedUpdate(self) -> None:
        self._updateScheduled = False
        self.updateText()
        self._syncSelectAllState()
        self._emitSelectionIfChanged()

    # --- Public API for coalescing updates ---
    def beginUpdate(self) -> None:
        """Public API to begin a batch update, deferring UI refresh."""
        self._beginBulkUpdate()

    def endUpdate(self) -> None:
        """Public API to end a batch update and refresh once."""
        self._endBulkUpdate()
