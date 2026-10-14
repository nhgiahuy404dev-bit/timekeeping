"""
BasePage cung cấp các hàm tiện ích chung cho toàn bộ các trang Playwright POM.
"""
import logging
from playwright.sync_api import Page, Locator

logger = logging.getLogger("TimekeepingAutomation")

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str, wait_until: str = "networkidle"):
        logger.info(f"Đang điều hướng đến: {url}")
        self.page.goto(url, wait_until=wait_until)

    def find(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def wait_for_visible(self, selector: str, timeout: int = 10000) -> Locator:
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text().strip()

    def screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True)
        logger.info(f"Đã chụp ảnh màn hình lưu tại: {path}")
