"""Step definitions: metadata for the visual test builder."""
from __future__ import annotations

STEP_TYPES = [
    {"id": "open_url", "label": "Open URL", "needs_locator": False, "needs_input": True},
    {"id": "click", "label": "Click Element", "needs_locator": True, "needs_input": False},
    {"id": "double_click", "label": "Double Click", "needs_locator": True, "needs_input": False},
    {"id": "right_click", "label": "Right Click", "needs_locator": True, "needs_input": False},
    {"id": "type_text", "label": "Type Text", "needs_locator": True, "needs_input": True},
    {"id": "clear_field", "label": "Clear Field", "needs_locator": True, "needs_input": False},
    {"id": "select_dropdown", "label": "Select Dropdown", "needs_locator": True, "needs_input": True},
    {"id": "check_checkbox", "label": "Check Checkbox", "needs_locator": True, "needs_input": False},
    {"id": "uncheck_checkbox", "label": "Uncheck Checkbox", "needs_locator": True, "needs_input": False},
    {"id": "wait", "label": "Wait (seconds)", "needs_locator": False, "needs_input": True},
    {"id": "wait_for_element", "label": "Wait for Element", "needs_locator": True, "needs_input": False},
    {"id": "scroll_to_element", "label": "Scroll to Element", "needs_locator": True, "needs_input": False},
    {"id": "scroll_page", "label": "Scroll Page", "needs_locator": False, "needs_input": True},
    {"id": "hover", "label": "Hover Over Element", "needs_locator": True, "needs_input": False},
    {"id": "press_key", "label": "Press Key", "needs_locator": True, "needs_input": True},
    {"id": "switch_frame", "label": "Switch to Frame", "needs_locator": True, "needs_input": False},
    {"id": "switch_window", "label": "Switch Window", "needs_locator": False, "needs_input": True},
    {"id": "screenshot", "label": "Take Screenshot", "needs_locator": False, "needs_input": False},
    {"id": "assert_text", "label": "Assert Text Present", "needs_locator": False, "needs_input": True},
    {"id": "assert_element_visible", "label": "Assert Element Visible", "needs_locator": True, "needs_input": False},
    {"id": "assert_url_contains", "label": "Assert URL Contains", "needs_locator": False, "needs_input": True},
    {"id": "assert_title_contains", "label": "Assert Title Contains", "needs_locator": False, "needs_input": True},
    {"id": "assert_element_text", "label": "Assert Element Text", "needs_locator": True, "needs_input": True},
    {"id": "custom_js", "label": "Execute JavaScript", "needs_locator": False, "needs_input": True},
]

LOCATOR_TYPES = ["id", "name", "xpath", "css", "class", "tag", "link_text", "partial_link_text"]
