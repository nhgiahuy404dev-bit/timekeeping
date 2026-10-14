"""
Automated Test Flow: Navigates to BOM BADO Timekeeping page and stops safely.
🔒 ABSOLUTE SAFETY LOCK:
- Navigates directly to https://bom.bado.vn/quan-ly/cham-cong.
- Validates URL and confirms presence of XPath locators on the page.
- STOPS HERE - NEVER CLICKS ANY TIMEKEEPING BUTTON!
"""
import os
import sys
import logging
from playwright.sync_api import sync_playwright

# Ensure imports from repository root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from url.timekeeping_page import CHAM_CONG_DIRECT_URL, CHROME_PATH
from data import LOGIN_ACCOUNT, PASSWORD
from model.locator.timekeeping_locator import LoginLocator
from model.page.timekeeping_page import TimekeepingPage

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configure logging: write all technical details to debug.log
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug.log")
handlers = [logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")]

if "--show-log" in sys.argv or "--verbose" in sys.argv:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=handlers
)
logger = logging.getLogger("TestTimekeepingFlow")

def ui_print(msg: str):
    """Outputs clear user-facing messages to terminal and records full detail to debug.log"""
    try:
        print(msg, flush=True)
    except Exception:
        try:
            print(msg.encode("ascii", errors="replace").decode("ascii"), flush=True)
        except Exception:
            pass
    logger.info(f"[UI] {msg}")

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("🚨 UNHANDLED EXCEPTION IN TEST FLOW:", exc_info=(exc_type, exc_value, exc_traceback))
    ui_print(f"❌ Error encountered: {exc_value}. Please check debug.log for details.")

sys.excepthook = handle_unhandled_exception

AUTOMATION_PROFILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "automation_profile")

def test_flow_to_timekeeping_page():
    """
    Test scenario:
    1. Launch browser (Headed mode for visual observation).
    2. Navigate to BOM BADO timekeeping page.
    3. Complete Google login if no active session exists.
    4. Verify redirection to: https://bom.bado.vn/quan-ly/cham-cong.
    5. Inspect and validate XPath elements on the timekeeping page.
    6. Stop safely - NO BUTTON CLICKS PERFORMED!
    """
    ui_print("=" * 65)
    ui_print("🚀 STARTING TEST FLOW: NAVIGATE TO TIMEKEEPING PAGE & STOP")
    ui_print("🔒 SAFETY LOCK: ZERO CLICKS ON TIMEKEEPING BUTTONS")
    ui_print("=" * 65)

    try:
        with sync_playwright() as p:
            # Launch Chrome with persistent session and disabled automation flags
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

            # Step 1: Open timekeeping URL
            ui_print(f"👉 [1/4] Navigating to URL: {CHAM_CONG_DIRECT_URL}")
            page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")
            page.wait_for_timeout(2000)

            # Step 2: Check if already authenticated
            if timekeeping_page.is_already_logged_in():
                ui_print("🎉 [2/4] Active session detected -> Skipping login!")
            else:
                ui_print("🔑 [2/4] Authentication required. Processing Google sign-in...")
                timekeeping_page.login(LOGIN_ACCOUNT, PASSWORD, CHAM_CONG_DIRECT_URL)

                ui_print("⏳ Waiting for authentication completion...")
                try:
                    page.wait_for_url(lambda u: "dang-nhap" not in u and "/quan-ly" in u, timeout=45000)
                    ui_print(f"✅ Successfully signed in: {page.url}")
                except Exception as e_nav:
                    logger.warning(f"Waiting for redirect notice: {e_nav}.")

                # Ensure navigation directly to Timekeeping page
                if "/quan-ly/cham-cong" not in page.url:
                    ui_print(f"👉 Navigating directly to timekeeping page: {CHAM_CONG_DIRECT_URL}")
                    page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")

            page.wait_for_timeout(3000)

            # Step 3: Validate current URL
            current_url = page.url
            logger.info(f"Step 3: URL validation: {current_url}")
            assert "dang-nhap" not in current_url and "/quan-ly/cham-cong" in current_url, (
                f"🚨 ERROR: Not on timekeeping page! Current URL: {current_url}. "
                f"Please ensure authentication completed in browser."
            )
            ui_print("✅ [3/4] Verified: Reached Timekeeping page successfully!")

            # Step 4: Scan XPath elements on timekeeping page
            ui_print("🔍 [4/4] Scanning XPath locators and work shift state (Safe Mode)...")
            locators_result = timekeeping_page.inspect_and_get_locators()
            ui_print(f"📊 Work shift status: {locators_result.get('status')}")

            # Step 5: Capture verification screenshot
            screenshot_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flow_stop_at_cham_cong.png")
            page.screenshot(path=screenshot_path, full_page=True)
            ui_print(f"📸 Verification screenshot saved: {os.path.basename(screenshot_path)}")

            # Step 6: Safe Stop
            ui_print("=" * 65)
            ui_print("🛑 REACHED TIMEKEEPING PAGE AND STOPPED AS INTENDED.")
            ui_print("🔒 100% SAFETY CONFIRMATION: Timekeeping button was NOT clicked!")
            ui_print("👀 Keeping window open for 10 seconds for visual confirmation...")
            ui_print("=" * 65)
            page.wait_for_timeout(10000)

            context.close()
            ui_print("✅ TEST FLOW COMPLETED SUCCESSFULLY.")
            ui_print("📝 Full technical logs recorded in: debug.log")
    except Exception as e:
        logger.error(f"❌ Error during test flow execution: {e}", exc_info=True)
        ui_print(f"❌ Error encountered: {e}. Check debug.log for full details.")
        raise

if __name__ == "__main__":
    test_flow_to_timekeeping_page()
