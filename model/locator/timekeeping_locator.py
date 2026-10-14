"""
Pure XPath Locators definition for BOM BADO timekeeping system (https://bom.bado.vn).
All locators strictly use 100% pure XPath syntax.

⚠️ SAFETY WARNING:
- DO NOT CLICK TIMEKEEPING BUTTONS DURING TESTING / LOCATOR INSPECTION.
"""

class LoginLocator:
    """XPath locators for Login page and Google OAuth popup"""
    # Google Login Button on Desktop view
    GOOGLE_LOGIN_BUTTON = "(//button[contains(., 'Đăng nhập với Google')])[last()]"
    
    # Partner Login Button
    PARTNER_LOGIN_BUTTON = "//button[contains(., 'Đối tác đăng nhập')]"
    
    # Username input field
    USERNAME_INPUT = "//input[@placeholder='Tài khoản']"
    
    # Password input field
    PASSWORD_INPUT = "//input[@placeholder='Mật khẩu']"
    
    # Submit login button
    LOGIN_SUBMIT_BUTTON = "//button[contains(@class, 'admin-submit-btn-custom') or normalize-space()='ĐĂNG NHẬP']"
    
    # Google OAuth Popup Locators (100% pure XPath)
    GOOGLE_ACCOUNT_CHOOSER = "//div[@data-identifier or @data-email or contains(@class, 'account')]"
    GOOGLE_USE_ANOTHER_ACCOUNT_BTN = (
        "(//*[normalize-space()='Use another account' or normalize-space()='Sử dụng một tài khoản khác' or normalize-space()='Sử dụng tài khoản khác'] "
        "| //*[@role='link' or @role='button' or self::li][contains(., 'Use another account') or contains(., 'Sử dụng một tài khoản khác') or contains(., 'Sử dụng tài khoản khác')] "
        "| //*[contains(text(), 'Use another account') or contains(text(), 'Sử dụng một tài khoản khác') or contains(text(), 'Sử dụng tài khoản khác')] "
        "| //*[(contains(., 'Use another account') or contains(., 'Sử dụng một tài khoản khác') or contains(., 'Sử dụng tài khoản khác')) and not(*[contains(., 'Use another account') or contains(., 'Sử dụng một tài khoản khác')])])[1]"
    )
    GOOGLE_EMAIL_INPUT = "//input[@type='email' or @id='identifierId']"
    GOOGLE_EMAIL_NEXT_BTN = "(//*[@id='identifierNext']//button | //*[@id='identifierNext'] | //button[contains(., 'Tiếp theo') or contains(., 'Next')])[1]"
    GOOGLE_PASSWORD_INPUT = "//input[@type='password' or @name='Passwd' or @name='password']"
    GOOGLE_PASSWORD_NEXT_BTN = "(//*[@id='passwordNext']//button | //*[@id='passwordNext'] | //button[contains(., 'Tiếp theo') or contains(., 'Next')])[1]"

    @staticmethod
    def get_google_account_xpath(username: str) -> str:
        """Returns pure XPath to select target account from Choose an account list"""
        return (
            f"(//li[contains(., '{username}')] "
            f"| //*[@role='link' and contains(., '{username}')] "
            f"| //*[@role='button' and contains(., '{username}')] "
            f"| //*[contains(@class, 'account') and contains(., '{username}')] "
            f"| //*[@data-identifier='{username}' or @data-email='{username}'] "
            f"| //*[contains(., '{username}') and not(*[contains(., '{username}')])] "
            f"| //li[contains(., 'Huy Nguyễn')] "
            f"| //*[@role='link' and contains(., 'Huy Nguyễn')] "
            f"| //*[contains(., 'Huy Nguyễn') and not(*[contains(., 'Huy Nguyễn')])])[1]"
        )


class TimekeepingLocator:
    """XPath locators for Timekeeping page"""
    
    # 1. Check-out button (Target for 17:45 shift completion)
    CHECKOUT_BUTTON = "//button[contains(., 'Bắt đầu chấm công ra')]"
    CHECKOUT_BUTTON_SPAN = "//span[text()='Bắt đầu chấm công ra']/ancestor::button"
    
    # 2. Check-in button
    CHECKIN_BUTTON = "//button[contains(., 'Bắt đầu chấm công vào')]"
    CHECKIN_BUTTON_SPAN = "//span[text()='Bắt đầu chấm công vào']/ancestor::button"
    
    # 3. Work Shift State indicators
    # Shift upcoming / Not yet time
    BTN_UPCOMING = "//span[text()='Chưa đến giờ chấm công']/ancestor::div[1]"
    
    # Shift already completed
    BTN_COMPLETED = "//span[text()='Đã hoàn thành ca làm việc']/ancestor::div[1]"
    
    # No shift assigned
    BTN_NO_SHIFT = "//span[text()='Chưa có ca làm việc']/ancestor::div[1]"
    
    # 4. Work shift cards
    SHIFT_CARD = "//div[contains(@class, 'rounded-[10px]') or contains(@class, 'rounded-[12px]')]"
    
    # 5. Confirmation modal and action buttons
    CONFIRM_MODAL = "//div[@role='dialog']"
    CONFIRM_BUTTON = "//button[contains(., 'Xác nhận') or contains(., 'Đồng ý')]"
    CANCEL_BUTTON = "//button[contains(., 'Hủy') or contains(., 'Đóng')]"
