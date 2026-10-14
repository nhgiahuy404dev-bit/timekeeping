"""
Kịch bản mở trang Chấm Công trực quan trên màn hình để bạn xem trực tiếp.
🔒 CAM KẾT AN TOÀN:
- TUYỆT ĐỐI KHÔNG CLICK VÀO NÚT CHẤM CÔNG!
- Chỉ highlight vùng nút trên giao diện để bạn nhìn thấy vị trí Locator chính xác.
"""
import sys
import os
import logging
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from url.timekeeping_page import CHAM_CONG_DIRECT_URL, CHROME_PATH
from model.page.timekeeping_page import TimekeepingPage

# Thư mục lưu profile tự động hóa riêng biệt (không đụng độ với Chrome bạn đang lướt web)
AUTOMATION_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automation_profile")

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug.log")
handlers = [logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")]
if "--show-log" in sys.argv or "--verbose" in sys.argv:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=handlers
)
logger = logging.getLogger("ViewLive")

def ui_print(msg: str):
    """In thông báo thân thiện trên terminal, ghi chi tiết vào debug.log"""
    print(msg, flush=True)
    logger.info(f"[UI] {msg}")

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("🚨 LỖI TRONG TIẾN TRÌNH VIEW LIVE:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception

def main():
    ui_print("=" * 65)
    ui_print("🖥️ MỞ TRÌNH DUYỆT TRỰC QUAN TRÊN MÀN HÌNH (HEADED MODE)")
    ui_print("🔒 TUYỆT ĐỐI KHÔNG BẤM NÚT CHẤM CÔNG - CHỈ HIGHLIGHT LOCATOR")
    ui_print("=" * 65)

    with sync_playwright() as p:
        # Dùng persistent context để lưu phiên đăng nhập vĩnh viễn cho automation
        context = p.chromium.launch_persistent_context(
            user_data_dir=AUTOMATION_PROFILE,
            executable_path=CHROME_PATH,
            channel="chrome",
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        page = context.pages[0] if context.pages else context.new_page()
        timekeeping_page = TimekeepingPage(page)

        ui_print(f"👉 Đang mở trang: {CHAM_CONG_DIRECT_URL}")
        page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")

        # Kiểm tra nếu đã ở đúng trang chấm công rồi thì KHỎI CẦN ĐĂNG NHẬP
        if timekeeping_page.is_already_logged_in():
            ui_print("🎉 ĐÃ Ở ĐÚNG TRANG CHẤM CÔNG RỒI -> KHỎI CẦN ĐĂNG NHẬP!")
        elif "dang-nhap" in page.url:
            ui_print("👉 Bạn hãy nhấp 'Đăng nhập với Google' trên màn hình Chrome đang mở.")
            ui_print("⏳ Đang đợi bạn đăng nhập vào trang chấm công...")
            try:
                page.wait_for_url(lambda u: "dang-nhap" not in u and "/quan-ly/cham-cong" in u, timeout=60000)
                ui_print("🎉 Đã phát hiện bạn vào trang chấm công thành công!")
            except Exception:
                pass

        page.wait_for_timeout(3000)

        # Quét Locator và Highlight trực tiếp trên màn hình
        ui_print("🔍 Đang quét và highlight Locator trên giao diện...")
        locators_info = timekeeping_page.inspect_and_get_locators()

        # Chụp ảnh lưu bằng chứng
        screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timekeeping_preview.png")
        page.screenshot(path=screenshot_path, full_page=True)

        ui_print("=" * 65)
        ui_print("✅ HOÀN TẤT: Locator đã được highlight trực tiếp trên màn hình của bạn!")
        ui_print(f"📊 Kết quả trạng thái: {locators_info.get('status')}")
        ui_print("🔒 Nút chấm công KHÔNG HỀ BỊ BẤM!")
        ui_print("👀 Cửa sổ sẽ giữ mở trong 30 giây để bạn thoải mái quan sát...")
        ui_print("=" * 65)

        page.wait_for_timeout(30000)
        context.close()
        ui_print("Đã đóng trình duyệt.")

if __name__ == "__main__":
    main()
