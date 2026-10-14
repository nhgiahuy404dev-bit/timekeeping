.PHONY: help install inspect inspect-headless test schedule schedule-live clean

help:
	@echo ================================================================
	@echo          AUTOMATION CHẤM CÔNG BOM BADO (MAKEFILE)
	@echo ================================================================
	@echo   make install          - Cài đặt thư viện và Playwright Chromium
	@echo   make inspect          - Mở trình duyệt xem trực quan Locator (Safe Mode)
	@echo   make inspect-headless - Quét Locator ở chế độ chạy ngầm
	@echo   make test             - Chạy unit test kiểm tra cú pháp XPath
	@echo   make test-flow        - Chạy test flow đến đúng trang chấm công rồi DỪNG
	@echo   make schedule         - Bật hẹn giờ 17h45 (An toàn - Dry Run, không bấm nút)
	@echo   make schedule-live    - Bật hẹn giờ 17h45 (Thực thi click thật)
	@echo   make clean            - Dọn dẹp cache và file tạm
	@echo ================================================================

install:
	python -m pip install -r requirements.txt
	python -m playwright install chromium

inspect:
	python view_timekeeping_live.py

inspect-headless:
	python inspect_locators.py --headless

test:
	python -m pytest test/test_locators.py -v

test-flow:
	python test/test_timekeeping_flow.py

schedule:
	python schedule_timekeeping.py

schedule-live:
	python schedule_timekeeping.py --live

clean:
	powershell -Command "Remove-Item -Path '*.png', '*.html', '*.log', '.pytest_cache' -Recurse -Force -ErrorAction SilentlyContinue"
