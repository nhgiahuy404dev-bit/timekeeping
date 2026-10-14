.PHONY: help install run test test-flow clean

help:
	@echo ================================================================
	@echo          BOM BADO TIMEKEEPING AUTOMATION (MAKEFILE)
	@echo ================================================================
	@echo   make run       - Run automated timekeeping with Safety Shield
	@echo   make test      - Run XPath and Safety Guard unit tests
	@echo   make test-flow - Run safe test flow (stops at timekeeping page)
	@echo   make install   - Install required dependencies and Playwright
	@echo   make clean     - Clean cache and temporary files
	@echo ================================================================

run:
	python schedule_timekeeping.py

test:
	python -m pytest test/test_locators.py -v

test-flow:
	python test/test_timekeeping_flow.py

install:
	python -m pip install -r requirements.txt
	python -m playwright install chromium

clean:
	powershell -Command "Remove-Item -Path '*.png', '*.html', '*.log', '.pytest_cache' -Recurse -Force -ErrorAction SilentlyContinue"
