"""Step executor: interprets step JSON against a Selenium WebDriver."""
from __future__ import annotations
import logging
import time
from typing import Any

log = logging.getLogger(__name__)

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

LOCATOR_MAP = {
    "id": "By.ID",
    "name": "By.NAME",
    "xpath": "By.XPATH",
    "css": "By.CSS_SELECTOR",
    "class": "By.CLASS_NAME",
    "tag": "By.TAG_NAME",
    "link_text": "By.LINK_TEXT",
    "partial_link_text": "By.PARTIAL_LINK_TEXT",
}

def _by(locator_type: str):
    mapping = {
        "id": By.ID,
        "name": By.NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }
    return mapping.get(locator_type.lower().strip(), By.XPATH)


def find_element(driver, locator_type: str, locator_value: str, timeout: int = 10):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((_by(locator_type), locator_value.strip())))


def find_clickable(driver, locator_type: str, locator_value: str, timeout: int = 10):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((_by(locator_type), locator_value.strip())))


def execute_step(driver, step: dict) -> dict:
    """Execute a single step. Returns {'success': bool, 'message': str}."""
    action = step.get("action", "")
    locator_type = step.get("locator_type", "id")
    locator_value = (step.get("locator_value") or "").strip()
    input_value = (step.get("input_value") or "").strip()
    # Cap element/assertion timeout at 0.8s max; open_url uses full page-load timeout
    raw_timeout = int(step.get("timeout", 10))
    timeout = raw_timeout if action == "open_url" else min(raw_timeout, 0.8)

    try:
        if action == "open_url":
            driver.get(input_value)
            # Wait for document readyState to be complete so the initial page is fully loaded
            try:
                WebDriverWait(driver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except Exception:
                pass # Allow it to try steps anyway
            return {"success": True, "message": f"Opened {input_value}"}

        elif action == "click":
            el = find_clickable(driver, locator_type, locator_value, timeout)
            el.click()
            return {"success": True, "message": f"Clicked {locator_type}={locator_value}"}

        elif action == "double_click":
            el = find_clickable(driver, locator_type, locator_value, timeout)
            ActionChains(driver).double_click(el).perform()
            return {"success": True, "message": f"Double-clicked {locator_value}"}

        elif action == "right_click":
            el = find_element(driver, locator_type, locator_value, timeout)
            ActionChains(driver).context_click(el).perform()
            return {"success": True, "message": f"Right-clicked {locator_value}"}

        elif action == "type_text":
            el = find_element(driver, locator_type, locator_value, timeout)
            el.clear()
            el.send_keys(input_value)
            return {"success": True, "message": f"Typed into {locator_value}"}

        elif action == "clear_field":
            el = find_element(driver, locator_type, locator_value, timeout)
            el.clear()
            return {"success": True, "message": f"Cleared {locator_value}"}

        elif action == "select_dropdown":
            el = find_element(driver, locator_type, locator_value, timeout)
            sel = Select(el)
            try:
                sel.select_by_visible_text(input_value)
            except Exception:
                sel.select_by_value(input_value)
            return {"success": True, "message": f"Selected '{input_value}'"}

        elif action == "check_checkbox":
            el = find_element(driver, locator_type, locator_value, timeout)
            if not el.is_selected():
                el.click()
            return {"success": True, "message": "Checked checkbox"}

        elif action == "uncheck_checkbox":
            el = find_element(driver, locator_type, locator_value, timeout)
            if el.is_selected():
                el.click()
            return {"success": True, "message": "Unchecked checkbox"}

        elif action == "wait":
            # Cap at 1.5 s so a test doesn't sit idle for long explicit waits
            secs = min(float(input_value) if input_value else 1.0, 1.5)
            time.sleep(secs)
            return {"success": True, "message": f"Waited {secs}s"}

        elif action == "wait_for_element":
            find_element(driver, locator_type, locator_value, timeout)
            return {"success": True, "message": f"Element found: {locator_value}"}

        elif action == "scroll_to_element":
            el = find_element(driver, locator_type, locator_value, timeout)
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            return {"success": True, "message": f"Scrolled to {locator_value}"}

        elif action == "scroll_page":
            driver.execute_script(f"window.scrollBy(0, {input_value or 300});")
            return {"success": True, "message": "Page scrolled"}

        elif action == "hover":
            el = find_element(driver, locator_type, locator_value, timeout)
            ActionChains(driver).move_to_element(el).perform()
            return {"success": True, "message": f"Hovered over {locator_value}"}

        elif action == "press_key":
            el = find_element(driver, locator_type, locator_value, timeout)
            key = getattr(Keys, input_value.upper(), input_value)
            el.send_keys(key)
            return {"success": True, "message": f"Pressed {input_value}"}

        elif action == "switch_frame":
            el = find_element(driver, locator_type, locator_value, timeout)
            driver.switch_to.frame(el)
            return {"success": True, "message": "Switched to frame"}

        elif action == "switch_window":
            idx = int(input_value) if input_value.isdigit() else 1
            driver.switch_to.window(driver.window_handles[idx])
            return {"success": True, "message": f"Switched to window {idx}"}

        elif action == "screenshot":
            return {"success": True, "message": "Screenshot taken", "take_screenshot": True}

        elif action == "assert_text":
            # Use instant JS check (does NOT wait for page load like driver.page_source does)
            # This allows the assert to FAIL on attempt 1 if the page is still transitioning
            # and PASS on attempt 2 once the page has loaded → triggers FLAKY detection
            current_html = driver.execute_script(
                "return document.documentElement ? document.documentElement.innerHTML : ''"
            ) or ""
            assert input_value.lower() in current_html.lower(), \
                f"Text '{input_value}' not found on page"
            return {"success": True, "message": f"Text '{input_value}' found"}


        elif action == "assert_element_visible":
            el = find_element(driver, locator_type, locator_value, timeout)
            assert el.is_displayed(), f"Element {locator_value} not visible"
            return {"success": True, "message": f"Element {locator_value} is visible"}

        elif action == "assert_url_contains":
            WebDriverWait(driver, timeout).until(EC.url_contains(input_value))
            return {"success": True, "message": f"URL contains '{input_value}'"}

        elif action == "assert_title_contains":
            assert input_value.lower() in driver.title.lower(), f"Title '{driver.title}' doesn't contain '{input_value}'"
            return {"success": True, "message": f"Title contains '{input_value}'"}

        elif action == "assert_element_text":
            el = find_element(driver, locator_type, locator_value, timeout)
            actual = el.text.strip()
            assert input_value in actual, f"Expected '{input_value}' in '{actual}'"
            return {"success": True, "message": f"Element text matches"}

        elif action == "custom_js":
            result = driver.execute_script(input_value)
            return {"success": True, "message": f"JS executed: {result}"}

        else:
            return {"success": False, "message": f"Unknown action: {action}"}

    except Exception as e:
        err_type = type(e).__name__
        err_msg = str(e).split("Stacktrace:")[0].replace("Message:", "").strip()
        if not err_msg:
            if "Timeout" in err_type:
                err_msg = "The page or element took too long to load (Timeout)."
            elif "NoSuchElement" in err_type:
                err_msg = f"Could not find element with {locator_type}='{locator_value}'."
            elif "ClickIntercepted" in err_type:
                err_msg = "Another element is blocking the click (Click Intercepted)."
            elif "NotInteractable" in err_type:
                err_msg = "The element is not visible or cannot be clicked."
            else:
                err_msg = f"Selenium error occurred ({err_type})"
        return {"success": False, "message": f"{err_type}: {err_msg}"}

