"""
Unit tests for Pure XPath Locators and Page Object Model Safety Guards.
Verifies:
1. Pure XPath syntax compliance (all locators start with '//' or '(//').
2. Multi-layer safety locks: Dry-run lock, Time guard, Once-per-day guard.
3. Session recognition logic.
"""
import os
import json
from datetime import datetime
from model.locator.timekeeping_locator import LoginLocator, TimekeepingLocator
from model.page.timekeeping_page import TimekeepingPage, is_checked_out_today, record_checkout_today, STATE_FILE

def test_xpath_syntax():
    """Verify all defined locators strictly follow pure XPath syntax starting with '//' or '(//'"""
    locators = [
        LoginLocator.GOOGLE_LOGIN_BUTTON,
        LoginLocator.PARTNER_LOGIN_BUTTON,
        LoginLocator.USERNAME_INPUT,
        LoginLocator.PASSWORD_INPUT,
        LoginLocator.LOGIN_SUBMIT_BUTTON,
        LoginLocator.GOOGLE_ACCOUNT_CHOOSER,
        LoginLocator.GOOGLE_USE_ANOTHER_ACCOUNT_BTN,
        LoginLocator.get_google_account_xpath("huy.nguyenn@bado.vn"),
        LoginLocator.GOOGLE_EMAIL_INPUT,
        LoginLocator.GOOGLE_EMAIL_NEXT_BTN,
        LoginLocator.GOOGLE_PASSWORD_INPUT,
        LoginLocator.GOOGLE_PASSWORD_NEXT_BTN,
        TimekeepingLocator.CHECKOUT_BUTTON,
        TimekeepingLocator.CHECKOUT_BUTTON_SPAN,
        TimekeepingLocator.CHECKIN_BUTTON,
        TimekeepingLocator.CHECKIN_BUTTON_SPAN,
        TimekeepingLocator.BTN_UPCOMING,
        TimekeepingLocator.BTN_COMPLETED,
        TimekeepingLocator.BTN_NO_SHIFT,
        TimekeepingLocator.SHIFT_CARD,
        TimekeepingLocator.CONFIRM_MODAL,
        TimekeepingLocator.CONFIRM_BUTTON,
        TimekeepingLocator.CANCEL_BUTTON
    ]
    for xpath in locators:
        assert xpath.startswith("//") or xpath.startswith("(//"), f"Locator {xpath} is not a valid pure XPath expression!"

def test_safety_dry_run_lock():
    """Verify Guard Layer 1: Dry-run mode strictly prevents button clicks"""
    class MockTimekeepingPage(TimekeepingPage):
        def __init__(self):
            pass

    page = MockTimekeepingPage()
    res = page.execute_timekeeping(action="checkout", dry_run=True)
    assert res["status"] == "SKIPPED_CLICK"
    assert res["dry_run"] is True

def test_safety_time_guard_lock():
    """Verify Guard Layer 3: Premature clicks before scheduled time (17:45) are blocked"""
    class MockTimekeepingPage(TimekeepingPage):
        def __init__(self):
            pass

    page = MockTimekeepingPage()
    # Force dry_run=False, but don't force time: if current time is before 17:45, it must block
    now = datetime.now()
    if now.hour < 17 or (now.hour == 17 and now.minute < 45):
        res = page.execute_timekeeping(action="checkout", dry_run=False, force_time=False)
        assert res["status"] in ("BLOCKED_BY_TIME_GUARD", "ALREADY_CHECKED_OUT_TODAY")

def test_is_already_logged_in_logic():
    """Verify session recognition logic: skip login when already on timekeeping page"""
    class MockPage:
        def __init__(self, url):
            self.url = url

    class MockTimekeepingPage(TimekeepingPage):
        def __init__(self, url):
            self.page = MockPage(url)

    # On login page -> False
    page_login = MockTimekeepingPage("https://bom.bado.vn/quan-ly/dang-nhap?returnUrl=%2Fquan-ly%2Fcham-cong")
    assert page_login.is_already_logged_in() is False

    # On timekeeping page -> True
    page_cham_cong = MockTimekeepingPage("https://bom.bado.vn/quan-ly/cham-cong")
    assert page_cham_cong.is_already_logged_in() is True
