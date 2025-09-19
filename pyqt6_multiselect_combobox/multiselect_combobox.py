from PyQt6.QtWidgets import QComboBox, QStyledItemDelegate
from PyQt6.QtGui import QStandardItem, QPalette, QFontMetrics
from PyQt6.QtCore import Qt, QEvent, pyqtSignal


class MultiSelectComboBox(QComboBox):
    """
    A custom combo box widget that allows for multi-select functionality.

    This widget provides the ability to select multiple items from a dropdown list and display them in a comma-separated format in the combo box's line edit area.
    """

    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):  # pragma: no cover (cosmetic GUI sizing)
            size = super().sizeHint(option, index)
            size.setHeight(20)
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

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        palette = self.lineEdit().palette()
        palette.setBrush(
            QPalette.ColorRole.Base, palette.brush(QPalette.ColorRole.Button)
        )
        self.lineEdit().setPalette(palette)

        self.setItemDelegate(MultiSelectComboBox.Delegate())
        self.setOutputType("data")
        self.setDisplayType("data")
        self.setDisplayDelimiter(",")

        self.model().dataChanged.connect(self._onModelDataChanged)
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False
        self.view().viewport().installEventFilter(self)

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

    def eventFilter(self, obj, event) -> bool:
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
        if obj == self.view().viewport() and event.type() == QEvent.Type.MouseButtonRelease:
            index = self.view().indexAt(event.position().toPoint())
            if not index.isValid():
                return False
            row = index.row()
            if self._selectAllEnabled and row == 0:
                # Toggle tri-state 'Select All'
                sa_item = self.model().item(0)
                if sa_item.checkState() in (Qt.CheckState.Unchecked, Qt.CheckState.PartiallyChecked):
                    self.selectAll()
                else:
                    self.clearSelection()
                return True
            else:
                item = self.model().itemFromIndex(index)
                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                # Update Select All state and emit selection change
                self._syncSelectAllState()
                self._emitSelectionIfChanged()
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

    def timerEvent(self, event) -> None:
        """Timer event handler.

        Args:
            event: The timer event.
        """
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def typeSelection(self, index: int, type_variable: str, expected_type: str = "data") -> str:
        """Get the selected item's data or text based on type.

        Args:
            index (int): The index of the item.
            type_variable (str): The type variable to retrieve ('data' or 'text').
            expected_type (str): The expected type. Default is 'data'.

        Returns:
            str: The selected item's data or text.
        """
        if type_variable == expected_type:
            return self.model().item(index).data()
        return self.model().item(index).text()

    def updateText(self) -> None:
        """Update the displayed text based on selected items.
        """
        display_type = self.getDisplayType()
        delimiter = self.getDisplayDelimiter()
        texts = [
            self.typeSelection(i, display_type)
            for i in range(self._firstOptionRow(), self.model().rowCount())
            if self.model().item(i).checkState() == Qt.CheckState.Checked
        ]
        
        if texts:
            text = delimiter.join(texts)
        else:
            text = self.placeholderText if hasattr(self, 'placeholderText') else ""
        
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(
            text, Qt.TextElideMode.ElideRight, self.lineEdit().width()
        )
        self.lineEdit().setText(elidedText)

    def addItem(self, text: str, data: str = None) -> None:
        """Add an item to the combo box.

        Args:
            text (str): The text to display.
            data (str): The associated data. Default is None.
        """
        # Enforce duplicates policy: when disabled, prevent adding an item
        # that duplicates by text OR by data (strictest interpretation).
        if not self.isDuplicatesEnabled():
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                existing = self.model().item(i)
                if existing.text() == text or existing.data() == (data or text):
                    return

        item = QStandardItem()
        item.setText(text)
        item.setData(data or text)
        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable
        )
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)
        self._syncSelectAllState()

    def addItems(self, texts: list, dataList: list = None) -> None:
        """Add multiple items to the combo box.

        Args:
            texts (list): A list of texts to display.
            dataList (list): A list of associated data. Default is None.
        """
        dataList = dataList or [None] * len(texts)
        for text, data in zip(texts, dataList):
            self.addItem(text, data)
        self._syncSelectAllState()

    def currentData(self) -> list:
        """Get the currently selected data.

        Returns:
            list: A list of currently selected data.
        """
        output_type = self.getOutputType()
        return [
            self.typeSelection(i, output_type)
            for i in range(self._firstOptionRow(), self.model().rowCount())
            if self.model().item(i).checkState() == Qt.CheckState.Checked
        ]

    def setCurrentIndexes(self, indexes: list) -> None:
        """Set the selected items based on the provided indexes.

        Args:
            indexes (list): A list of indexes to select.
        """
        self._beginBulkUpdate()
        try:
            for i in range(self._firstOptionRow(), self.model().rowCount()):
                self.model().item(i).setCheckState(
                    Qt.CheckState.Checked if i in indexes else Qt.CheckState.Unchecked
                )
        finally:
            self._endBulkUpdate()

    def getCurrentIndexes(self) -> list:
        """Get the indexes of the currently selected items.

        Returns:
            list: A list of indexes of selected items.
        """
        return [
            i
            for i in range(self._firstOptionRow(), self.model().rowCount())
            if self.model().item(i).checkState() == Qt.CheckState.Checked
        ]

    def setPlaceholderText(self, text: str) -> None:
        """Set the placeholder text for the combo box.

        Args:
            text (str): The placeholder text.
        """
        self.placeholderText = text
        self.updateText()

    def showEvent(self, event) -> None:
        """Show event handler.

        Args:
            event: The show event.
        """
        super().showEvent(event)
        self.updateText()
        self._syncSelectAllState()
    
    def getCurrentOptions(self):
        """Get the currently selected options along with their associated data.

        Returns:
            list: A list of tuples containing the text and data of the currently selected options.
                Each tuple consists of (text, data).
        """
        res = []
        for i in range(self._firstOptionRow(), self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                res.append((self.model().item(i).text(), self.model().item(i).data()))
        return res
    
    def getPlaceholderText(self):
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
        parts = [
            self.typeSelection(i, display_type)
            for i in range(self._firstOptionRow(), self.model().rowCount())
            if self.model().item(i).checkState() == Qt.CheckState.Checked
        ]
        if parts:
            return delimiter.join(parts)
        return self.placeholderText if hasattr(self, 'placeholderText') else ""

    def setCurrentText(self, value) -> None:  # type: ignore[override]
        """Select items matching the provided value.

        Args:
            value: Either a string joined by the current display delimiter or an
                iterable of strings. Each entry is matched against item text;
                if not found, it is compared to item data.

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
                match = item.text() in to_select or str(item.data()) in to_select
                item.setCheckState(Qt.CheckState.Checked if match else Qt.CheckState.Unchecked)
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

    def findData(self, data, role: int = int(Qt.ItemDataRole.UserRole)) -> int:  # helper similar to QComboBox
        """Find the index of the first item whose data matches the given value.

        Args:
            data: The data value to search for.
            role (int): Data role (kept for API parity; currently not used and
                defaults to Qt.UserRole). Included for compatibility.

        Returns:
            int: The index of the first matching item, or -1 if not found. If the
                optional "Select All" item is enabled, indices include that row.
        """
        for i in range(self._firstOptionRow(), self.model().rowCount()):
            if self.model().item(i).data() == data:
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
                self.model().item(i).setCheckState(Qt.CheckState.Checked)
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
                self.model().item(i).setCheckState(Qt.CheckState.Unchecked)
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
                item.setCheckState(
                    Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
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
                sa.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
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
            sa.setCheckState(Qt.CheckState.Unchecked)
            return
        checked = sum(1 for i in range(self._firstOptionRow(), self.model().rowCount()) if self.model().item(i).checkState() == Qt.CheckState.Checked)
        if checked == 0:
            sa.setCheckState(Qt.CheckState.Unchecked)
        elif checked == total:
            sa.setCheckState(Qt.CheckState.Checked)
        else:
            sa.setCheckState(Qt.CheckState.PartiallyChecked)

    def _emitSelectionIfChanged(self) -> None:
        current = self.currentData()
        if current != self._lastSelectionSnapshot:
            self._lastSelectionSnapshot = list(current)
            self.selectionChanged.emit(list(current))

    def _onModelDataChanged(self, topLeft, bottomRight, roles=None) -> None:
        # Any change might affect display text/selection
        if self._inBulkUpdate:
            return
        self.updateText()
        self._syncSelectAllState()
        self._emitSelectionIfChanged()

    def _beginBulkUpdate(self) -> None:
        self._inBulkUpdate = True

    def _endBulkUpdate(self) -> None:
        self._inBulkUpdate = False
        self._syncSelectAllState()
        self.updateText()
        self._emitSelectionIfChanged()

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
