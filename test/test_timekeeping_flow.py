"""
Test Flow tự động điều hướng đến đúng trang Chấm Công BOM BADO rồi dừng lại.
🔒 NGUYÊN TẮC AN TOÀN:
- Flow chạy tới đúng trang https://bom.bado.vn/quan-ly/cham-cong.
- Kiểm tra URL và xác thực sự hiện diện của các phần tử XPath trên trang.
- DỪNG LẠI TẠI ĐÂY - TUYỆT ĐỐI KHÔNG CLICK VÀO NÚT CHẤM CÔNG!
"""
import os
import sys
import logging
from playwright.sync_api import sync_playwright

# Đảm bảo import từ thư mục gốc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from url.timekeeping_page import CHAM_CONG_DIRECT_URL, CHROME_PATH
from data import LOGIN_ACCOUNT, PASSWORD
from model.locator.timekeeping_locator import LoginLocator
from model.page.timekeeping_page import TimekeepingPage

# Cấu hình logging: Ghi toàn bộ dữ liệu chi tiết vào file debug.log
# Mặc định KHÔNG in định dạng debug.log ra terminal để màn hình sạch đẹp
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug.log")
# mode="w" đảm bảo xóa sạch log cũ của lần chạy trước, luôn bắt đầu với file log mới
handlers = [logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")]

# Chỉ bật StreamHandler nếu người dùng truyền cờ --show-log hoặc --verbose
if "--show-log" in sys.argv or "--verbose" in sys.argv:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=handlers
)
logger = logging.getLogger("TestTimekeepingFlow")

def ui_print(msg: str):
    """In thông báo ngắn gọn, trực quan trên terminal (không có timestamp/logger format)"""
    print(msg, flush=True)
    logger.info(f"[UI] {msg}")

# Bắt toàn bộ lỗi chưa xử lý và tự động ghi vào debug.log
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("🚨 LỖI HỆ THỐNG / EXCEPTION XẢY RA:", exc_info=(exc_type, exc_value, exc_traceback))
    ui_print(f"❌ Đã xảy ra lỗi: {exc_value}. Xem chi tiết trong file debug.log")

sys.excepthook = handle_unhandled_exception

AUTOMATION_PROFILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "automation_profile")

