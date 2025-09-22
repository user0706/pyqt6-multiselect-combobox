from typing import Any, Iterable, List, Optional, Tuple

from PyQt6.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QToolTip
from PyQt6.QtGui import QStandardItem, QPalette, QFontMetrics, QCursor
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
        # Maximum number of selectable items; None means unlimited
        self._maxSelectionCount: Optional[int] = None
        # Debounce guard to avoid spamming tooltip
        self._lastLimitNotifyMs: int = 0
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
        # Keep the editor editable so the native clear button can function,
        # but we'll block typing via eventFilter to avoid user text edits.
        self.lineEdit().setReadOnly(False)
        # Surface a clear affordance on the read-only line edit; clicking the
        # native clear button should clear the selection, not only the text.
        try:
            self.lineEdit().setClearButtonEnabled(True)
        except Exception:
            # Fallback for environments/styles that might not support it
            pass

        palette = self.lineEdit().palette()
        palette.setBrush(
            QPalette.ColorRole.Base, palette.brush(QPalette.ColorRole.Button)
        )
        self.lineEdit().setPalette(palette)

        self.setItemDelegate(MultiSelectComboBox.Delegate())
        self.setOutputType("data")
        self.setDisplayType("text")
        self.setDisplayDelimiter(",")

        # Optional summarization feature (disabled by default)
        # When a threshold is set (int >= 0), the display can be summarized
        # using either a count ("{count} selected") or a leading list with
        # a "+{more} more" suffix. None disables summarization.
        self._summaryThreshold: Optional[int] = None
        self._summaryMode: str = "leading"  # "leading" or "count"
        # Default formats; apply only when mode requires them
        self._summaryCountFormat: str = "{count} selected"
        self._summaryLeadingFormat: str = "{shown} … +{more} more"

        # When True, keep the widget tooltip in sync with the full (non-elided)
        # selection text so users can hover to view the entire selection.
        self._elideToolTipEnabled: bool = True

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

        # Optional filter UI inside the popup
        self._filterEnabled: bool = False
        self._filterEdit: Optional[QLineEdit] = None
        self._filterTopMargin: int = 0

        # Initialize caches
        self._rebuildCheckedCache()

        # Set initial accessible names for screen readers
        self._updateAccessibilityLabels()

        # If the user clicks the clear button, QLineEdit clears its text.
        # Detect that user action via textChanged when not in a programmatic
        # update and clear the selection once.
        try:
            self.lineEdit().textChanged.connect(self._onLineEditTextChanged)
        except Exception:
            pass

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

    def setElideToolTipEnabled(self, enabled: bool) -> None:
        """Enable or disable tooltip synchronization with the full selection text.

        When enabled, the widget's tooltip is updated to the full, non-elided
        joined text built by updateText()/currentText(). This allows users to
        hover and see the entire selection when the line edit display is elided.
        """
        self._elideToolTipEnabled = bool(enabled)
        # Refresh immediately so current tooltip reflects the new preference
        self.updateText()

    def isElideToolTipEnabled(self) -> bool:
        """Return whether tooltip synchronization for elided text is enabled."""
        return self._elideToolTipEnabled

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
        # Reapply filter if enabled to the new model
        self._reapplyFilterIfNeeded()

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
        # Block keyboard edits in the line edit while allowing the clear button
        # to function (the clear button triggers a textChanged("") we handle).
        if obj == self.lineEdit() and event.type() == QEvent.Type.KeyPress:
            # Eat key presses to prevent manual typing into the line edit
            return True
        # Keep filter UI positioned on view resize/move
        if self._filterEnabled and obj in (self.view(), self.view().viewport()):
            if event.type() in (QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.Move):
                self._positionFilterUi()
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
                        # Respect disabled rows: do not toggle via keyboard
                        try:
                            if not bool(item.flags() & Qt.ItemFlag.ItemIsEnabled):
                                return True
                        except Exception:
                            pass
                        state = item.data(Qt.ItemDataRole.CheckStateRole)
                        new_state = Qt.CheckState.Unchecked if state == Qt.CheckState.Checked else Qt.CheckState.Checked
                        if new_state == Qt.CheckState.Checked and not self._canSelectMore(1):
                            self._notifyLimitReached()
                        else:
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
                # Respect disabled rows: do not toggle via mouse
                try:
                    if not bool(item.flags() & Qt.ItemFlag.ItemIsEnabled):
                        return True
                except Exception:
                    pass
                state = item.data(Qt.ItemDataRole.CheckStateRole)
                new_state = Qt.CheckState.Unchecked if state == Qt.CheckState.Checked else Qt.CheckState.Checked
                if new_state == Qt.CheckState.Checked and not self._canSelectMore(1):
                    self._notifyLimitReached()
                else:
                    item.setData(new_state, Qt.ItemDataRole.CheckStateRole)
                # Update Select All state and emit selection change
                self._syncSelectAllState()
                self._emitSelectionIfChanged()
                if self._closeOnSelect:
                    self.hidePopup()
                    self._forceHidePopupView()
                return True
        return False

    # --- In-popup filter support ---
    def setFilterEnabled(self, enabled: bool) -> None:
        """Enable or disable a search/filter field inside the popup.

        When enabled, a small QLineEdit is shown above the list and filters
        visible rows on-the-fly by item text (case-insensitive contains).
        """
        self._filterEnabled = bool(enabled)
        if not enabled:
            # Tear down UI and clear hiding if disabling
            self._teardownFilterUi()
            self._clearRowHiding()
        else:
            # Lazily create on next popup show
            pass

    def isFilterEnabled(self) -> bool:
        """Return whether the in-popup filter is enabled."""
        return self._filterEnabled

    def _ensureFilterUi(self) -> None:
        if self._filterEdit is not None:
            return
        try:
            v = self.view()
        except Exception:
            return
        self._filterEdit = QLineEdit(v)
        self._filterEdit.setPlaceholderText("Filter...")
        self._filterEdit.textChanged.connect(self._applyTextFilter)
        # Compute a comfortable height based on font metrics
        fm = QFontMetrics(self._filterEdit.font())
        h = fm.height() + 10
        self._filterTopMargin = h + 2
        try:
            v.setViewportMargins(0, self._filterTopMargin, 0, 0)
        except Exception:
            pass
        # Ensure clicks in the filter do not propagate to the list view
        self._filterEdit.installEventFilter(self)

    def _positionFilterUi(self) -> None:  # pragma: no cover (cosmetic UI positioning)
        if not self._filterEnabled or self._filterEdit is None:
            return
        v = self.view()
        # Keep viewport top margin in sync (some styles reset margins)
        try:
            v.setViewportMargins(0, self._filterTopMargin, 0, 0)
        except Exception:
            pass
        # Place the edit at the very top inside the view
        w = v.viewport().width() if v.viewport() is not None else v.width()
        self._filterEdit.setGeometry(1, 1, max(0, w - 2), self._filterTopMargin - 2)

    def _teardownFilterUi(self) -> None:  # pragma: no cover (cosmetic UI teardown)
        if self._filterEdit is None:
            # Also clear viewport margins
            try:
                self.view().setViewportMargins(0, 0, 0, 0)
            except Exception:
                pass
            return
        try:
            self.view().setViewportMargins(0, 0, 0, 0)
        except Exception:
            pass
        try:
            self._filterEdit.deleteLater()
        except Exception:
            pass
        self._filterEdit = None
        self._filterTopMargin = 0

    def _applyTextFilter(self, pattern: str) -> None:
        # Hide rows that do not match the filter; keep Select All (if present) visible
        patt = (pattern or "").strip()
        casefold = patt.casefold()
        m = self.model()
        first = self._firstOptionRow()
        for row in range(0, m.rowCount()):
            if row < first:
                # Always show pseudo-rows above options (e.g., Select All)
                self.view().setRowHidden(row, False)
                continue
            item = m.item(row)
            if not patt:
                self.view().setRowHidden(row, False)
            else:
                text = item.text() if item is not None else ""
                self.view().setRowHidden(row, casefold not in text.casefold())

    def _clearRowHiding(self) -> None:
        try:
            m = self.model()
            for row in range(0, m.rowCount()):
                self.view().setRowHidden(row, False)
        except Exception:
            pass

    def showPopup(self) -> None:
        """Show the combo box popup.
        """
        # Ensure filter UI is prepared before showing
        if self._filterEnabled:
            self._ensureFilterUi()
            self._positionFilterUi()
        super().showPopup()
        # In case the view/viewport were force-hidden during a previous close,
        # explicitly re-show them to avoid a perceived lag or invisible popup.
        try:
            v = self.view()
            v.show()
            if v.viewport() is not None:
                v.viewport().show()
        except Exception:
            pass
        self.closeOnLineEditClick = True

    def hidePopup(self) -> None:
        """Hide the combo box popup.
        """
        super().hidePopup()
        self.startTimer(100)

    def _forceHidePopupView(self) -> None:  # pragma: no cover (cosmetic force hide)
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

            # Apply optional summarization for display text
            text = self._buildDisplayText(texts, delimiter)

            # Also set native placeholder for better styling when empty
            if not texts:
                self.lineEdit().setPlaceholderText(self.placeholderText)

            # Keep tooltip synchronized with the full (non-elided) text so users
            # can hover to see the entire selection when the display is elided.
            # Mirror currentText(): include placeholder when no selections.
            if getattr(self, "_elideToolTipEnabled", False):
                self.setToolTip(text)

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
            # Keep accessibility labels in sync with the UI text/selection
            self._updateAccessibilityLabels()
        finally:
            self._updatingText = False

    def addItem(self, text: str, data: Optional[Any] = None, *, enabled: bool = True) -> None:
        """Add an item to the combo box.

        Args:
            text (str): The text to display.
            data (Optional[Any]): The associated data. Default is None.
            enabled (bool): Whether the item should be enabled (selectable via user
                interaction). Disabled items remain visible but cannot be toggled by
                the user. Programmatic changes are still possible. Default True.
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
        # Build flags respecting the requested enabled state, always ensuring
        # user-checkable/selectable so they appear and can be controlled when enabled
        flags = Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        if enabled:
            flags |= Qt.ItemFlag.ItemIsEnabled
        item.setFlags(flags)
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
        # Rebuild cache to reflect any external model changes that may not have
        # gone through our normal update paths yet
        self._rebuildCheckedCache()
        # Enforce max selection proactively if exceeded
        if self._hasMaxLimit():
            selected_count = len([r for r in self._checkedRows if self._isOptionRow(r)])
            if selected_count > int(self._maxSelectionCount or 0):
                self._enforceMaxSelection()
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
            allowed = set(indexes)
            # Enforce "options only" range
            allowed = {i for i in allowed if self._isOptionRow(i)}
            # Apply limit if present
            if self._hasMaxLimit() and len(allowed) > self._maxSelectionCount:  # type: ignore[operator]
                allowed = set(sorted(allowed)[: int(self._maxSelectionCount or 0)])
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                self.model().item(i).setData(
                    Qt.CheckState.Checked if i in allowed else Qt.CheckState.Unchecked,
                    Qt.ItemDataRole.CheckStateRole,
                )
            if self._hasMaxLimit() and len(allowed) < len(indexes):
                self._notifyLimitReached()
        finally:
            self._endBulkUpdate()

    def getCurrentIndexes(self) -> List[int]:
        """Get the indexes of the currently selected items.

        Returns:
            List[int]: A list of indexes of selected items.
        """
        # Keep cache in sync in case of external modifications
        self._rebuildCheckedCache()
        # Enforce max selection if needed before reporting
        if self._hasMaxLimit():
            selected_rows = sorted(r for r in self._checkedRows if self._isOptionRow(r))
            if len(selected_rows) > int(self._maxSelectionCount or 0):
                self._enforceMaxSelection()
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
        return self._buildDisplayText(parts, delimiter)

    # --- Optional summarization API ---
    def setSummaryThreshold(self, threshold: Optional[int]) -> None:
        """Set the number of items to show before summarizing.

        - None disables summarization (default behavior).
        - 0 means always summarize (even one selection).
        - N>0 shows up to N items, beyond that summarizes.
        """
        if threshold is None:
            self._summaryThreshold = None
        else:
            if threshold < 0:
                raise ValueError("Summary threshold must be >= 0 or None")
            self._summaryThreshold = int(threshold)
        self.updateText()

    def getSummaryThreshold(self) -> Optional[int]:
        """Return the current summarization threshold or None if disabled."""
        return self._summaryThreshold

    def setSummaryMode(self, mode: str) -> None:
        """Set summarization mode: 'count' or 'leading'.

        - 'count': shows text based on _summaryCountFormat (e.g., "{count} selected").
        - 'leading': shows first N items then _summaryLeadingFormat (e.g., "A, B … +2 more").
        """
        if mode not in ("count", "leading"):
            raise ValueError("Summary mode must be 'count' or 'leading'")
        self._summaryMode = mode
        self.updateText()

    def getSummaryMode(self) -> str:
        """Return current summarization mode."""
        return self._summaryMode

    def setSummaryFormat(self, *, count: Optional[str] = None, leading: Optional[str] = None) -> None:
        """Customize summary text formats.

        Args:
            count: Format for count mode. Available fields: {count}.
            leading: Format for leading mode. Available fields: {shown}, {more}.
        """
        if count is not None:
            # sanity check
            if "{count}" not in count:
                raise ValueError("count format must include '{count}' placeholder")
            self._summaryCountFormat = count
        if leading is not None:
            if "{shown}" not in leading or "{more}" not in leading:
                raise ValueError("leading format must include '{shown}' and '{more}' placeholders")
            self._summaryLeadingFormat = leading
        self.updateText()

    def getSummaryFormat(self) -> Tuple[str, str]:
        """Return (count_format, leading_format)."""
        return self._summaryCountFormat, self._summaryLeadingFormat

    def _buildDisplayText(self, parts: List[Any], delimiter: str) -> str:
        """Build the display text from selected parts with optional summarization."""
        # No selection: return placeholder
        if not parts:
            return self.placeholderText if hasattr(self, 'placeholderText') else ""

        # If summarization is disabled, return full joined text
        if self._summaryThreshold is None:
            return delimiter.join(str(p) for p in parts)

        # Summarization enabled
        count = len(parts)
        threshold = int(self._summaryThreshold)

        if self._summaryMode == "count":
            # Always summarize when threshold is not None and count >= threshold
            # If threshold>0 and count < threshold, show full list
            if threshold > 0 and count < threshold:
                return delimiter.join(str(p) for p in parts)
            return self._summaryCountFormat.format(count=count)

        # leading mode
        if threshold == 0:
            shown_list: List[str] = []
        else:
            shown_list = [str(p) for p in parts[:threshold]]
        more = max(0, count - threshold)
        if more <= 0:
            return delimiter.join(shown_list)
        shown = delimiter.join(shown_list)
        return self._summaryLeadingFormat.format(shown=shown, more=more)

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
                if match:
                    if self._canSelectMore(1):
                        item.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
                    else:
                        self._notifyLimitReached()
                        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
                else:
                    item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
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
            remaining = self._remainingSelectable()
            if remaining == 0 and self._hasMaxLimit():
                self._notifyLimitReached()
                return
            count_selected = 0
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                item = self.model().item(i)
                if item.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked:
                    continue
                if self._hasMaxLimit() and count_selected >= remaining:
                    break
                item.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
                count_selected += 1
            # If we couldn't select all due to limit, surface feedback
            if self._hasMaxLimit() and (len([r for r in self._checkedRows if self._isOptionRow(r)]) >= self._maxSelectionCount):
                self._notifyLimitReached()
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

    # Public clear() slot for better API discoverability and to integrate with
    # the line edit clear button UX. This clears the selection and lets the
    # coalesced update emit selectionChanged once.
    def clear(self) -> None:  # type: ignore[override]
        """Clear the current selection and update the display once."""
        self.clearSelection()

    def invertSelection(self) -> None:
        """Invert the selection state of all items.

        Returns:
            None
        """
        self._beginBulkUpdate()
        try:
            remaining = self._remainingSelectable()
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                item = self.model().item(i)
                state = item.data(Qt.ItemDataRole.CheckStateRole)
                if state == Qt.CheckState.Checked:
                    item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
                else:
                    if self._canSelectMore(1):
                        item.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
                        remaining = self._remainingSelectable()
                    else:
                        # Skip toggling to checked due to limit
                        pass
            if self._hasMaxLimit() and self._remainingSelectable() == 0:
                self._notifyLimitReached()
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
        # After updates, enforce max selection if external changes exceeded it
        if self._hasMaxLimit():
            self._enforceMaxSelection()
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
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                self._checkedRows.add(i)

    def _onRowsInserted(self, parent, start: int, end: int) -> None:
        # Rebuild cache as rows shift; then schedule update
        if self._inBulkUpdate:
            return
        self._rebuildCheckedCache()
        self._scheduleCoalescedUpdate()
        self._reapplyFilterIfNeeded()

    def _onRowsRemoved(self, parent, start: int, end: int) -> None:
        # Rebuild cache as rows shift; then schedule update
        if self._inBulkUpdate:
            return
        self._rebuildCheckedCache()
        self._scheduleCoalescedUpdate()
        self._reapplyFilterIfNeeded()

    def _onModelReset(self) -> None:
        # Model structure changed drastically
        if self._inBulkUpdate:
            return
        self._rebuildCheckedCache()
        self._scheduleCoalescedUpdate()
        self._reapplyFilterIfNeeded()

    def _scheduleCoalescedUpdate(self) -> None:
        if self._updateScheduled:
            return
        self._updateScheduled = True
        QTimer.singleShot(0, self._performCoalescedUpdate)

    def _reapplyFilterIfNeeded(self) -> None:
        # Reapply filtering after model changes
        try:
            if self._filterEnabled and self._filterEdit is not None:
                self._applyTextFilter(self._filterEdit.text())
        except Exception:
            pass

    def _performCoalescedUpdate(self) -> None:
        self._updateScheduled = False
        self.updateText()
        self._syncSelectAllState()
        self._emitSelectionIfChanged()
        # Ensure accessible names reflect the latest selection state
        self._updateAccessibilityLabels()
        # Update ARIA-like hints in tooltips/status tips for all rows
        self._updateAriaLikeHints()

    # --- Max selection feature ---
    def setMaxSelectionCount(self, max_count: Optional[int]) -> None:
        """Set the maximum number of items that can be selected.

        Pass None, 0 or a negative value to disable the limit.
        """
        if max_count is None or (isinstance(max_count, int) and max_count <= 0):
            self._maxSelectionCount = None
        else:
            self._maxSelectionCount = int(max_count)
        # Enforce immediately in case current selection exceeds new limit
        if self._hasMaxLimit():
            self._enforceMaxSelection()
        self._performCoalescedUpdate()

    def maxSelectionCount(self) -> Optional[int]:
        """Return the current maximum selection count, or None if unlimited."""
        return self._maxSelectionCount

    def _hasMaxLimit(self) -> bool:
        return isinstance(self._maxSelectionCount, int) and self._maxSelectionCount is not None

    def _remainingSelectable(self) -> int:
        if not self._hasMaxLimit():
            return 10**9  # effectively unlimited
        current = len([r for r in self._checkedRows if self._isOptionRow(r)])
        return max(0, int(self._maxSelectionCount or 0) - current)

    def _canSelectMore(self, n: int) -> bool:
        if not self._hasMaxLimit():
            return True
        return self._remainingSelectable() >= n

    def _enforceMaxSelection(self) -> None:
        """If the current selection exceeds the limit, uncheck excess items deterministically.

        We keep the first N selected by row order and uncheck the rest.
        """
        if not self._hasMaxLimit():
            return
        allowed = int(self._maxSelectionCount or 0)
        selected_rows = sorted(r for r in self._checkedRows if self._isOptionRow(r))
        if len(selected_rows) <= allowed:
            return
        self._beginBulkUpdate()
        try:
            for r in selected_rows[allowed:]:
                item = self.model().item(r)
                if item is not None:
                    item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        finally:
            self._endBulkUpdate()
        self._notifyLimitReached()

    def _notifyLimitReached(self) -> None:  # pragma: no cover (tooltip only)
        """Show a brief tooltip/status message indicating the selection limit."""
        if not self._hasMaxLimit():
            return
        try:
            # Show tooltip near cursor or over the view
            msg = f"Maximum {self._maxSelectionCount} selections allowed."
            pos = QCursor.pos()
            QToolTip.showText(pos, msg, self.view())
        except Exception:
            pass

    # --- Internal handlers ---
    def _onLineEditTextChanged(self, text: str) -> None:
        """Handle user-initiated text clears from the line edit's clear button.

        The line edit is read-only and reflects selection. If the user clicks
        the clear button, QLineEdit clears its text and emits textChanged("").
        We treat that as intent to clear selection. Programmatic updates to the
        text are guarded by _updatingText and blockSignals, so we won't react
        to our own updates here.
        """
        if self._updatingText:
            return
        if text == "":
            # Clear once; clearSelection() will schedule a single emit.
            self.clear()

    def _updateAccessibilityLabels(self) -> None:
        """Update accessible names for the combo box and line edit.

        This helps screen readers announce a useful summary such as
        "3 items selected.". The widget role remains provided by Qt based
        on the widget type (QComboBox / QLineEdit).
        """
        try:
            count = len([r for r in self._checkedRows if self._isOptionRow(r)])
        except Exception:
            count = 0

        if count == 0:
            summary = "No items selected."
        elif count == 1:
            summary = "1 item selected."
        else:
            summary = f"{count} items selected."

        # Accessible names for the combo and its editor
        # Keep the names concise and informative for screen readers.
        self.setAccessibleName(f"Multi-select combo box. {summary}")
        if self.lineEdit() is not None:
            self.lineEdit().setAccessibleName(f"Selected items. {summary}")

    def _updateAriaLikeHints(self) -> None:  # pragma: no cover (cosmetic tooltips/status hints)
        """Update tooltips and status tips for items to provide ARIA-like hints.

        This augments accessibility by offering descriptive hints to all users,
        including sighted users, via native Qt tooltips/status bar messages.
        """
        try:
            m = self.model()
        except Exception:
            return
        if m is None:
            return

        # Determine select-all row info if present
        has_sa = self._selectAllEnabled and m.rowCount() > 0 and m.item(0) is not None and m.item(0).data() == "__select_all__"
        first_option = self._firstOptionRow()

        # Compute select-all state summary
        total_options = max(0, m.rowCount() - first_option)
        selected_count = len([r for r in self._checkedRows if self._isOptionRow(r)])

        # Helper for keyboard hint
        nav_hint = "Use Up/Down to navigate; press Space or Enter to toggle."

        # Update Select All pseudo-item hint
        if has_sa:
            sa = m.item(0)
            sa_state = sa.data(Qt.ItemDataRole.CheckStateRole)
            if selected_count == 0:
                summary = "None selected."
            elif selected_count == total_options and total_options > 0:
                summary = "All selected."
            else:
                summary = f"{selected_count} of {total_options} selected."
            if sa_state == Qt.CheckState.PartiallyChecked:
                state_text = "partially checked"
            elif sa_state == Qt.CheckState.Checked:
                state_text = "checked"
            else:
                state_text = "unchecked"
            sa_hint = (
                f"{self._selectAllText}: toggles selection of all items; currently {state_text}. "
                f"{summary} {nav_hint}"
            )
            try:
                sa.setToolTip(sa_hint)
                sa.setStatusTip(sa_hint)
            except Exception:
                pass

        # Update regular option items
        for row in range(first_option, m.rowCount()):
            item = m.item(row)
            if item is None:
                continue
            checked = item.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
            state_text = "selected" if checked else "not selected"
            text = item.text()
            if self._hasMaxLimit():
                limit_hint = f" Maximum {self._maxSelectionCount} selections."
            else:
                limit_hint = ""
            hint = f"Option '{text}' is {state_text}. {nav_hint}{limit_hint}"
            try:
                item.setToolTip(hint)
                item.setStatusTip(hint)
            except Exception:
                pass

    # --- Public API for coalescing updates ---
    def beginUpdate(self) -> None:
        """Public API to begin a batch update, deferring UI refresh."""
        self._beginBulkUpdate()

    def endUpdate(self) -> None:
        """Public API to end a batch update and refresh once."""
        self._endBulkUpdate()
