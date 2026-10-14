"""
Page Object Model cho màn hình Đăng nhập và Chấm công BOM BADO.
Đảm bảo cơ chế an toàn: mặc định dry_run=True (CHỈ LẤY LOCATOR, TUYỆT ĐỐI KHÔNG BẤM NÚT CHẤM CÔNG).
"""
import logging
from playwright.sync_api import Page
from model.page.base_page import BasePage
from model.locator.timekeeping_locator import LoginLocator, TimekeepingLocator

logger = logging.getLogger("TimekeepingPage")

class TimekeepingPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.login_locators = LoginLocator()
        self.timekeeping_locators = TimekeepingLocator()

    def is_already_logged_in(self) -> bool:
        """
        Kiểm tra xem trình duyệt đã ở đúng trang chấm công (phiên đăng nhập còn hiệu lực) hay chưa.
        Nếu ĐÚNG TRANG RỒI THÌ KHỎI ĐĂNG NHẬP.
        """
        current_url = self.page.url
        # Điều kiện 1: URL không chứa dang-nhap và chứa quan-ly/cham-cong
        if "dang-nhap" not in current_url and "cham-cong" in current_url:
            return True

        # Điều kiện 2: Kiểm tra sự hiện diện của các phần tử nút ca làm việc
        shift_indicators = [
            TimekeepingLocator.CHECKOUT_BUTTON,
            TimekeepingLocator.CHECKIN_BUTTON,
            TimekeepingLocator.BTN_UPCOMING,
            TimekeepingLocator.BTN_COMPLETED,
            TimekeepingLocator.BTN_NO_SHIFT
        ]
        for xpath in shift_indicators:
            try:
                if self.page.locator(xpath).first.is_visible(timeout=500):
                    return True
            except Exception:
                pass
        return False

    def login(self, username: str, password: str, login_url: str):
        """
        Điều hướng tới trang đăng nhập và xử lý đăng nhập vào BOM BADO.
        Nếu đã ở đúng trang rồi thì KHỎI ĐĂNG NHẬP.
        """
        # Kiểm tra trước: nếu đã ở đúng trang chấm công rồi thì KHỎI ĐĂNG NHẬP
        if self.is_already_logged_in():
            logger.info("🎉 ĐÃ Ở ĐÚNG TRANG CHẤM CÔNG RỒI -> KHỎI CẦN ĐĂNG NHẬP!")
            return True

        logger.info(f"Mở trang: {login_url}")
        self.page.goto(login_url, wait_until="networkidle")
        self.page.wait_for_timeout(2000)

        # Kiểm tra lại: nếu hệ thống tự nhận diện phiên và vào thẳng trang chấm công thì dừng ngay
        if self.is_already_logged_in():
            logger.info("🎉 Đã có phiên đăng nhập sẵn và đang ở đúng trang Chấm Công -> KHỎI CẦN ĐĂNG NHẬP!")
            return True

        # Kiểm tra nút đăng nhập Google
        google_btn = self.page.locator(LoginLocator.GOOGLE_LOGIN_BUTTON).first
        if google_btn.is_visible(timeout=5000):
            logger.info("Phát hiện nút Đăng nhập với Google công ty. Tiến hành click...")
            try:
                with self.page.expect_popup(timeout=10000) as popup_info:
                    google_btn.click()
                popup = popup_info.value
                logger.info("Cửa sổ Google popup đã mở.")

                # Chờ popup chuyển hướng từ Firebase sang Google Accounts (phải là accounts.google.com)
                try:
                    if "accounts.google.com" not in popup.url:
                        popup.wait_for_url(lambda u: "accounts.google.com" in u, timeout=20000)
                    logger.info(f"Popup đã tải trang Google Accounts: {popup.url}")
                except Exception as e_url:
                    logger.warning(f"Chờ accounts.google.com: {e_url}")

                popup.wait_for_load_state("domcontentloaded")
                popup.wait_for_timeout(1500)

                # Bước 1: Kiểm tra màn hình Chọn tài khoản (Choose an account)
                account_xpath = LoginLocator.get_google_account_xpath(username)
                account_el = popup.locator(account_xpath).first
                account_selected = False
                try:
                    account_el.wait_for(state="visible", timeout=8000)
                    logger.info(f"Phát hiện tài khoản {username} trong danh sách Choose an account. Đang click chọn...")
                    account_el.scroll_into_view_if_needed()
                    try:
                        account_el.click(timeout=3000)
                    except Exception:
                        account_el.click(force=True)
                    account_selected = True
                    logger.info(f"Đã click chọn tài khoản {username}.")
                    popup.wait_for_timeout(2000)
                except Exception:
                    logger.info("Không phát hiện tài khoản trong Choose an account, kiểm tra ô nhập Email...")

                # Nếu sau khi click chọn tài khoản mà popup đã tự đóng (do đã có phiên sẵn không cần mật khẩu)
                if popup.is_closed():
                    logger.info("✅ Cửa sổ Google popup đã tự động đóng sau khi chọn tài khoản (đăng nhập thành công)!")

                # Bước 2: Nếu chưa chọn tài khoản từ danh sách và popup vẫn mở, kiểm tra ô nhập Email
                if not account_selected and not popup.is_closed():
                    email_input = popup.locator(LoginLocator.GOOGLE_EMAIL_INPUT).first
                    if email_input.is_visible(timeout=3000):
                        logger.info(f"Điền email: {username}")
                        email_input.fill(username)
                        popup.wait_for_timeout(500)
                        email_input.press("Enter")
                        popup.wait_for_timeout(1500)

                        next_btn = popup.locator(LoginLocator.GOOGLE_EMAIL_NEXT_BTN).first
                        if next_btn.is_visible(timeout=1500):
                            try:
                                next_btn.click()
                            except Exception:
                                pass

                # Bước 3: Áp dụng khi Google yêu cầu Mật khẩu (tài khoản Signed out hoặc sau khi điền email)
                if not popup.is_closed():
                    pass_input = popup.locator(LoginLocator.GOOGLE_PASSWORD_INPUT).first
                    try:
                        if pass_input.is_visible(timeout=4000):
                            logger.info("Phát hiện ô nhập mật khẩu Google. Đang điền mật khẩu...")
                            pass_input.fill(password)
                            popup.wait_for_timeout(500)
                            pass_input.press("Enter")
                            popup.wait_for_timeout(1500)

                            pass_next_btn = popup.locator(LoginLocator.GOOGLE_PASSWORD_NEXT_BTN).first
                            if pass_next_btn.is_visible(timeout=1500):
                                try:
                                    pass_next_btn.click()
                                except Exception:
                                    pass
                    except Exception:
                        pass

                # Bước 4: Chờ popup Google đóng nếu vẫn còn mở
                if not popup.is_closed():
                    logger.info("⏳ Chờ hoàn tất đăng nhập Google (nếu có xác thực 2 bước 2FA trên điện thoại, hãy duyệt trên máy)...")
                    try:
                        popup.wait_for_event("close", timeout=45000)
                        logger.info("✅ Cửa sổ Google popup đã đóng thành công.")
                    except Exception:
                        logger.info("Popup chưa đóng hoặc đã hoàn tất xử lý. Tiếp tục kiểm tra trang chính...")

                # Chờ trang chính chuyển hướng khỏi trang đăng nhập
                try:
                    self.page.wait_for_url(lambda u: "dang-nhap" not in u and "/quan-ly" in u, timeout=15000)
                    logger.info(f"Đã chuyển hướng trang chính: {self.page.url}")
                except Exception:
                    pass

            except Exception as e:
                logger.error(f"Thông báo đăng nhập Google: {e}", exc_info=True)
            return

        # Nếu là form đăng nhập đối tác / admin
        partner_btn = self.page.locator(LoginLocator.PARTNER_LOGIN_BUTTON).first
        if partner_btn.is_visible(timeout=2000):
            logger.info("Mở form đăng nhập đối tác...")
            partner_btn.click()
            self.page.wait_for_timeout(1000)

        user_input = self.page.locator(LoginLocator.USERNAME_INPUT).first
        pass_input = self.page.locator(LoginLocator.PASSWORD_INPUT).first
        submit_btn = self.page.locator(LoginLocator.LOGIN_SUBMIT_BUTTON).first

        if user_input.is_visible(timeout=2000):
            logger.info(f"Điền thông tin tài khoản {username}...")
            user_input.fill(username)
            pass_input.fill(password)
            submit_btn.click()
            self.page.wait_for_load_state("networkidle")

    def inspect_and_get_locators(self) -> dict:
        """
        Quét và trích xuất toàn bộ locator trên trang chấm công.
        CHỈ ĐỌC THÔNG TIN VÀ HIGHLIGHT TRÊN MÀN HÌNH, TUYỆT ĐỐI KHÔNG CLICK LÊN NÚT CHẤM CÔNG!
        """
        logger.info("=" * 60)
        logger.info("🔍 BẮT ĐẦU QUÉT LOCATOR TRÊN TRANG CHẤM CÔNG (CHẾ ĐỘ AN TOÀN)")
        logger.info("=" * 60)
        
        locators_info = {
            "current_url": self.page.url,
            "status": "UNKNOWN",
            "locators": {}
        }

        # 1. Kiểm tra nút Ra ca (Mục tiêu 17h45)
        checkout_el = self.page.locator(TimekeepingLocator.CHECKOUT_BUTTON).first
        if checkout_el.is_visible(timeout=2000):
            locators_info["status"] = "IN_PROGRESS (Đang trong ca - Sẵn sàng chấm công ra)"
            locators_info["locators"]["checkout_button"] = {
                "name": "Nút Bắt đầu chấm công ra",
                "selector": TimekeepingLocator.CHECKOUT_BUTTON,
                "text": checkout_el.inner_text().strip(),
                "enabled": checkout_el.is_enabled()
            }
            logger.info("🟢 [LOCATOR FOUND] Nút 'Bắt đầu chấm công ra' đã hiển thị!")
            try:
                checkout_el.highlight()
                logger.info("✨ Đã highlight nút 'Bắt đầu chấm công ra' trên màn hình trình duyệt!")
            except Exception:
                pass

        # 2. Kiểm tra nút Vào ca
        checkin_el = self.page.locator(TimekeepingLocator.CHECKIN_BUTTON).first
        if checkin_el.is_visible(timeout=1000):
            locators_info["status"] = "READY (Sẵn sàng chấm công vào)"
            locators_info["locators"]["checkin_button"] = {
                "name": "Nút Bắt đầu chấm công vào",
                "selector": TimekeepingLocator.CHECKIN_BUTTON,
                "text": checkin_el.inner_text().strip(),
                "enabled": checkin_el.is_enabled()
            }
            logger.info("🟡 [LOCATOR FOUND] Nút 'Bắt đầu chấm công vào' đã hiển thị.")
            try:
                checkin_el.highlight()
            except Exception:
                pass

        # 3. Kiểm tra các trạng thái ca đang khóa
        upcoming_el = self.page.locator(TimekeepingLocator.BTN_UPCOMING).first
        if upcoming_el.is_visible(timeout=1000):
            locators_info["status"] = "UPCOMING (Chưa đến giờ chấm công)"
            locators_info["locators"]["upcoming_indicator"] = {
                "name": "Chưa đến giờ chấm công",
                "selector": TimekeepingLocator.BTN_UPCOMING
            }
            logger.info("ℹ️ [STATUS] Ca làm việc: Chưa đến giờ chấm công.")
            try:
                upcoming_el.highlight()
            except Exception:
                pass

        completed_el = self.page.locator(TimekeepingLocator.BTN_COMPLETED).first
        if completed_el.is_visible(timeout=1000):
            locators_info["status"] = "COMPLETED (Đã hoàn thành ca làm việc)"
            locators_info["locators"]["completed_indicator"] = {
                "name": "Đã hoàn thành ca làm việc",
                "selector": TimekeepingLocator.BTN_COMPLETED
            }
            logger.info("ℹ️ [STATUS] Ca làm việc: Đã hoàn thành.")

        no_shift_el = self.page.locator(TimekeepingLocator.BTN_NO_SHIFT).first
        if no_shift_el.is_visible(timeout=1000):
            locators_info["status"] = "NO_SHIFT (Chưa có ca làm việc)"
            locators_info["locators"]["no_shift_indicator"] = {
                "name": "Chưa có ca làm việc",
                "selector": TimekeepingLocator.BTN_NO_SHIFT
            }
            logger.info("ℹ️ [STATUS] Chưa có ca làm việc hôm nay.")

        logger.info(f"Tổng hợp trạng thái hiện tại: {locators_info['status']}")
        logger.info("=" * 60)
        return locators_info

    def execute_timekeeping(self, action: str = "checkout", dry_run: bool = True):
        """
        Thực hiện chấm công.
        QUY TẮC AN TOÀN TUYỆT ĐỐI:
        Mặc định dry_run = True: Chỉ kiểm tra locator sẵn sàng, KHÔNG BAO GIỜ GỌI .click().
        Chỉ khi dry_run = False và đúng giờ hẹn (17h45) mới được kích hoạt bấm!
        """
        if dry_run:
            logger.warning("=" * 60)
            logger.warning("🔒 CHẾ ĐỘ AN TOÀN (DRY-RUN): KHÔNG BẤM NÚT CHẤM CÔNG!")
            logger.warning(f"Đã khóa an toàn cho hành động: {action}")
            logger.warning("=" * 60)
            return {"status": "SKIPPED_CLICK", "dry_run": True, "action": action}

        # Nếu dry_run = False (khi chạy thật vào lúc 17h45):
        logger.info(f"Tiến hành bấm nút {action}...")
        if action == "checkout":
            btn = self.page.locator(TimekeepingLocator.CHECKOUT_BUTTON).first
            btn.click()
            logger.info("Đã bấm nút Chấm công ra ca thành công!")
            return {"status": "SUCCESS", "dry_run": False}
