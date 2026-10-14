"""
Page Object Model for BOM BADO Timekeeping and Authentication.
Includes multi-layered safety guards:
- Dry-run absolute lock
- Once-per-day execution limit
- Time-window lock (prevents premature clicks before 17:45)
- Shift state & page URL validation
"""
import os
import json
import logging
from datetime import datetime
from playwright.sync_api import Page
from model.page.base_page import BasePage
from model.locator.timekeeping_locator import LoginLocator, TimekeepingLocator
from url.timekeeping_page import TARGET_TIME, CHAM_CONG_DIRECT_URL

logger = logging.getLogger("TimekeepingPage")

# State file to track once-per-day execution status
STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".attendance_state.json"
)

def is_checked_out_today() -> bool:
    """Check if attendance checkout has already succeeded for today's calendar date"""
    if not os.path.exists(STATE_FILE):
        return False
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        today_str = datetime.now().strftime("%Y-%m-%d")
        return data.get(today_str, {}).get("status") == "SUCCESS"
    except Exception as e:
        logger.warning(f"Failed to read attendance state file: {e}")
        return False

def record_checkout_today(status: str = "SUCCESS", details: dict = None):
    """Record checkout execution record for today to prevent duplicate runs"""
    try:
        data = {}
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        today_str = datetime.now().strftime("%Y-%m-%d")
        data[today_str] = {
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": details or {}
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save attendance state: {e}")


class TimekeepingPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.login_locators = LoginLocator()
        self.timekeeping_locators = TimekeepingLocator()

    def is_already_logged_in(self) -> bool:
        """
        Verify if browser session is currently authenticated and on timekeeping page.
        If valid session exists, skip login procedure entirely.
        """
        current_url = self.page.url
        if "dang-nhap" not in current_url and "cham-cong" in current_url:
            return True

        shift_indicators = [
            TimekeepingLocator.CHECKOUT_BUTTON,
            TimekeepingLocator.CHECKIN_BUTTON,
            TimekeepingLocator.BTN_UPCOMING,
            TimekeepingLocator.BTN_COMPLETED,
            TimekeepingLocator.BTN_NO_SHIFT
        ]
        for xpath in shift_indicators:
            try:
                if self.page.locator(xpath).first.is_visible(timeout=500):
                    return True
            except Exception:
                pass
        return False

    def login(self, username: str, password: str, login_url: str):
        """
        Navigate to login page and perform Google OAuth authentication.
        If session is already active, bypasses authentication.
        """
        if self.is_already_logged_in():
            logger.info("Session already active and on timekeeping page. Skipping login.")
            return True

        logger.info(f"Opening login URL: {login_url}")
        self.page.goto(login_url, wait_until="networkidle")
        self.page.wait_for_timeout(2000)

        if self.is_already_logged_in():
            logger.info("Session recognized automatically. Skipping login.")
            return True

        # Check for Google login button
        google_btn = self.page.locator(LoginLocator.GOOGLE_LOGIN_BUTTON).first
        if google_btn.is_visible(timeout=5000):
            logger.info("Detected Google login button. Opening popup...")
            try:
                with self.page.expect_popup(timeout=10000) as popup_info:
                    google_btn.click()
                popup = popup_info.value
                logger.info("Google OAuth popup opened.")

                # Wait for popup to reach accounts.google.com
                try:
                    if "accounts.google.com" not in popup.url:
                        popup.wait_for_url(lambda u: "accounts.google.com" in u, timeout=20000)
                    logger.info(f"Popup reached Google Accounts: {popup.url}")
                except Exception as e_url:
                    logger.warning(f"Waiting for accounts.google.com: {e_url}")

                popup.wait_for_load_state("domcontentloaded")
                popup.wait_for_timeout(1500)

                # Step 1: Priority - Check and click 'Use another account' first
                clicked_use_another = False
                use_another_el = popup.locator(LoginLocator.GOOGLE_USE_ANOTHER_ACCOUNT_BTN).first
                try:
                    if use_another_el.is_visible(timeout=3000):
                        logger.info("Detected 'Use another account' option. Clicking first as requested...")
                        use_another_el.scroll_into_view_if_needed()
                        try:
                            use_another_el.click(timeout=3000)
                        except Exception:
                            use_another_el.click(force=True)
                        clicked_use_another = True
                        logger.info("Clicked 'Use another account' successfully. Waiting for email input...")
                        popup.wait_for_timeout(1500)
                except Exception as e_ua:
                    logger.debug(f"Checking 'Use another account': {e_ua}")

                # Step 1b: Fallback - If 'Use another account' was not clicked, check account chooser list
                if not clicked_use_another and not popup.is_closed():
                    email_input_check = popup.locator(LoginLocator.GOOGLE_EMAIL_INPUT).first
                    if not email_input_check.is_visible(timeout=1000):
                        account_xpath = LoginLocator.get_google_account_xpath(username)
                        account_el = popup.locator(account_xpath).first
                        try:
                            if account_el.is_visible(timeout=2000):
                                logger.info(f"Selecting account {username} from account chooser list...")
                                account_el.scroll_into_view_if_needed()
                                try:
                                    account_el.click(timeout=3000)
                                except Exception:
                                    account_el.click(force=True)
                                logger.info(f"Selected account {username}.")
                                popup.wait_for_timeout(2000)
                        except Exception:
                            pass

                if popup.is_closed():
                    logger.info("Google popup closed automatically (authentication successful).")

                # Step 2: Fill Email input
                if not popup.is_closed():
                    email_input = popup.locator(LoginLocator.GOOGLE_EMAIL_INPUT).first
                    try:
                        if email_input.is_visible(timeout=4000):
                            logger.info(f"Filling email: {username}")
                            email_input.fill(username)
                            popup.wait_for_timeout(500)
                            email_input.press("Enter")
                            popup.wait_for_timeout(1500)

                            next_btn = popup.locator(LoginLocator.GOOGLE_EMAIL_NEXT_BTN).first
                            if next_btn.is_visible(timeout=1500):
                                try:
                                    next_btn.click()
                                except Exception:
                                    pass
                    except Exception as e_em:
                        logger.debug(f"Handling email input: {e_em}")

                # Step 3: Fill Password input
                if not popup.is_closed():
                    pass_input = popup.locator(LoginLocator.GOOGLE_PASSWORD_INPUT).first
                    try:
                        pass_input.wait_for(state="visible", timeout=8000)
                        logger.info("Filling Google account password...")
                        pass_input.fill(password)
                        popup.wait_for_timeout(500)
                        pass_input.press("Enter")
                        popup.wait_for_timeout(1500)

                        pass_next_btn = popup.locator(LoginLocator.GOOGLE_PASSWORD_NEXT_BTN).first
                        if pass_next_btn.is_visible(timeout=1500):
                            try:
                                pass_next_btn.click()
                            except Exception:
                                pass
                    except Exception as e_pw:
                        logger.debug(f"Handling password input: {e_pw}")

                # Step 4: Wait for popup to close
                if not popup.is_closed():
                    logger.info("Waiting for Google authentication to finish (approve 2FA on mobile if prompted)...")
                    try:
                        popup.wait_for_event("close", timeout=60000)
                        logger.info("Google popup closed successfully.")
                    except Exception:
                        logger.info("Popup did not close or processing completed.")

                # Wait for main page to redirect to dashboard / management area
                try:
                    self.page.wait_for_url(lambda u: "dang-nhap" not in u and "/quan-ly" in u, timeout=20000)
                    logger.info(f"Main page navigated: {self.page.url}")
                except Exception:
                    pass

            except Exception as e:
                logger.error(f"Google login flow notice: {e}", exc_info=True)
            return

        # Alternative Partner Login form
        partner_btn = self.page.locator(LoginLocator.PARTNER_LOGIN_BUTTON).first
        if partner_btn.is_visible(timeout=2000):
            logger.info("Opening partner login form...")
            partner_btn.click()
            self.page.wait_for_timeout(1000)

        user_input = self.page.locator(LoginLocator.USERNAME_INPUT).first
        pass_input = self.page.locator(LoginLocator.PASSWORD_INPUT).first
        submit_btn = self.page.locator(LoginLocator.LOGIN_SUBMIT_BUTTON).first

        if user_input.is_visible(timeout=2000):
            logger.info(f"Submitting credentials for {username}...")
            user_input.fill(username)
            pass_input.fill(password)
            submit_btn.click()
            self.page.wait_for_load_state("networkidle")

    def inspect_and_get_locators(self) -> dict:
        """
        Inspect and extract locators on the timekeeping page.
        READ-ONLY AND HIGHLIGHT MODE: NEVER CLICKS ANY BUTTON.
        """
        logger.info("=" * 60)
        logger.info("INSPECTING TIMEKEEPING LOCATORS (SAFE READ-ONLY MODE)")
        logger.info("=" * 60)

        locators_info = {
            "current_url": self.page.url,
            "status": "UNKNOWN",
            "locators": {}
        }

        # 1. Checkout button inspection
        checkout_el = self.page.locator(TimekeepingLocator.CHECKOUT_BUTTON).first
        if checkout_el.is_visible(timeout=2000):
            locators_info["status"] = "IN_PROGRESS (Shift active - Ready for checkout)"
            locators_info["locators"]["checkout_button"] = {
                "name": "Check-out Button",
                "selector": TimekeepingLocator.CHECKOUT_BUTTON,
                "text": checkout_el.inner_text().strip(),
                "enabled": checkout_el.is_enabled()
            }
            logger.info("[LOCATOR FOUND] 'Bắt đầu chấm công ra' button is visible.")
            try:
                checkout_el.highlight()
                logger.info("Highlighted checkout button on screen.")
            except Exception:
                pass

        # 2. Check-in button inspection
        checkin_el = self.page.locator(TimekeepingLocator.CHECKIN_BUTTON).first
        if checkin_el.is_visible(timeout=1000):
            locators_info["status"] = "READY (Ready for check-in)"
            locators_info["locators"]["checkin_button"] = {
                "name": "Check-in Button",
                "selector": TimekeepingLocator.CHECKIN_BUTTON,
                "text": checkin_el.inner_text().strip(),
                "enabled": checkin_el.is_enabled()
            }
            logger.info("[LOCATOR FOUND] 'Bắt đầu chấm công vào' button is visible.")
            try:
                checkin_el.highlight()
            except Exception:
                pass

        # 3. Shift status indicators
        upcoming_el = self.page.locator(TimekeepingLocator.BTN_UPCOMING).first
        if upcoming_el.is_visible(timeout=1000):
            locators_info["status"] = "UPCOMING (Shift not yet open for timekeeping)"
            locators_info["locators"]["upcoming_indicator"] = {
                "name": "Chưa đến giờ chấm công",
                "selector": TimekeepingLocator.BTN_UPCOMING
            }
            logger.info("[STATUS] Work shift: Not yet time.")

        completed_el = self.page.locator(TimekeepingLocator.BTN_COMPLETED).first
        if completed_el.is_visible(timeout=1000):
            locators_info["status"] = "COMPLETED (Work shift finished)"
            locators_info["locators"]["completed_indicator"] = {
                "name": "Đã hoàn thành ca làm việc",
                "selector": TimekeepingLocator.BTN_COMPLETED
            }
            logger.info("[STATUS] Work shift: Completed.")

        no_shift_el = self.page.locator(TimekeepingLocator.BTN_NO_SHIFT).first
        if no_shift_el.is_visible(timeout=1000):
            locators_info["status"] = "NO_SHIFT (No work shift assigned)"
            locators_info["locators"]["no_shift_indicator"] = {
                "name": "Chưa có ca làm việc",
                "selector": TimekeepingLocator.BTN_NO_SHIFT
            }
            logger.info("[STATUS] No work shift scheduled for today.")

        logger.info(f"Inspection summary: {locators_info['status']}")
        logger.info("=" * 60)
        return locators_info

    def execute_timekeeping(
        self,
        action: str = "checkout",
        dry_run: bool = True,
        force_time: bool = False
    ) -> dict:
        """
        Executes timekeeping action protected by 6-LAYER SAFETY GUARDS:
        1. Dry-run safety lock: Never clicks if dry_run=True.
        2. Once-per-day lock: Prevents duplicate execution on the same date.
        3. Time-window guard: Prevents premature clicking before target time (17:45).
        4. Page URL verification: Ensures browser is strictly on /quan-ly/cham-cong.
        5. Shift state validation: Checks if shift is completed, upcoming, or missing.
        6. Safe execution & Confirmation modal handler.
        """
        # ======================================================================
        # GUARD LAYER 1: ABSOLUTE DRY-RUN SAFETY LOCK
        # ======================================================================
        if dry_run:
            logger.warning("=" * 60)
            logger.warning("🔒 [SAFETY GUARD 1] DRY-RUN LOCK ACTIVE: BUTTON CLICK PREVENTED!")
            logger.warning(f"Action '{action}' was securely skipped.")
            logger.warning("=" * 60)
            return {"status": "SKIPPED_CLICK", "dry_run": True, "action": action}

        # ======================================================================
        # GUARD LAYER 2: ONCE-PER-DAY SAFETY LOCK
        # ======================================================================
        if is_checked_out_today():
            today_str = datetime.now().strftime("%Y-%m-%d")
            logger.warning("=" * 60)
            logger.warning(f"🛡️ [SAFETY GUARD 2] ONCE-PER-DAY LOCK: Already checked out today ({today_str})!")
            logger.warning("Aborting execution to prevent duplicate checkout.")
            logger.warning("=" * 60)
            return {"status": "ALREADY_CHECKED_OUT_TODAY", "dry_run": False}

        # ======================================================================
        # GUARD LAYER 3: TIME-WINDOW GUARD (Prevents premature clicks before 17:45)
        # ======================================================================
        if not force_time:
            now = datetime.now()
            t_hour, t_min = map(int, TARGET_TIME.split(":"))
            scheduled_target = now.replace(hour=t_hour, minute=t_min, second=0, microsecond=0)
            if now < scheduled_target:
                logger.error("=" * 60)
                logger.error(
                    f"🛡️ [SAFETY GUARD 3] TIME-WINDOW LOCK: Current time {now.strftime('%H:%M:%S')} "
                    f"is BEFORE scheduled time {TARGET_TIME}!"
                )
                logger.error("Click rejected by safety shield.")
                logger.error("=" * 60)
                return {
                    "status": "BLOCKED_BY_TIME_GUARD",
                    "reason": f"Current time ({now.strftime('%H:%M')}) is before target ({TARGET_TIME})",
                    "dry_run": False
                }

        # ======================================================================
        # GUARD LAYER 4: PAGE URL & AUTHENTICATION VALIDATION
        # ======================================================================
        current_url = getattr(self.page, "url", "")
        if "dang-nhap" in current_url or "/quan-ly/cham-cong" not in current_url:
            logger.error(f"🛡️ [SAFETY GUARD 4] URL MISMATCH: Current URL '{current_url}' is not timekeeping page!")
            return {"status": "INVALID_PAGE_URL", "url": current_url, "dry_run": False}

        # ======================================================================
        # GUARD LAYER 5: SHIFT STATE VALIDATION
        # ======================================================================
        completed_el = self.page.locator(TimekeepingLocator.BTN_COMPLETED).first
        if completed_el.is_visible(timeout=1500):
            logger.info("🛡️ [SAFETY GUARD 5] Work shift is already completed. Skipping click.")
            record_checkout_today(status="SUCCESS", details={"note": "Shift already completed on page"})
            return {"status": "ALREADY_COMPLETED", "dry_run": False}

        upcoming_el = self.page.locator(TimekeepingLocator.BTN_UPCOMING).first
        if upcoming_el.is_visible(timeout=1500):
            logger.warning("🛡️ [SAFETY GUARD 5] Work shift not yet open for timekeeping.")
            return {"status": "NOT_YET_TIME", "dry_run": False}

        no_shift_el = self.page.locator(TimekeepingLocator.BTN_NO_SHIFT).first
        if no_shift_el.is_visible(timeout=1500):
            logger.warning("🛡️ [SAFETY GUARD 5] No work shift assigned for today.")
            return {"status": "NO_SHIFT", "dry_run": False}

        # ======================================================================
        # GUARD LAYER 6: SAFE CLICK EXECUTION & CONFIRMATION HANDLER
        # ======================================================================
        logger.info(f"Executing timekeeping action: {action}...")
        if action == "checkout":
            btn = self.page.locator(TimekeepingLocator.CHECKOUT_BUTTON).first
            if not btn.is_visible(timeout=5000):
                btn = self.page.locator(TimekeepingLocator.CHECKOUT_BUTTON_SPAN).first

            if btn.is_visible(timeout=5000) and btn.is_enabled():
                logger.info("Found checkout button. Proceeding with click...")
                try:
                    btn.click(timeout=5000)
                except Exception:
                    btn.click(force=True)
                logger.info("Checkout button clicked.")
                self.page.wait_for_timeout(1500)

                # Handle confirmation popup if displayed
                confirm_btn = self.page.locator(TimekeepingLocator.CONFIRM_BUTTON).first
                try:
                    if confirm_btn.is_visible(timeout=4000):
                        logger.info("Confirmation dialog detected. Clicking 'Xác nhận'...")
                        confirm_btn.click()
                        logger.info("Confirmation confirmed.")
                        self.page.wait_for_timeout(1500)
                except Exception:
                    pass

                # Record success to ensure once-per-day rule
                record_checkout_today(status="SUCCESS", details={"action": "checkout"})
                return {"status": "SUCCESS", "dry_run": False}
            else:
                logger.warning("Checkout button is not currently clickable or visible.")
                return {"status": "BUTTON_NOT_FOUND", "dry_run": False}

        elif action == "checkin":
            btn = self.page.locator(TimekeepingLocator.CHECKIN_BUTTON).first
            if not btn.is_visible(timeout=5000):
                btn = self.page.locator(TimekeepingLocator.CHECKIN_BUTTON_SPAN).first
            if btn.is_visible(timeout=5000) and btn.is_enabled():
                btn.click()
                logger.info("Check-in button clicked.")
                self.page.wait_for_timeout(1500)
                confirm_btn = self.page.locator(TimekeepingLocator.CONFIRM_BUTTON).first
                try:
                    if confirm_btn.is_visible(timeout=4000):
                        confirm_btn.click()
                except Exception:
                    pass
                return {"status": "SUCCESS", "dry_run": False}
            return {"status": "CHECKIN_BUTTON_NOT_FOUND", "dry_run": False}
