"""
Kịch bản quét và hiển thị trực quan Locator trên trang Chấm Công BOM BADO.
⚠️ CẢNH BÁO AN TOÀN:
- Kịch bản mở trình duyệt trực tiếp trên màn hình (Headed mode) để bạn nhìn thấy.
- TUYỆT ĐỐI KHÔNG BẤM NÚT CHẤM CÔNG!
"""
import sys
import os
import json
import logging
from playwright.sync_api import sync_playwright

# Fix utf-8 output cho console Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from url.timekeeping_page import TIMEKEEPING_URL, CHAM_CONG_DIRECT_URL, CHROME_PATH
from data import LOGIN_ACCOUNT
from model.page.timekeeping_page import TimekeepingPage

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8")
    ]
)
logger = logging.getLogger("InspectLocators")

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("🚨 LỖI TRONG TIẾN TRÌNH INSPECT LOCATORS:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception

def run_inspector(headless: bool = False):
    logger.info("=" * 65)
    logger.info("🚀 ĐANG MỞ TRÌNH DUYỆT TRỰC QUAN (HEADED) TRÊN MÀN HÌNH CỦA BẠN")
    logger.info("🔒 CAM KẾT: CHỈ TÌM VÀ HIGHLIGHT LOCATOR - TUYỆT ĐỐI KHÔNG BẤM CHẤM CÔNG!")
    logger.info("=" * 65)

    with sync_playwright() as p:
        try:
            logger.info("Khởi động Google Chrome...")
            browser = p.chromium.launch(
                executable_path=CHROME_PATH,
                headless=headless,
                args=["--start-maximized"]
            )
        except Exception:
            logger.warning("Mở Playwright Chromium...")
            browser = p.chromium.launch(
                headless=headless,
                args=["--start-maximized"]
            )

        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        timekeeping_page = TimekeepingPage(page)

        # 1. Mở trang đăng nhập / chấm công
        logger.info(f"Truy cập: {TIMEKEEPING_URL}")
        page.goto(TIMEKEEPING_URL, wait_until="networkidle")

        # 2. Nếu đang ở trang đăng nhập, tự động kích hoạt Đăng nhập Google
        if "cham-cong" not in page.url or "dang-nhap" in page.url:
            logger.info("Đang ở trang đăng nhập. Kích hoạt Đăng nhập với Google...")
            google_btn = page.locator("button:has-text('Đăng nhập với Google'):visible").first
            if google_btn.is_visible(timeout=5000):
                try:
                    with page.expect_popup(timeout=8000) as popup_info:
                        google_btn.click()
                    popup = popup_info.value
                    logger.info("Cửa sổ đăng nhập Google đã mở trên màn hình.")
                    
                    # Nếu có sẵn tài khoản huy.nguyenn@bado.vn thì click chọn
                    account_el = popup.locator(f"div:has-text('{LOGIN_ACCOUNT}'), [data-email='{LOGIN_ACCOUNT}']").first
                    if account_el.is_visible(timeout=4000):
                        logger.info(f"Tự động chọn tài khoản {LOGIN_ACCOUNT}...")
                        account_el.click()
                except Exception:
                    pass

            logger.info("⏳ Chờ bạn hoàn tất đăng nhập nếu có popup (tối đa 45s)...")
            try:
                page.wait_for_url("**/quan-ly/cham-cong**", timeout=45000)
                logger.info("🎉 Đã vào thành công trang Chấm Công!")
            except Exception:
                logger.info("Tiếp tục điều hướng thẳng tới trang chấm công...")
                page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")

        # Chờ trang tải đầy đủ DOM
        page.wait_for_timeout(3000)

        # 3. Quét và Highlight Locator trên màn hình (CHẾ ĐỘ AN TOÀN)
        locators_result = timekeeping_page.inspect_and_get_locators()

        # 4. Chụp ảnh màn hình lưu bằng chứng
        screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timekeeping_preview.png")
        page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"📸 Đã lưu ảnh màn hình tại: {screenshot_path}")

        # 5. Lưu kết quả ra JSON
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_locators.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(locators_result, f, ensure_ascii=False, indent=2)

        # 6. Giữ màn hình trình duyệt mở để bạn quan sát
        logger.info("=" * 65)
        logger.info("👀 TRÌNH DUYỆT ĐANG MỞ TRÊN MÀN HÌNH ĐỂ BẠN QUAN SÁT!")
        logger.info("🔒 XÁC NHẬN AN TOÀN: Nút chấm công KHÔNG BỊ BẤM!")
        logger.info("Sẽ tự động đóng sau 25 giây quan sát...")
        logger.info("=" * 65)
        page.wait_for_timeout(25000)

        browser.close()
        logger.info("Đã đóng trình duyệt.")

if __name__ == "__main__":
    is_headless = "--headless" in sys.argv
    run_inspector(headless=is_headless)
