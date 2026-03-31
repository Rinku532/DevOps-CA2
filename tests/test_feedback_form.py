"""
test_feedback_form.py — Selenium Test Suite
Sub Task 4: Automated tests for Student Feedback Registration Form

Test Cases:
  TC1 - Form page opens successfully
  TC2 - Valid form submission shows success modal
  TC3 - Blank mandatory fields show error messages
  TC4 - Invalid email format shows email error
  TC5 - Invalid mobile number shows mobile error
  TC6 - Department dropdown selection works
  TC7 - Submit and Reset buttons work correctly

Requirements:
  pip install selenium pytest webdriver-manager

Usage:
  pytest tests/test_feedback_form.py -v
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


import pathlib
import os

# ── Helper: absolute path to index.html ───────────────────────────────────────
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
FORM_URL = BASE_DIR.joinpath("index.html").as_uri()

WAIT_SEC  = 8   # max seconds for explicit waits


# ── Fixture: shared headless Chrome driver ────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """
    Create a single Chrome WebDriver instance for the entire module.
    Uses headless mode so it runs without a display (required for Jenkins CI).
    Relies on Selenium Manager (built into Selenium 4.6+) to auto-resolve ChromeDriver.
    """
    options = Options()
    options.add_argument("--headless=new")          # headless Chrome
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-gpu")

    # Selenium Manager (built-in since Selenium 4.6) auto-resolves the correct ChromeDriver
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(3)

    yield drv

    drv.quit()


# ── Utility helpers ───────────────────────────────────────────────────────────
def wait_visible(driver, by, locator, timeout=WAIT_SEC):
    """Wait until an element is visible and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, locator))
    )


