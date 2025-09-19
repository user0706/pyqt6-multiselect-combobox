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
    assert combo.getDisplayType() == "data"
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
