"""
Tự động hóa chấm công BOM BADO theo lịch trình hàng ngày (Mặc định 17:45).
Có chế độ Safe Mode (Dry Run) để test quy trình mà KHÔNG bấm nút.
"""
import sys
import os
import time
import logging
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from url.timekeeping_page import TIMEKEEPING_URL, CHAM_CONG_DIRECT_URL, CHROME_PATH, TARGET_TIME
from data import LOGIN_ACCOUNT, PASSWORD
from model.page.timekeeping_page import TimekeepingPage

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug.log")
handlers = [logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")]
if "--show-log" in sys.argv or "--verbose" in sys.argv:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=handlers
)
logger = logging.getLogger("SchedulerTimekeeping")

def ui_print(msg: str):
    """In thông báo trực quan trên terminal, ghi chi tiết vào debug.log"""
    print(msg, flush=True)
    logger.info(f"[UI] {msg}")

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("🚨 LỖI NGOẠI LỆ TRONG TIẾN TRÌNH HẸN GIỜ:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception

AUTOMATION_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automation_profile")

def perform_attendance_job(dry_run: bool = True):
    ui_print("=" * 60)
    ui_print(f"⏰ KÍCH HOẠT QUY TRÌNH CHẤM CÔNG LÚC: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if dry_run:
        ui_print("🔒 CHẾ ĐỘ AN TOÀN ĐANG BẬT (dry_run=True): KHÔNG BẤM NÚT CHẤM CÔNG!")
    else:
        ui_print("⚡ CHẾ ĐỘ THỰC THI THẬT (dry_run=False): TIẾN HÀNH BẤM CHẤM CÔNG!")
    ui_print("=" * 60)

    with sync_playwright() as p:
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

        # 1. Điều hướng thẳng tới trang chấm công
        logger.info(f"Mở trang chấm công: {CHAM_CONG_DIRECT_URL}")
        page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")
        page.wait_for_timeout(2000)

        # 2. Kiểm tra nếu đã ở đúng trang chấm công rồi thì KHỎI CẦN ĐĂNG NHẬP
        if timekeeping_page.is_already_logged_in():
            logger.info("🎉 ĐÃ Ở ĐÚNG TRANG CHẤM CÔNG (phiên đăng nhập vẫn còn hiệu lực) -> KHỎI CẦN ĐĂNG NHẬP!")
        else:
            logger.info("Chưa có phiên đăng nhập, thực hiện đăng nhập...")
            timekeeping_page.login(LOGIN_ACCOUNT, PASSWORD, CHAM_CONG_DIRECT_URL)
            try:
                page.wait_for_url(lambda u: "dang-nhap" not in u and "/quan-ly/cham-cong" in u, timeout=45000)
            except Exception:
                page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")

        page.wait_for_timeout(3000)

        # 3. Lấy locator và thực thi
        result = timekeeping_page.execute_timekeeping(action="checkout", dry_run=dry_run)
        
        # 4. Chụp ảnh kết quả
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        res_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"timekeeping_result_{timestamp}.png")
        page.screenshot(path=res_img, full_page=True)
        logger.info(f"Đã lưu ảnh bằng chứng: {res_img}")

        page.wait_for_timeout(5000)
        browser.close()
        logger.info(f"Hoàn thành job với kết quả: {result}")

def main():
    # Kiểm tra cờ chạy: mặc định dry_run = True (CỰC KỲ AN TOÀN)
    dry_run = True
    if "--live" in sys.argv:
        dry_run = False
        ui_print("⚠️ CHÚ Ý: ĐÃ KÍCH HOẠT CHẾ ĐỘ LIVE. HỆ THỐNG SẼ BẤM NÚT VÀO LÚC 17:45!")
    else:
        ui_print("🛡️ ĐANG CHẠY CHẾ ĐỘ AN TOÀN (DRY-RUN). Sẽ không có nút nào bị bấm.")

    target = TARGET_TIME  # "17:45"
    ui_print(f"⏰ Đã đặt lịch hẹn tự động chấm công lúc: {target} mỗi ngày.")
    ui_print("💡 Nhấn Ctrl + C để dừng tiến trình.")
    ui_print("📝 Toàn bộ log kỹ thuật được ghi ngầm vào: debug.log")

    # Đăng ký lịch với thư viện schedule
    schedule.every().day.at(target).do(perform_attendance_job, dry_run=dry_run)

    # Chạy vòng lặp kiểm tra
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
