@echo off
chcp 65001 >nul
title BOM BADO Timekeeping Automation

cd /d "%~dp0"

:menu
cls
echo =================================================================
echo          HỆ THỐNG AUTOMATION CHẤM CÔNG BOM BADO
echo =================================================================
echo   1) Mở trình duyệt xem trực quan Locator (Safe Mode - Không Click)
echo   2) Chạy kiểm thử cú pháp XPath (Pytest)
echo   3) Chạy Test Flow: Đến đúng trang chấm công rồi DỪNG
echo   4) Bật hẹn giờ 17h45 (Chế độ An toàn - KHÔNG bấm nút)
echo   5) Bật hẹn giờ 17h45 (Chế độ Thực thi thật - Click lúc 17h45)
echo   6) Cài đặt thư viện (Playwright ^& dependencies)
echo   7) Thoát
echo =================================================================
set /p choice="Vui lòng chọn thao tác (1-7): "

if "%choice%"=="1" (
    echo 🚀 Đang mở trình duyệt trực quan để bạn quan sát Locator...
    python view_timekeeping_live.py
    pause
    goto menu
)
if "%choice%"=="2" (
    echo 🧪 Đang chạy kiểm thử XPath...
    python -m pytest test/test_locators.py -v
    pause
    goto menu
)
if "%choice%"=="3" (
    echo 🛑 Đang chạy test flow đến đúng trang chấm công rồi DỪNG...
    python test/test_timekeeping_flow.py
    pause
    goto menu
)
if "%choice%"=="4" (
    echo ⏰ Đang khởi động tiến trình hẹn giờ 17:45 (CHẾ ĐỘ AN TOÀN)...
    python schedule_timekeeping.py
    pause
    goto menu
)
if "%choice%"=="5" (
    echo ⚠️ Đang khởi động hẹn giờ 17:45 (CHẾ ĐỘ THỰC THI THẬT)...
    python schedule_timekeeping.py --live
    pause
    goto menu
)
if "%choice%"=="6" (
    echo 📦 Đang cài đặt thư viện...
    python -m pip install -r requirements.txt
    python -m playwright install chromium
    pause
    goto menu
)
if "%choice%"=="7" (
    echo Tạm biệt!
    exit /b 0
)

echo Lựa chọn không hợp lệ!
pause
goto menu
