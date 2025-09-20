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
