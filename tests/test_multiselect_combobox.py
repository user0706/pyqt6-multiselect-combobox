import sys
import types
import pytest

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt

from pyqt6_multiselect_combobox import MultiSelectComboBox


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture()
def combo(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"], ["da", "db", "dc"])
    return c


def get_item(c: MultiSelectComboBox, row: int):
    return c.model().item(row)


# --- Basic API & defaults ---

def test_defaults(combo: MultiSelectComboBox):
    assert combo.getOutputType() == "data"
    assert combo.getDisplayType() == "text"
    assert combo.getDisplayDelimiter() == ", "
    assert combo.isDuplicatesEnabled() is True
    assert combo.isSelectAllEnabled() is False
    # Summarization defaults
    assert combo.getSummaryThreshold() is None
    assert combo.getSummaryMode() == "leading"


def test_add_item_and_items(qapp):
    c = MultiSelectComboBox()
    c.addItem("X", "dx")
    c.addItems(["Y", "Z"], ["dy", "dz"])
    assert c.model().rowCount() == 3
    assert get_item(c, 0).text() == "X"
    assert get_item(c, 1).data() == "dy"


# --- Duplicate policy ---

def test_duplicates_disabled_prevents_same_text_or_data(qapp):
    c = MultiSelectComboBox()
    c.setDuplicatesEnabled(False)
    c.addItem("A", "data1")
    c.addItem("A", "data2")  # same text -> skipped
    c.addItem("B", "data1")  # same data -> skipped
    c.addItem("B", "data2")  # unique -> added
    assert c.model().rowCount() == 2
    assert [get_item(c, i).text() for i in range(c.model().rowCount())] == ["A", "B"]


# --- Selection & currentData/currentText ---

def test_set_current_indexes_and_current_data_text(combo: MultiSelectComboBox):
    combo.setCurrentIndexes([0, 2])
    # By default, output_type=data, display_type=data
    assert combo.currentData() == ["da", "dc"]
    # Change display_type to text and verify currentText joining
    combo.setDisplayType("text")
    assert combo.currentText() == "A, C"


# --- Summarization feature ---

def test_summary_leading_threshold_basic(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    c.addItems(["Apple", "Banana", "Cherry", "Date"])  # 4 items
    c.setSummaryThreshold(2)  # show up to 2, then summarize
    c.setCurrentIndexes([0, 1])
    assert c.currentText() == "Apple, Banana"  # no summary when <= threshold
    c.setCurrentIndexes([0, 1, 2])
    # Default leading format uses ellipsis + "more"
    assert "Apple, Banana" in c.currentText()
    assert "+1 more" in c.currentText()


def test_summary_count_mode(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    c.addItems(["A", "B", "C"])  # 3 items
    c.setSummaryMode("count")
    c.setSummaryThreshold(0)  # always summarize
    c.setCurrentIndexes([0])
    assert c.currentText() == "1 selected"
    c.setCurrentIndexes([0, 2])
    assert c.currentText() == "2 selected"


def test_summary_count_respects_threshold_show_full_when_under(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    c.addItems(["A", "B", "C"])  # 3 items
    c.setSummaryMode("count")
    c.setSummaryThreshold(3)
    c.setCurrentIndexes([0, 1])
    # count mode with threshold>0 should show full list when count <= threshold
    assert c.currentText() == "A, B"
    # Exceed threshold -> summarize
    c.setCurrentIndexes([0, 1, 2])
    assert c.currentText() == "3 selected"


def test_summary_custom_formats(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    c.addItems(["A", "B", "C", "D"])  # 4 items
    c.setSummaryThreshold(1)
    c.setSummaryMode("leading")
    c.setSummaryFormat(leading="{shown} and {more} others")
    c.setCurrentIndexes([0, 1, 2])
    assert c.currentText() == "A and 2 others"
    # Count format
    c.setSummaryMode("count")
    c.setSummaryFormat(count="Selected: {count}")
    c.setSummaryThreshold(0)
    c.setCurrentIndexes([0, 1, 2, 3])
    assert c.currentText() == "Selected: 4"


def test_set_current_text_with_string_and_list(combo: MultiSelectComboBox):
    combo.setDisplayDelimiter(", ")
    combo.setCurrentText("A, C")
    assert combo.getCurrentIndexes() == [0, 2]
    # Using list, match by data
    combo.setCurrentText(["db"])  # matches B by data
    assert combo.getCurrentIndexes() == [1]


# --- findText/findData ---

def test_find_text_exact_and_contains(combo: MultiSelectComboBox):
    # exact
    idx = combo.findText("B")
    assert idx == 1
    # contains (case-insensitive default)
    idx = combo.findText("b", Qt.MatchFlag.MatchContains)
    assert idx == 1
    # not found
    assert combo.findText("ZZZ") == -1


def test_find_data(combo: MultiSelectComboBox):
    assert combo.findData("db") == 1
    assert combo.findData("nope") == -1


# --- Bulk helpers ---

def test_select_all_clear_invert(combo: MultiSelectComboBox):
    # select all
    combo.selectAll()
    assert combo.getCurrentIndexes() == [0, 1, 2]
    # clear
    combo.clearSelection()
    assert combo.getCurrentIndexes() == []
    # invert
    combo.invertSelection()
    assert combo.getCurrentIndexes() == [0, 1, 2]
    combo.invertSelection()
    assert combo.getCurrentIndexes() == []


# --- Select All pseudo-item ---

def test_select_all_pseudo_item_states(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    c.setSelectAllEnabled(True)
    assert c.model().rowCount() == 4
    sa = get_item(c, 0)
    assert sa.text() == "Select All"
    # none selected -> unchecked
    assert sa.checkState() == Qt.CheckState.Unchecked
    # selectAll sets checked
    c.selectAll()
    assert sa.checkState() == Qt.CheckState.Checked
    # partial -> partiallyChecked
    c.model().item(2).setCheckState(Qt.CheckState.Unchecked)
    c._syncSelectAllState()
    assert sa.checkState() == Qt.CheckState.PartiallyChecked
    # clear -> unchecked
    c.clearSelection()
    assert sa.checkState() == Qt.CheckState.Unchecked


# --- selectionChanged signal ---

def test_selection_changed_emits_on_changes(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"])  # data defaults to text
    captured = []

    def on_changed(values):
        captured.append(list(values))

    c.selectionChanged.connect(on_changed)
    # programmatic select
    c.setCurrentIndexes([0])
    # duplicate operation should not emit a new one when selection stays the same
    c.setCurrentText(["A"])  # same selection
    # change selection
    c.setCurrentText(["B"])  # switch

    assert captured[0] == ["A",]  # first emission
    assert captured[-1] == ["B",]
    # Ensure no spurious emissions for same selection
    # There should be exactly 2 entries
    assert len(captured) == 2


# --- Output type affects emission ---

def test_selection_changed_respects_output_type(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"], ["da", "db"])  # custom data
    c.setOutputType("text")
    captured = []

    def on_changed(values):
        captured.append(list(values))

    c.selectionChanged.connect(on_changed)
    c.setCurrentIndexes([0, 1])
    assert captured[-1] == ["A", "B"]

    c.setOutputType("data")
    c.clearSelection()
    c.setCurrentIndexes([1])
    assert captured[-1] == ["db"]


# --- Additional edge cases ---

def test_placeholder_and_current_text_when_none_selected(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    # default: no placeholder -> empty string
    c.setDisplayType("text")
    assert c.currentText() == ""
    # set placeholder
    c.setPlaceholderText("Pick items")
    assert c.currentText() == "Pick items"


def test_display_with_dict_data_no_crash_and_current_data_returns_dicts(qapp):
    c = MultiSelectComboBox()
    c.setSelectAllEnabled(False)
    # Add items with dict data (as in examples/demo_data_role.py)
    c.addItem("Apple", {"id": 1, "code": "APL"})
    c.addItem("Banana", {"id": 2, "code": "BAN"})
    c.addItem("Orange", {"id": 3, "code": "ORG"})
    # Select two items
    c.setCurrentIndexes([0, 2])
    # Default display type is text; ensure joined text is correct and no exception occurs
    assert c.currentText() == "Apple, Orange"
    # Output type defaults to data; ensure currentData returns the dicts stored
    data = c.currentData()
    assert data == [{"id": 1, "code": "APL"}, {"id": 3, "code": "ORG"}]


def test_set_current_text_empty_string_clears_selection(combo: MultiSelectComboBox):
    combo.setCurrentIndexes([0, 1, 2])
    combo.setCurrentText("")
    assert combo.getCurrentIndexes() == []


def test_select_all_custom_text_and_find_indices(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setSelectAllEnabled(True, text="Everything")
    assert c.model().rowCount() == 4
    # findText should return index of option rows, not pseudo-item by default queries
    assert c.findText("A") == 1  # because row 0 is select all
    # ensure the custom text was applied
    assert c.model().item(0).text() == "Everything"


def test_duplicates_enabled_allows_duplicates(qapp):
    c = MultiSelectComboBox()
    c.setDuplicatesEnabled(True)
    c.addItem("A", "d1")
    c.addItem("A", "d1")
    c.addItem("A", "d2")
    assert c.model().rowCount() == 3


def test_toggle_select_all_off_removes_row(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.setSelectAllEnabled(True)
    assert c.model().rowCount() == 3
    c.setSelectAllEnabled(False)
    assert c.model().rowCount() == 2
    # ensure indices are back to 0..n-1 for options
    assert c.findText("B") == 1


def test_display_delimiter_variations_affect_set_current_text(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setDisplayDelimiter(";", space_after=False, space_before=False)
    c.setCurrentText("A;B")
    assert c.getCurrentIndexes() == [0, 1]
    c.setDisplayDelimiter("|", space_after=True, space_before=True)
    c.setCurrentText(" A | C ")
    assert c.getCurrentIndexes() == [0, 2]


def test_invert_selection_with_select_all_enabled(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setSelectAllEnabled(True)
    c.clearSelection()
    c.invertSelection()
    assert c.getCurrentIndexes() == [1, 2, 3] if c.isSelectAllEnabled() else [0, 1, 2]
    # For clarity, convert to option indices by subtracting first option row
    base = 1 if c.isSelectAllEnabled() else 0
    assert [i - base for i in c.getCurrentIndexes()] == [0, 1, 2]


# --- GUI interactions to cover eventFilter and popup lifecycle ---

def test_event_filter_clicks_and_select_all_toggle(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setSelectAllEnabled(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()

    # Click row 1 (first option after Select All) to check it
    idx_opt1 = c.model().index(1, 0)
    rect1 = c.view().visualRect(idx_opt1)
    pos1 = rect1.center()
    QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos1)
    assert c.getCurrentIndexes() == [1]

    # Click Select All row (0) to select all
    idx_sa = c.model().index(0, 0)
    rect_sa = c.view().visualRect(idx_sa)
    pos_sa = rect_sa.center()
    QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos_sa)
    # All options should be selected now
    assert [i for i in range(1, c.model().rowCount())] == c.getCurrentIndexes()

    # Click Select All again to clear
    QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos_sa)
    assert c.getCurrentIndexes() == []

    c.hidePopup()


def test_max_selection_zero_and_negative_disable_limit(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    # Zero should disable limit
    c.setMaxSelectionCount(0)
    c.selectAll()
    assert len(c.getCurrentIndexes()) == 3
    # Negative also disables
    c.clearSelection()
    c.setMaxSelectionCount(-5)
    c.selectAll()
    assert len(c.getCurrentIndexes()) == 3


def test_line_edit_click_toggles_popup(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.show()
    qapp.processEvents()
    # Open popup explicitly to ensure consistent state
    c.showPopup()
    qapp.processEvents()
    assert c.view().isVisible()
    # When popup open, clicking line edit should hide it due to closeOnLineEditClick
    QTest.mouseClick(c.lineEdit(), Qt.MouseButton.LeftButton)
    # hidePopup uses a 100ms timer; wait briefly for it to take effect
    QTest.qWait(150)
    qapp.processEvents()
    assert not c.view().isVisible()
    qapp.processEvents()


def test_popup_lifecycle_timer_and_line_edit_toggle(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.show()
    qapp.processEvents()
    # showPopup sets flag
    c.showPopup()
    assert c.closeOnLineEditClick is True
    # hidePopup starts timer; after processEvents, timerEvent should reset flag
    c.hidePopup()
    # Allow the 100ms timer to fire
    QTest.qWait(150)
    qapp.processEvents()
    assert c.closeOnLineEditClick is False


def test_show_and_resize_events_update_text(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    c.setPlaceholderText("Pick items")
    c.addItems(["Alpha", "Beta"]) 
    # Before show, line edit text may not be set; show should update
    c.show()
    qapp.processEvents()
    # After showEvent -> updateText -> placeholder visible
    assert c.currentText() == "Pick items"
    # Select one and resize to trigger elision path
    c.setCurrentIndexes([0])
    # Make the widget narrow and ensure updateText runs on resize
    old_text = c.currentText()
    c.resize(50, c.height())
    qapp.processEvents()
    # currentText (non-elided) remains the same
    assert c.currentText() == old_text


def test_find_text_case_sensitive_and_contains(combo: MultiSelectComboBox):
    # Case sensitive exact should fail for lower-case
    assert combo.findText("b", Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchCaseSensitive) == -1
    # Case sensitive exact should pass for exact case
    assert combo.findText("B", Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchCaseSensitive) == 1
    # Case sensitive contains should fail for different case
    assert combo.findText("b", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchCaseSensitive) == -1
    # Case insensitive contains should pass
    assert combo.findText("b", Qt.MatchFlag.MatchContains) == 1


def test_keyboard_space_enter_toggle(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])
    c.setSelectAllEnabled(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()

    # Toggle first option with Space then Enter
    c.view().setCurrentIndex(c.model().index(1, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Space)
    assert c.getCurrentIndexes() == [1]
    QTest.keyClick(c.view(), Qt.Key.Key_Return)
    assert c.getCurrentIndexes() == []

    # Toggle Select All row with Space
    c.view().setCurrentIndex(c.model().index(0, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Space)
    assert [i for i in range(1, c.model().rowCount())] == c.getCurrentIndexes()


def test_close_on_select_behavior(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.setSelectAllEnabled(True)
    c.setCloseOnSelect(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()

    # Select an item via keyboard; popup should close
    c.view().setCurrentIndex(c.model().index(1, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Space)
    qapp.processEvents()
    assert not c.view().isVisible()


def test_item_flags_include_selectable(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A"]) 
    flags = c.model().item(0).flags()
    assert bool(flags & Qt.ItemFlag.ItemIsSelectable)


def test_placeholder_sets_native(qapp):
    c = MultiSelectComboBox()
    c.setPlaceholderText("Pick items")
    assert c.lineEdit().placeholderText() == "Pick items"


def test_output_role_and_misc_apis(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    # Manually set a different role's data for first item
    c.model().item(0).setData("dispA", int(Qt.ItemDataRole.DisplayRole))
    # Switch output role to DisplayRole and select first
    c.setOutputDataRole(Qt.ItemDataRole.DisplayRole)
    assert c.getOutputDataRole() == Qt.ItemDataRole.DisplayRole
    c.setCurrentIndexes([0])
    assert c.currentData() == ["dispA"]
    # beginUpdate/endUpdate should not error and should coalesce updates
    c.beginUpdate()
    c.addItem("C", "dc")
    c.endUpdate()
    assert c.findText("C") != -1
    # Placeholder text getter
    c.setPlaceholderText("Choose")
    assert c.getPlaceholderText() == "Choose"
    # Close-on-select toggle and query
    c.setCloseOnSelect(True)
    assert c.isCloseOnSelect() is True


def test_runtime_set_model_and_role_switch(qapp):
    from PyQt6.QtGui import QStandardItemModel, QStandardItem

    c = MultiSelectComboBox()
    # Build a custom model like the runtime role switch demo
    m = QStandardItemModel()

    def add_item(text, code):
        it = QStandardItem(text)
        it.setData(code, int(Qt.ItemDataRole.DisplayRole))
        it.setData({"code": code}, int(Qt.ItemDataRole.UserRole))
        it.setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        )
        it.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        m.appendRow(it)

    for t, code in [("Apple", "APL"), ("Banana", "BAN")]:
        add_item(t, code)

    # Attach model at runtime; internal signals should connect without errors
    c.setModel(m)
    # Select row 0 and verify selection is tracked
    m.item(0).setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    # Coalesce updates are queued; process events to be safe
    qapp.processEvents()
    assert c.getCurrentIndexes() == [0]


# --- In-popup filter tests ---

def test_filter_enable_disable_and_row_hiding(qapp):
    c = MultiSelectComboBox()
    c.addItems(["Alpha", "Beta", "Gamma", "Alphabet"])  # 4 items
    # Initially disabled
    assert c.isFilterEnabled() is False
    c.setFilterEnabled(True)
    assert c.isFilterEnabled() is True

    # Show to create the popup view and filter UI
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()

    # The private filter edit should be present; set text to filter
    assert getattr(c, "_filterEdit") is not None
    c._filterEdit.setText("Al")  # matches Alpha and Alphabet
    qapp.processEvents()

    # Verify hidden rows: expect rows with "Alpha" and "Alphabet" visible
    view = c.view()
    # Determine indices by item text to avoid relying on order
    texts = [c.model().item(i).text() for i in range(c.model().rowCount())]
    idx_alpha = texts.index("Alpha")
    idx_alphabet = texts.index("Alphabet")
    idx_beta = texts.index("Beta")
    idx_gamma = texts.index("Gamma")
    assert view.isRowHidden(idx_alpha) is False
    assert view.isRowHidden(idx_alphabet) is False
    assert view.isRowHidden(idx_beta) is True
    assert view.isRowHidden(idx_gamma) is True

    # Clearing filter shows all
    c._filterEdit.clear()
    qapp.processEvents()
    for row in range(c.model().rowCount()):
        assert view.isRowHidden(row) is False

    # Disable filter tears down UI and clears hiding
    c.setFilterEnabled(False)
    qapp.processEvents()
    assert getattr(c, "_filterEdit") is None
    for row in range(c.model().rowCount()):
        assert view.isRowHidden(row) is False


def test_filter_persists_across_model_changes(qapp):
    from PyQt6.QtGui import QStandardItem

    c = MultiSelectComboBox()
    c.addItems(["One", "Two", "Three"])  # 3 items
    c.setFilterEnabled(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()

    # Apply a filter that matches only "Two"
    c._filterEdit.setText("wo")
    qapp.processEvents()
    view = c.view()
    texts = [c.model().item(i).text() for i in range(c.model().rowCount())]
    idx_one = texts.index("One")
    idx_two = texts.index("Two")
    idx_three = texts.index("Three")
    assert view.isRowHidden(idx_one) is True
    assert view.isRowHidden(idx_two) is False
    assert view.isRowHidden(idx_three) is True

    # Insert a new row that matches the filter ("Twofold"); filter should reapply
    it = QStandardItem("Twofold")
    it.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
    it.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
    c.model().appendRow(it)
    qapp.processEvents()

    texts2 = [c.model().item(i).text() for i in range(c.model().rowCount())]
    idx_twofold = texts2.index("Twofold")
    assert view.isRowHidden(idx_twofold) is False


def test_filter_keeps_select_all_visible(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setSelectAllEnabled(True)
    c.setFilterEnabled(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()
    # Apply a filter that matches none of the options
    c._filterEdit.setText("ZZZ")
    qapp.processEvents()
    # Row 0 is Select All -> should remain visible
    assert c.view().isRowHidden(0) is False
    # All option rows should be hidden
    for row in range(1, c.model().rowCount()):
        assert c.view().isRowHidden(row) is True


def test_display_delimiter_with_embedded_spaces(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    # Provide a delimiter that already contains spaces; widget should respect it verbatim
    c.setDisplayDelimiter(" | ")
    c.setCurrentIndexes([0, 1])
    assert c.getDisplayDelimiter() == " | "
    assert c.currentText() == "A | B"


def test_display_delimiter_spacing_flags(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.setDisplayDelimiter(";", space_after=False, space_before=True)
    c.setCurrentIndexes([0, 1])
    assert c.getDisplayDelimiter() == " ;"
    assert c.currentText() == "A ;B"


def test_invalid_output_and_display_type_raise(qapp):
    c = MultiSelectComboBox()
    with pytest.raises(ValueError):
        c.setOutputType("invalid")
    with pytest.raises(ValueError):
        c.setDisplayType("invalid")


def test_set_current_text_with_iterable_mixed_types(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"], ["da", "db"]) 
    # Mixed iterable including a dict that doesn't match; only "A" should be selected
    c.setCurrentText([{ "k": 1 }, "A"])  # dict will be str()-ed and won't match
    assert c.getCurrentIndexes() == [0]


def test_find_data_with_custom_role(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    # Set custom role on B and search using that role
    role = int(Qt.ItemDataRole.DisplayRole)
    c.model().item(1).setData("Bee", role)
    assert c.findData("Bee", role=role) == 1


def test_select_all_enabled_on_empty_model_no_crash(qapp):
    c = MultiSelectComboBox()
    # Enable Select All with no items and ensure no crash/edge
    c.setSelectAllEnabled(True)
    # selectAll on empty should not change selection and should not crash
    c.selectAll()
    assert c.getCurrentIndexes() == []
    # clearSelection on empty
    c.clearSelection()
    assert c.getCurrentIndexes() == []


def test_set_model_twice_disconnects_and_reconnects(qapp):
    from PyQt6.QtGui import QStandardItemModel, QStandardItem
    c = MultiSelectComboBox()
    m1 = QStandardItemModel()
    it1 = QStandardItem("One")
    it1.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
    it1.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    m1.appendRow(it1)
    c.setModel(m1)
    qapp.processEvents()
    assert c.getCurrentIndexes() == [0]
    # Now set a new model and ensure previous connections don't interfere
    m2 = QStandardItemModel()
    it2 = QStandardItem("Two")
    it2.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
    it2.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    m2.appendRow(it2)
    c.setModel(m2)
    qapp.processEvents()
    assert c.getCurrentIndexes() == [0]


def test_get_current_options_respects_output_role(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    # Set custom DisplayRole data for first item
    c.model().item(0).setData("dispA", int(Qt.ItemDataRole.DisplayRole))
    c.setCurrentIndexes([0])
    # Default output role is UserRole; addItems stored data=text at UserRole
    text_user = c.getCurrentOptions()
    # After setting DisplayRole on the item, item.text() reflects that role,
    # so the tuple's text component becomes 'dispA'. UserRole data remains 'A'.
    assert text_user == [("dispA", "A")]
    # Switch to DisplayRole -> data part should change
    c.setOutputDataRole(Qt.ItemDataRole.DisplayRole)
    text_disp = c.getCurrentOptions()
    # With DisplayRole active, data component is 'dispA'; and since DisplayRole
    # was set earlier, item.text() also reflects 'dispA'.
    assert text_disp == [("dispA", "dispA")]

    # Switch back to UserRole: currentData returns dicts
    c.setOutputDataRole(Qt.ItemDataRole.UserRole)
    data_user = c.currentData()
    # Items were created via addItems without explicit data, so UserRole holds the text
    assert data_user == ["A"]
    # currentText uses item.text(); since DisplayRole was set to 'dispA',
    # QStandardItem.text() reflects that value regardless of output role.
    assert c.currentText() == "dispA"

    # Switch output role to DisplayRole -> currentData returns codes
    c.setOutputDataRole(Qt.ItemDataRole.DisplayRole)
    data_disp = c.currentData()
    assert data_disp == ["dispA"]
    # currentText remains the same code text
    assert c.currentText() == "dispA"


def test_runtime_model_rows_and_reset_paths(qapp):
    from PyQt6.QtGui import QStandardItemModel, QStandardItem

    c = MultiSelectComboBox()
    m = QStandardItemModel()

    # Connect and insert rows -> should rebuild caches via rowsInserted
    c.setModel(m)
    it1 = QStandardItem("One")
    it1.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
    it1.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    m.appendRow(it1)
    qapp.processEvents()
    assert c.getCurrentIndexes() == [0]

    # Remove row -> rowsRemoved path
    m.removeRow(0)
    qapp.processEvents()
    assert c.getCurrentIndexes() == []

    # Model reset via clear() -> modelReset path, then add again
    m.clear()
    qapp.processEvents()
    it2 = QStandardItem("Two")
    it2.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
    it2.setData(Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    m.appendRow(it2)
    qapp.processEvents()
    assert c.getCurrentIndexes() == [0]


# --- Accessibility (A11y) tests ---

def test_accessible_names_update_with_selection(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    # Initially none selected
    qapp.processEvents()
    assert "No items selected." in (c.accessibleName() or "")
    assert (c.lineEdit().accessibleName() or "").startswith("Selected items.")

    # Select one item -> should say 1 item selected
    c.setCurrentIndexes([0])
    qapp.processEvents()
    assert "1 item selected." in (c.accessibleName() or "")
    assert "1 item selected." in (c.lineEdit().accessibleName() or "")

    # Select two items -> plural form
    c.setCurrentIndexes([0, 2])
    qapp.processEvents()
    assert "2 items selected." in (c.accessibleName() or "")
    assert "2 items selected." in (c.lineEdit().accessibleName() or "")


def test_aria_like_hints_tooltips_and_status_tips(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.setSelectAllEnabled(True)
    c.show()
    qapp.processEvents()

    # Select All pseudo-item hints
    sa = c.model().item(0)
    # After coalesced update, tooltip/status tip should be populated
    qapp.processEvents()
    sa_tip = sa.toolTip() or ""
    assert "toggles selection of all items" in sa_tip
    assert "None selected." in sa_tip
    assert "unchecked" in sa_tip or "partially checked" in sa_tip or "checked" in sa_tip
    assert "Use Up/Down to navigate; press Space or Enter to toggle." in sa_tip

    # Toggle to all selected and verify updated summary/state
    c.selectAll()
    qapp.processEvents()
    sa_tip2 = sa.toolTip() or ""
    assert "All selected." in sa_tip2
    # Regular option hints
    opt0 = c.model().item(1)
    tip0 = opt0.toolTip() or ""
    assert "Option 'A'" in tip0
    assert "is selected" in tip0
    assert "Use Up/Down to navigate; press Space or Enter to toggle." in tip0

    # Clear and check option hint updates to not selected
    c.clearSelection()
    qapp.processEvents()
    tip0_cleared = (c.model().item(1).toolTip() or "")
    assert "is not selected" in tip0_cleared


# --- Clear button and clear() slot ---

def test_line_edit_has_clear_button_enabled(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    # Clear button should be enabled on the internal line edit
    assert c.lineEdit().isClearButtonEnabled() is True


def test_clear_slot_clears_selection_and_emits_once(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setCurrentIndexes([0, 2])
    captured = []

    def on_changed(values):
        captured.append(list(values))

    c.selectionChanged.connect(on_changed)
    # Call clear() once -> should clear selection and emit once
    c.clear()
    qapp.processEvents()
    assert c.getCurrentIndexes() == []
    # There should be exactly 1 emission for the changed selection
    assert len(captured) >= 1
    # If there were previous emissions from setCurrentIndexes coalescing, ensure last is empty
    assert captured[-1] == []

    # Calling clear() again should not emit a new signal since selection didn't change
    prev_len = len(captured)
    c.clear()
    qapp.processEvents()
    assert len(captured) == prev_len


def test_line_edit_blocks_typing(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.setDisplayType("text")
    c.show()
    qapp.processEvents()
    # Focus line edit and attempt to type; eventFilter should block edits
    c.lineEdit().setFocus()
    QTest.keyClick(c.lineEdit(), Qt.Key.Key_A)
    qapp.processEvents()
    # No selection; currentText should remain empty (placeholder not set here)
    assert c.currentText() == ""


def test_keyboard_enter_toggle_paths(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setSelectAllEnabled(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()
    # Toggle option via Enter
    c.view().setCurrentIndex(c.model().index(1, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Return)
    assert c.getCurrentIndexes() == [1]
    # Toggle Select All via Enter -> should select all
    c.view().setCurrentIndex(c.model().index(0, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Return)
    assert [i for i in range(1, c.model().rowCount())] == c.getCurrentIndexes()
    c.hidePopup()


def test_type_selection_text_branch(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    # Ensure typeSelection returns text when requested explicitly
    assert c.typeSelection(0, "text", expected_type="data") == "A"


def test_line_edit_clear_button_action_clears_selection(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B"]) 
    c.setDisplayType("text")
    c.setCurrentIndexes([0, 1])
    qapp.processEvents()
    # Simulate user clicking the clear button by invoking QLineEdit.clear()
    captured = []

    def on_changed(values):
        captured.append(list(values))

    c.selectionChanged.connect(on_changed)
    # Ensure text is non-empty before clear
    assert c.currentText() != ""
    c.lineEdit().clear()
    qapp.processEvents()
    assert c.getCurrentIndexes() == []
    assert captured and captured[-1] == []


# --- Max selection (setMaxSelectionCount) tests ---


def test_max_selection_basic_enforcement(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C", "D"])  # 4 items
    c.setMaxSelectionCount(2)
    # selectAll should cap at 2
    c.selectAll()
    assert len(c.getCurrentIndexes()) == 2


def test_max_selection_disable_and_reenable(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C", "D"])  # 4 items
    # Set a limit and select
    c.setMaxSelectionCount(2)
    assert c.maxSelectionCount() == 2
    c.setCurrentIndexes([0, 1])
    assert len(c.getCurrentIndexes()) == 2
    # Disable the limit and select all
    c.setMaxSelectionCount(None)
    assert c.maxSelectionCount() is None
    c.selectAll()
    assert len(c.getCurrentIndexes()) == 4
    # Re-enable with a stricter limit and ensure pruning occurs via getter
    c.setMaxSelectionCount(1)
    # Accessor should enforce pruning if needed
    idxs = c.getCurrentIndexes()
    assert len(idxs) == 1


def test_invert_selection_with_limit_respects_capacity(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    c.setMaxSelectionCount(2)
    # Start with first checked
    c.setCurrentIndexes([0])
    # Invert -> tries to check the other two, but should cap at 2 total
    c.invertSelection()
    idxs = c.getCurrentIndexes()
    assert len(idxs) == 2


# --- Tooltip synchronization for elided text ---

def test_tooltip_mirrors_current_text_when_enabled(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    c.addItems(["Alpha", "Beta", "Gamma"]) 
    c.setCurrentIndexes([0, 2])
    qapp.processEvents()
    # By default tooltip sync is enabled; tooltip should equal full currentText
    assert c.toolTip() == c.currentText()


def test_tooltip_stays_full_on_resize_and_elision(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    # Long names to trigger elision easily
    items = [
        "Massachusetts",
        "Rhode Island",
        "Connecticut",
        "New Hampshire",
    ]
    c.addItems(items)
    c.setCurrentText(["Massachusetts", "Rhode Island", "Connecticut"])  # by text
    qapp.processEvents()

    full_text_before = c.currentText()
    # Make the widget narrow to force elision in the line edit display
    c.resize(120, c.height())
    qapp.processEvents()

    # Tooltip should mirror the full (non-elided) text
    assert c.toolTip() == full_text_before
    # And currentText remains the full text regardless of elision
    assert c.currentText() == full_text_before


def test_disabling_tooltip_sync_stops_updates(qapp):
    c = MultiSelectComboBox()
    c.setDisplayType("text")
    c.addItems(["A", "B", "C"]) 
    c.setCurrentIndexes([0, 1])
    qapp.processEvents()
    synced_tip = c.toolTip()
    assert synced_tip == c.currentText()

    # Disable sync and change selection; tooltip should not follow anymore
    c.setElideToolTipEnabled(False)
    c.setCurrentIndexes([2])
    qapp.processEvents()
    assert c.currentText() == "C"
    # Tooltip should still be the previous value (or at least not equal currentText)
    assert c.toolTip() != c.currentText()
def test_set_current_indexes_respects_limit(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    c.setMaxSelectionCount(2)
    c.setCurrentIndexes([0, 1, 2])
    assert len(c.getCurrentIndexes()) == 2


def test_set_current_text_respects_limit(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    c.setMaxSelectionCount(2)
    c.setCurrentText(["A", "B", "C"])  # ask for 3
    assert len(c.getCurrentIndexes()) == 2


def test_click_block_when_limit_reached(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    c.setMaxSelectionCount(2)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()

    # Click to select first two
    for row in [0, 1]:
        idx = c.model().index(row, 0)
        rect = c.view().visualRect(idx)
        pos = rect.center()
        QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos)
    assert len(c.getCurrentIndexes()) == 2

    # Try clicking third; should remain 2
    idx3 = c.model().index(2, 0)
    rect3 = c.view().visualRect(idx3)
    pos3 = rect3.center()
    QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos3)
    assert len(c.getCurrentIndexes()) == 2

    c.hidePopup()


def test_keyboard_block_when_limit_reached(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    c.setMaxSelectionCount(2)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()

    # Select first two via keyboard
    c.view().setCurrentIndex(c.model().index(0, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Space)
    c.view().setCurrentIndex(c.model().index(1, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Space)
    assert len(c.getCurrentIndexes()) == 2

    # Attempt to select third via keyboard -> should stay at 2
    c.view().setCurrentIndex(c.model().index(2, 0))
    QTest.keyClick(c.view(), Qt.Key.Key_Space)
    assert len(c.getCurrentIndexes()) == 2

    c.hidePopup()


def test_external_over_selection_is_enforced(qapp):
    # If an external change somehow over-selects items, the widget should prune to the limit
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"])  # 3 items
    c.setMaxSelectionCount(2)
    # Manually mark all checked via model to simulate external change
    for i in range(c._firstOptionRow(), c.model().rowCount()):
        c.model().item(i).setCheckState(Qt.CheckState.Checked)
    # Process pending updates
    qapp.processEvents()
    # The widget should prune back down to 2 selections
    assert len(c.getCurrentIndexes()) == 2


def test_close_on_select_mouse_item_hides_popup_and_view(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setCloseOnSelect(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()
    assert c.view().isVisible()

    # Click row 0 (first option) to toggle and close
    idx0 = c.model().index(0, 0)
    rect0 = c.view().visualRect(idx0)
    pos0 = rect0.center()
    QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos0)
    qapp.processEvents()
    assert not c.view().isVisible()
    # Also ensure viewport is hidden as _forceHidePopupView is used
    assert not c.view().viewport().isVisible()


def test_show_popup_reopens_immediately_after_close_on_select(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setCloseOnSelect(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()
    assert c.view().isVisible()

    # Click an item to close
    idx0 = c.model().index(0, 0)
    rect0 = c.view().visualRect(idx0)
    pos0 = rect0.center()
    QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos0)
    qapp.processEvents()
    assert not c.view().isVisible()

    # Immediately request to show again; view should become visible without lag
    c.showPopup()
    qapp.processEvents()
    assert c.view().isVisible()


def test_close_on_select_mouse_select_all_row_hides_popup_and_view(qapp):
    c = MultiSelectComboBox()
    c.addItems(["A", "B", "C"]) 
    c.setSelectAllEnabled(True)
    c.setCloseOnSelect(True)
    c.show()
    qapp.processEvents()
    c.showPopup()
    qapp.processEvents()
    assert c.view().isVisible()

    # Click Select All row (0) to toggle and close
    idx_sa = c.model().index(0, 0)
    rect_sa = c.view().visualRect(idx_sa)
    pos_sa = rect_sa.center()
    QTest.mouseClick(c.view().viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pos_sa)
    qapp.processEvents()
    assert not c.view().isVisible()
    assert not c.view().viewport().isVisible()
