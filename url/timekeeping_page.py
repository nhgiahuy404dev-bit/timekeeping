import os

# Đường dẫn trang đăng nhập và chấm công BOM BADO
TIMEKEEPING_URL = "https://bom.bado.vn/quan-ly/dang-nhap?returnUrl=%2Fquan-ly%2Fcham-cong"
CHAM_CONG_DIRECT_URL = "https://bom.bado.vn/quan-ly/cham-cong"

# Cấu hình Chrome Profile để dùng cookie/phiên làm việc sẵn có nếu cần
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_NAME = "Profile 10"
USER_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

# Thời gian thực hiện chấm công hàng ngày
TARGET_TIME = "17:45"