"""
Định nghĩa toàn bộ Locator CHỈ SỬ DỤNG MÃ XPATH theo đúng yêu cầu.
Trích xuất và chuẩn hóa cho hệ thống BOM BADO (https://bom.bado.vn).

⚠️ CẢNH BÁO AN TOÀN:
- TUYỆT ĐỐI KHÔNG CLICK VÀO NÚT CHẤM CÔNG TRONG LÚC TEST / LẤY LOCATOR.
"""

class LoginLocator:
    """Các Locator dạng XPath trên trang Đăng nhập"""
    # Nút 'Đăng nhập với Google' (chọn nút hiển thị trên Desktop qua [last()])
    GOOGLE_LOGIN_BUTTON = "(//button[contains(., 'Đăng nhập với Google')])[last()]"
    
    # Nút 'Đối tác đăng nhập'
    PARTNER_LOGIN_BUTTON = "//button[contains(., 'Đối tác đăng nhập')]"
    
    # Input 'Tài khoản'
    USERNAME_INPUT = "//input[@placeholder='Tài khoản']"
    
    # Input 'Mật khẩu'
    PASSWORD_INPUT = "//input[@placeholder='Mật khẩu']"
    
    # Nút bấm submit 'ĐĂNG NHẬP'
    LOGIN_SUBMIT_BUTTON = "//button[contains(@class, 'admin-submit-btn-custom') or normalize-space()='ĐĂNG NHẬP']"
    
    # Google OAuth Popup Locators (100% XPath thuần)
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
        """Trả về 100% cú pháp XPath để chọn đúng tài khoản trong danh sách Choose an account"""
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
    """Các Locator dạng XPath trên trang Chấm Công"""
    
    # 1. NÚT CHẤM CÔNG RA (Mục tiêu 17h45 khi đang trong ca)
    CHECKOUT_BUTTON = "//button[contains(., 'Bắt đầu chấm công ra')]"
    CHECKOUT_BUTTON_SPAN = "//span[text()='Bắt đầu chấm công ra']/ancestor::button"
    
    # 2. NÚT CHẤM CÔNG VÀO
    CHECKIN_BUTTON = "//button[contains(., 'Bắt đầu chấm công vào')]"
    CHECKIN_BUTTON_SPAN = "//span[text()='Bắt đầu chấm công vào']/ancestor::button"
    
    # 3. CÁC TRẠNG THÁI CA LÀM VIỆC (Dạng XPath)
    # Chưa đến giờ chấm công
    BTN_UPCOMING = "//span[text()='Chưa đến giờ chấm công']/ancestor::div[1]"
    
    # Đã hoàn thành ca làm việc
    BTN_COMPLETED = "//span[text()='Đã hoàn thành ca làm việc']/ancestor::div[1]"
    
    # Chưa có ca làm việc
    BTN_NO_SHIFT = "//span[text()='Chưa có ca làm việc']/ancestor::div[1]"
    
    # 4. KHUNG CA VÀ THỜI GIAN LÀM VIỆC (XPath)
    SHIFT_CARD = "//div[contains(@class, 'rounded-[10px]') or contains(@class, 'rounded-[12px]')]"
    
    # 5. MODAL VÀ NÚT XÁC NHẬN (XPath)
    CONFIRM_MODAL = "//div[@role='dialog']"
    CONFIRM_BUTTON = "//button[contains(., 'Xác nhận') or contains(., 'Đồng ý')]"
    CANCEL_BUTTON = "//button[contains(., 'Hủy') or contains(., 'Đóng')]"
