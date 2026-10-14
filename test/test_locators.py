"""
Kiểm thử bộ Locator thuần XPath và Page Object Model trong chế độ An Toàn (Safe Dry-Run).
"""
from model.locator.timekeeping_locator import LoginLocator, TimekeepingLocator
from model.page.timekeeping_page import TimekeepingPage

def test_xpath_syntax():
    """Kiểm tra toàn bộ locator đều bắt đầu bằng cú pháp XPath '//'"""
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
        assert xpath.startswith("//") or xpath.startswith("(//"), f"Locator {xpath} không phải là XPath hợp lệ!"

def test_safety_dry_run_lock():
    """Kiểm tra cơ chế khóa an toàn: tuyệt đối không bấm nút trong chế độ dry_run"""
    class MockTimekeepingPage(TimekeepingPage):
        def __init__(self):
            pass

    page = MockTimekeepingPage()
    res = page.execute_timekeeping(action="checkout", dry_run=True)
    assert res["status"] == "SKIPPED_CLICK"
    assert res["dry_run"] is True

def test_is_already_logged_in_logic():
    """Kiểm tra logic: nếu đã ở đúng trang chấm công thì khỏi cần đăng nhập"""
    class MockPage:
        def __init__(self, url):
            self.url = url

    class MockTimekeepingPage(TimekeepingPage):
        def __init__(self, url):
            self.page = MockPage(url)

    # Đang ở trang login (chứa dang-nhap) -> False
    page_login = MockTimekeepingPage("https://bom.bado.vn/quan-ly/dang-nhap?returnUrl=%2Fquan-ly%2Fcham-cong")
    assert page_login.is_already_logged_in() is False

    # Đã ở đúng trang chấm công -> True (khỏi cần đăng nhập)
    page_cham_cong = MockTimekeepingPage("https://bom.bado.vn/quan-ly/cham-cong")
    assert page_cham_cong.is_already_logged_in() is True

