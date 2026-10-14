#!/usr/bin/env bash
# ==============================================================================
# Script điều khiển Automation Chấm Công BOM BADO
# ==============================================================================

set -e

# Đổi thư mục làm việc về thư mục chứa script
cd "$(dirname "$0")"

show_menu() {
    echo "================================================================="
    echo "         HỆ THỐNG AUTOMATION CHẤM CÔNG BOM BADO"
    echo "================================================================="
    echo "  1) Mở trình duyệt xem trực quan Locator (Safe Mode - Không Click)"
    echo "  2) Chạy kiểm thử cú pháp XPath (Pytest)"
    echo "  3) Chạy Test Flow: Đến đúng trang chấm công rồi DỪNG"
    echo "  4) Bật hẹn giờ 17h45 (Chế độ An toàn - KHÔNG bấm nút)"
    echo "  5) Bật hẹn giờ 17h45 (Chế độ Thực thi thật - Click lúc 17h45)"
    echo "  6) Cài đặt thư viện (Playwright & dependencies)"
    echo "  7) Thoát"
    echo "================================================================="
    read -p "Vui lòng chọn thao tác (1-7): " choice

    case "$choice" in
        1)
            echo "🚀 Đang mở trình duyệt trực quan để bạn quan sát Locator..."
            python view_timekeeping_live.py
            ;;
        2)
            echo "🧪 Đang chạy kiểm thử XPath..."
            python -m pytest test/test_locators.py -v
            ;;
        3)
            echo "🛑 Đang chạy test flow đến đúng trang chấm công rồi DỪNG..."
            python test/test_timekeeping_flow.py
            ;;
        4)
            echo "⏰ Đang khởi động tiến trình hẹn giờ 17:45 (CHẾ ĐỘ AN TOÀN)..."
            python schedule_timekeeping.py
            ;;
        5)
            echo "⚠️ Đang khởi động hẹn giờ 17:45 (CHẾ ĐỘ THỰC THI THẬT)..."
            python schedule_timekeeping.py --live
            ;;
        6)
            echo "📦 Đang cài đặt thư viện..."
            python -m pip install -r requirements.txt
            python -m playwright install chromium
            ;;
        7)
            echo "Tạm biệt!"
            exit 0
            ;;
        *)
            echo "Lựa chọn không hợp lệ!"
            exit 1
            ;;
    esac
}

# Nếu có truyền tham số dòng lệnh
if [ $# -gt 0 ]; then
    case "$1" in
        inspect)
            python view_timekeeping_live.py
            ;;
        inspect-headless)
            python inspect_locators.py --headless
            ;;
        test)
            python -m pytest test/test_locators.py -v
            ;;
        test-flow|flow)
            python test/test_timekeeping_flow.py
            ;;
        schedule)
            python schedule_timekeeping.py
            ;;
        schedule-live|live)
            python schedule_timekeeping.py --live
            ;;
        install)
            python -m pip install -r requirements.txt
            python -m playwright install chromium
            ;;
        *)
            echo "Lệnh không hợp lệ: $1"
            echo "Cách dùng: ./run.sh [inspect | test | schedule | schedule-live | install]"
            exit 1
            ;;
    esac
else
    show_menu
fi