def test_flow_to_timekeeping_page():
    """
    Kịch bản kiểm thử:
    1. Khởi chạy trình duyệt (Headed mode để người dùng quan sát).
    2. Điều hướng tới trang BOM BADO.
    3. Hoàn tất đăng nhập nếu chưa có phiên.
    4. Xác nhận chuyển hướng ĐÚNG vào trang: https://bom.bado.vn/quan-ly/cham-cong.
    5. Kiểm tra và xác nhận các phần tử XPath trên trang chấm công.
    6. Dừng lại an toàn - KHÔNG THỰC HIỆN BẤT KỲ LỆNH BẤM CHẤM CÔNG NÀO!
    """
    ui_print("=" * 65)
    ui_print("🚀 BẮT ĐẦU TEST FLOW: ĐIỀU HƯỚNG TỚI TRANG CHẤM CÔNG RỒI DỪNG")
    ui_print("🔒 KHÓA AN TOÀN: TUYỆT ĐỐI KHÔNG BẤM NÚT CHẤM CÔNG")
    ui_print("=" * 65)

    try:
        with sync_playwright() as p:
            # Sử dụng Google Chrome với profile lưu session và tắt cờ automation
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

            # Bước 1: Mở URL chấm công
            ui_print(f"👉 [1/4] Đang mở URL hệ thống: {CHAM_CONG_DIRECT_URL}")
            page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")
            page.wait_for_timeout(2000)

            # Bước 2: Kiểm tra nếu ĐÃ Ở ĐÚNG TRANG CHẤM CÔNG rồi thì KHỎI ĐĂNG NHẬP
            if timekeeping_page.is_already_logged_in():
                ui_print("🎉 [2/4] ĐÃ Ở ĐÚNG TRANG CHẤM CÔNG (đã có phiên) -> KHỎI CẦN ĐĂNG NHẬP!")
            else:
                ui_print("🔑 [2/4] Hệ thống yêu cầu đăng nhập. Đang xử lý đăng nhập Google...")
                timekeeping_page.login(LOGIN_ACCOUNT, PASSWORD, CHAM_CONG_DIRECT_URL)

                ui_print("⏳ Đang chờ hoàn tất đăng nhập để vào hệ thống...")
                try:
                    page.wait_for_url(lambda u: "dang-nhap" not in u and "/quan-ly" in u, timeout=45000)
                    ui_print(f"✅ Đã đăng nhập thành công vào hệ thống: {page.url}")
                except Exception as e_nav:
                    logger.warning(f"Chưa tự động chuyển hướng: {e_nav}.")

                # Đảm bảo điều hướng thẳng tới đúng trang Chấm Công
                if "/quan-ly/cham-cong" not in page.url:
                    ui_print(f"👉 Đang chuyển hướng tới trang Chấm Công: {CHAM_CONG_DIRECT_URL}")
                    page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")

            # Chờ thêm thời gian để Vue/React load dữ liệu trang Chấm Công
            page.wait_for_timeout(3000)

            # Bước 3: Xác nhận đã vào ĐÚNG trang Chấm Công (loại bỏ trường hợp dang-nhap?returnUrl=...)
            current_url = page.url
            logger.info(f"Bước 3: Xác nhận URL: {current_url}")
            assert "dang-nhap" not in current_url and "/quan-ly/cham-cong" in current_url, (
                f"🚨 LỖI: Chưa vào đúng trang chấm công! URL hiện tại: {current_url}. "
                f"Vui lòng hoàn tất xác thực đăng nhập trên trình duyệt."
            )
            ui_print("✅ [3/4] Xác nhận: ĐÃ VÀO ĐÚNG TRANG CHẤM CÔNG!")

            # Bước 4: Quét các phần tử XPath trên trang chấm công
            ui_print("🔍 [4/4] Đang quét Locator và trạng thái ca làm việc (Chế độ An Toàn)...")
            locators_result = timekeeping_page.inspect_and_get_locators()
            ui_print(f"📊 Trạng thái ca làm việc: {locators_result.get('status')}")

            # Bước 5: Chụp ảnh màn hình lưu bằng chứng tại đúng trang chấm công
            screenshot_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flow_stop_at_cham_cong.png")
            page.screenshot(path=screenshot_path, full_page=True)
            ui_print(f"📸 Đã chụp ảnh màn hình xác thực: {os.path.basename(screenshot_path)}")

            # Bước 6: DỪNG LẠI TẠI TRANG CHẤM CÔNG
            ui_print("=" * 65)
            ui_print("🛑 ĐÃ ĐẾN ĐÚNG TRANG CHẤM CÔNG VÀ DỪNG LẠI THEO YÊU CẦU.")
            ui_print("🔒 XÁC NHẬN AN TOÀN 100%: Nút chấm công KHÔNG HỀ BỊ CLICK!")
            ui_print("👀 Giữ màn hình mở trong 10 giây để quan sát trước khi kết thúc...")
            ui_print("=" * 65)
            page.wait_for_timeout(10000)

            context.close()
            ui_print("✅ KẾT THÚC TEST FLOW THÀNH CÔNG.")
            ui_print("📝 Toàn bộ log kỹ thuật chi tiết đã được lưu trong file: debug.log")
    except Exception as e:
        logger.error(f"❌ LỖI TRONG QUÁ TRÌNH THỰC THI TEST FLOW: {e}", exc_info=True)
        ui_print(f"❌ Đã xảy ra lỗi: {e}. Vui lòng kiểm tra file debug.log")
        raise

if __name__ == "__main__":
    test_flow_to_timekeeping_page()