def scroll_into_view(driver, element):
    """Scroll the given element into the viewport centre."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'nearest'});", element)
    time.sleep(0.15)


def click_element(driver, element):
    """Scroll into view then click. Falls back to JS click if blocked by CSS layers."""
    scroll_into_view(driver, element)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def fill_valid_form(driver):
    """Helper: populate all fields with valid data."""
    driver.find_element(By.ID, "studentName").clear()
    driver.find_element(By.ID, "studentName").send_keys("Rahul Sharma")

    driver.find_element(By.ID, "emailId").clear()
    driver.find_element(By.ID, "emailId").send_keys("rahul.sharma@college.edu")

    driver.find_element(By.ID, "mobileNumber").clear()
    driver.find_element(By.ID, "mobileNumber").send_keys("9876543210")

    # Department dropdown
    select = Select(driver.find_element(By.ID, "department"))
    select.select_by_value("CSE")

    # Gender radio
    click_element(driver, driver.find_element(By.ID, "genderMale"))

    # Comments (10+ words)
    comments = driver.find_element(By.ID, "feedbackComments")
    scroll_into_view(driver, comments)
    comments.clear()
    comments.send_keys(
        "The course content was excellent and very well structured. Highly recommend it."
    )



# ═══════════════════════════════════════════════════════════════════════════════
# TC1 — Form page opens successfully
# ═══════════════════════════════════════════════════════════════════════════════
def test_tc1_page_opens_successfully(driver):
    """
    Verify that the feedback form page loads and the title/heading is present.
    """
    driver.get(FORM_URL)

    # Page title contains 'Feedback'
    assert "Feedback" in driver.title, (
        f"Expected 'Feedback' in page title, got: '{driver.title}'"
    )

    # Main heading visible
    heading = wait_visible(driver, By.TAG_NAME, "h1")
    assert "Feedback" in heading.text, (
        f"Expected 'Feedback' in h1 text, got: '{heading.text}'"
    )

    # Form element present
    form = driver.find_element(By.ID, "feedbackForm")
    assert form.is_displayed(), "feedbackForm element should be visible on the page."


# ═══════════════════════════════════════════════════════════════════════════════
# TC2 — Valid data entry → successful submission
# ═══════════════════════════════════════════════════════════════════════════════
def test_tc2_valid_form_submission(driver):
    """
    Fill all fields with valid data, click Submit, and verify the success modal appears.
    """
    driver.get(FORM_URL)
    fill_valid_form(driver)

    click_element(driver, driver.find_element(By.ID, "submitBtn"))
    time.sleep(0.5)  # allow JS validation + modal animation

    # Success modal should be visible
    modal = wait_visible(driver, By.ID, "successModal")
    assert modal.is_displayed(), "Success modal should appear after valid form submission."

    modal_title = driver.find_element(By.ID, "modal-title")
    assert "Submitted" in modal_title.text or "Feedback" in modal_title.text, (
        f"Modal title should confirm submission, got: '{modal_title.text}'"
    )

    # Close the modal for subsequent tests
    driver.find_element(By.ID, "modalClose").click()
    time.sleep(0.3)


# ═══════════════════════════════════════════════════════════════════════════════
# TC3 — Blank mandatory fields → all error messages visible
# ═══════════════════════════════════════════════════════════════════════════════
def test_tc3_blank_fields_show_errors(driver):
    """
    Click Submit without filling any field; every mandatory error should appear.
    """
    driver.get(FORM_URL)

    click_element(driver, driver.find_element(By.ID, "submitBtn"))
    time.sleep(0.3)

    # Success modal must NOT appear
    modal = driver.find_element(By.ID, "successModal")
    assert not modal.is_displayed(), "Success modal should NOT appear when form is empty."

    # Check all error spans have non-empty text
    error_ids = ["err-name", "err-email", "err-mobile", "err-dept", "err-gender", "err-comments"]
    for eid in error_ids:
        err = driver.find_element(By.ID, eid)
        assert err.text.strip(), (
            f"Error message for #{eid} should be visible when field is blank."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TC4 — Invalid email format → email error shown
# ═══════════════════════════════════════════════════════════════════════════════
def test_tc4_invalid_email_shows_error(driver):
    """
    Fill all other valid fields; enter an invalid email and check the error.
    """
    driver.get(FORM_URL)

    driver.find_element(By.ID, "studentName").send_keys("Test User")
    driver.find_element(By.ID, "emailId").send_keys("invalidemail@")   # malformed
    driver.find_element(By.ID, "mobileNumber").send_keys("9876543210")
    Select(driver.find_element(By.ID, "department")).select_by_value("IT")
    click_element(driver, driver.find_element(By.ID, "genderFemale"))
    comments = driver.find_element(By.ID, "feedbackComments")
    scroll_into_view(driver, comments)
    comments.send_keys(
        "Great experience with all the coursework and faculty members here."
    )

    click_element(driver, driver.find_element(By.ID, "submitBtn"))
    time.sleep(0.3)

    err_email = driver.find_element(By.ID, "err-email")
    assert err_email.text.strip(), (
        "Email error message should appear for an invalid email format."
    )

    # Modal must NOT appear
    modal = driver.find_element(By.ID, "successModal")
    assert not modal.is_displayed(), (
        "Success modal should NOT appear when email is invalid."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TC5 — Invalid mobile number → mobile error shown
# ═══════════════════════════════════════════════════════════════════════════════
def test_tc5_invalid_mobile_shows_error(driver):
    """
    Enter a mobile number containing letters; verify the mobile validation error.
    """
    driver.get(FORM_URL)

    driver.find_element(By.ID, "studentName").send_keys("Test User")
    driver.find_element(By.ID, "emailId").send_keys("test@example.com")
    driver.find_element(By.ID, "mobileNumber").send_keys("98ABC43210")  # invalid
    Select(driver.find_element(By.ID, "department")).select_by_value("ECE")
    click_element(driver, driver.find_element(By.ID, "genderOther"))
    comments5 = driver.find_element(By.ID, "feedbackComments")
    scroll_into_view(driver, comments5)
    comments5.send_keys(
        "Really enjoyed the practical sessions and hands on lab work."
    )

    click_element(driver, driver.find_element(By.ID, "submitBtn"))
    time.sleep(0.3)

    err_mobile = driver.find_element(By.ID, "err-mobile")
    assert err_mobile.text.strip(), (
        "Mobile error message should appear for a non-numeric mobile number."
    )

    modal = driver.find_element(By.ID, "successModal")
    assert not modal.is_displayed(), (
        "Success modal should NOT appear when mobile number is invalid."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TC6 — Department dropdown selection works correctly
# ═══════════════════════════════════════════════════════════════════════════════
def test_tc6_dropdown_selection_works(driver):
    """
    Select each department option and verify the selection persists.
    """
    driver.get(FORM_URL)

    department_select = Select(driver.find_element(By.ID, "department"))

    test_departments = [
        ("CSE",   "Computer Science"),
        ("IT",    "Information Technology"),
        ("AIDS",  "AI"),
    ]

    for value, label_fragment in test_departments:
        department_select.select_by_value(value)
        selected = department_select.first_selected_option
        assert selected.get_attribute("value") == value, (
            f"Expected department '{value}' to be selected, got: {selected.get_attribute('value')}"
        )
        assert label_fragment in selected.text, (
            f"Expected option text to contain '{label_fragment}', got: '{selected.text}'"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TC7 — Submit and Reset buttons work correctly
# ═══════════════════════════════════════════════════════════════════════════════
def test_tc7_submit_and_reset_buttons(driver):
    """
    Verify Submit triggers validation (not blank submission) and
    Reset clears all form fields.
    """
    driver.get(FORM_URL)

    # ── Part A: Submit with empty form triggers validation (no modal) ──
    name_field = driver.find_element(By.ID, "studentName")
    assert name_field.get_attribute("value") == "", "Name field should start empty."

    submit_btn = driver.find_element(By.ID, "submitBtn")
    scroll_into_view(driver, submit_btn)
    assert submit_btn.is_displayed() and submit_btn.is_enabled(), (
        "Submit button should be visible and enabled."
    )
    submit_btn.click()
    time.sleep(0.3)

    modal = driver.find_element(By.ID, "successModal")
    assert not modal.is_displayed(), "Empty submit should NOT open success modal."

    # ── Part B: Fill form, then Reset clears it ──
    fill_valid_form(driver)
    time.sleep(0.2)

    # Confirm data was entered
    assert driver.find_element(By.ID, "studentName").get_attribute("value") == "Rahul Sharma"

    reset_btn = driver.find_element(By.ID, "resetBtn")
    scroll_into_view(driver, reset_btn)
    assert reset_btn.is_displayed() and reset_btn.is_enabled(), (
        "Reset button should be visible and enabled."
    )
    reset_btn.click()
    time.sleep(0.3)

    # All text fields should now be empty
    assert driver.find_element(By.ID, "studentName").get_attribute("value") == "", (
        "Name field should be cleared after Reset."
    )
    assert driver.find_element(By.ID, "emailId").get_attribute("value") == "", (
        "Email field should be cleared after Reset."
    )
    assert driver.find_element(By.ID, "mobileNumber").get_attribute("value") == "", (
        "Mobile field should be cleared after Reset."
    )
    assert driver.find_element(By.ID, "feedbackComments").get_attribute("value") == "", (
        "Comments field should be cleared after Reset."
    )

    # Department should reset to placeholder
    dept_select = Select(driver.find_element(By.ID, "department"))
    assert dept_select.first_selected_option.get_attribute("value") == "", (
        "Department should reset to placeholder after Reset."
    )
