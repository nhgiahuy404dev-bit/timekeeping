"""
Automated Daily Timekeeping Scheduler for BOM BADO (Target: 17:45).
Includes Ironclad Safety Shield against premature or accidental button clicks.
Only runs once per calendar day.
"""
import sys
import os
import time
import logging
import schedule
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from url.timekeeping_page import CHAM_CONG_DIRECT_URL, CHROME_PATH, TARGET_TIME
from data import LOGIN_ACCOUNT, PASSWORD
from model.page.timekeeping_page import TimekeepingPage, is_checked_out_today

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
    """Outputs clear messages to terminal and saves technical logs to debug.log"""
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
    logger.error("🚨 UNHANDLED EXCEPTION IN SCHEDULER:", exc_info=(exc_type, exc_value, exc_traceback))
    ui_print(f"❌ An error occurred: {exc_value}. Please check debug.log")

sys.excepthook = handle_unhandled_exception

AUTOMATION_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automation_profile")

def get_time_until_target(target_time_str: str) -> str:
    """Calculates remaining hours and minutes until scheduled target time"""
    now = datetime.now()
    t_hour, t_min = map(int, target_time_str.split(":"))
    target = now.replace(hour=t_hour, minute=t_min, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    diff = target - now
    hours, remainder = divmod(int(diff.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes:02d}m"

def is_time_reached(target_time_str: str) -> bool:
    """Returns True only if current local time is at or past target_time_str on current day"""
    now = datetime.now()
    t_hour, t_min = map(int, target_time_str.split(":"))
    target = now.replace(hour=t_hour, minute=t_min, second=0, microsecond=0)
    return now >= target

def perform_attendance_job(dry_run: bool = False, force_time: bool = False):
    """
    Executes automated attendance routine with strict multi-layer protection:
    1. Once-Per-Day Guard: Rejects execution if already checked out today.
    2. Premature Click Shield: Refuses to click if current time < TARGET_TIME.
    3. Auto-opens Chrome with persistent session.
    4. Navigates to https://bom.bado.vn/quan-ly/cham-cong.
    5. Signs in via Google OAuth (clicks 'Use another account' first) if session expired.
    6. Safely clicks checkout button and confirms dialog.
    7. Captures screenshot and records completion.
    """
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    # ======================================================================
    # SAFETY SHIELD: ONCE-PER-DAY CHECK
    # ======================================================================
    if not dry_run and is_checked_out_today():
        ui_print("=" * 65)
        ui_print("🛡️ [SAFETY SHIELD] ALREADY CHECKED OUT TODAY!")
        ui_print(f"📅 Date: {today_str}")
        ui_print("🔒 Check-out was already completed today. Button is 100% LOCKED.")
        ui_print("=" * 65)
        return {"status": "ALREADY_COMPLETED_TODAY"}

    # ======================================================================
    # SAFETY SHIELD: PREMATURE CLICK TIME GUARD
    # ======================================================================
    if not dry_run and not force_time and not is_time_reached(TARGET_TIME):
        rem = get_time_until_target(TARGET_TIME)
        ui_print("=" * 65)
        ui_print("🛡️ [SAFETY SHIELD TRIGGERED] NOT YET TIME FOR TIMEKEEPING!")
        ui_print(f"⏰ Current Time:   {now.strftime('%H:%M:%S')}")
        ui_print(f"⏰ Scheduled Time: {TARGET_TIME}:00")
        ui_print(f"⏳ Time Remaining: {rem}")
        ui_print("🔒 Check-out button is 100% PROTECTED against premature clicks.")
        ui_print("=" * 65)
        return {"status": "BLOCKED_BY_TIME_GUARD", "reason": f"Time {now.strftime('%H:%M')} < {TARGET_TIME}"}

    ui_print("")
    ui_print("=" * 65)
    ui_print(f"⏰ ACTIVATING TIMEKEEPING ROUTINE AT: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    if dry_run:
        ui_print("🔒 SAFETY MODE (dry_run=True): Button clicks are locked.")
    else:
        ui_print("⚡ EXECUTION MODE: AUTOMATED TIMEKEEPING CHECKOUT ACTIVE!")
    ui_print("=" * 65)

    try:
        with sync_playwright() as p:
            ui_print("🌐 [1/4] Launching Google Chrome browser...")
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

            # Step 1: Navigate to timekeeping URL
            ui_print(f"👉 [2/4] Navigating to: {CHAM_CONG_DIRECT_URL}")
            page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")
            page.wait_for_timeout(2000)

            # Step 2: Session validation and login
            if timekeeping_page.is_already_logged_in():
                ui_print("🎉 [3/4] Active session recognized -> Direct entry to Timekeeping page!")
            else:
                ui_print("🔑 [3/4] Authentication required. Performing automated Google sign-in...")
                timekeeping_page.login(LOGIN_ACCOUNT, PASSWORD, CHAM_CONG_DIRECT_URL)
                try:
                    page.wait_for_url(lambda u: "dang-nhap" not in u and "/quan-ly" in u, timeout=45000)
                except Exception:
                    pass

                if "/quan-ly/cham-cong" not in page.url:
                    page.goto(CHAM_CONG_DIRECT_URL, wait_until="networkidle")

            page.wait_for_timeout(3000)

            # Step 3: Execute timekeeping action with 6-layer safety guards
            ui_print("⚡ [4/4] Evaluating safety guards and executing checkout...")
            result = timekeeping_page.execute_timekeeping(
                action="checkout",
                dry_run=dry_run,
                force_time=force_time
            )

            # Step 4: Capture screenshot confirmation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            res_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"timekeeping_result_{timestamp}.png")
            page.screenshot(path=res_img, full_page=True)
            ui_print(f"📸 Verification screenshot saved: {os.path.basename(res_img)}")

            status = result.get("status")
            if status == "SUCCESS":
                ui_print("🎉 SUCCESS: Timekeeping check-out completed and confirmed!")
            elif status in ("ALREADY_COMPLETED", "ALREADY_CHECKED_OUT_TODAY"):
                ui_print("ℹ️ Shift for today was already completed.")
            elif status == "BLOCKED_BY_TIME_GUARD":
                ui_print(f"🛡️ [BLOCKED BY TIME GUARD] {result.get('reason')}")
            elif status == "SKIPPED_CLICK":
                ui_print("🔒 Button click skipped because Dry-Run safety mode is enabled.")
            else:
                ui_print(f"⚠️ Execution status: {status}")

            ui_print("👀 Keeping browser open for 6 seconds to finalize session...")
            page.wait_for_timeout(6000)
            context.close()
            ui_print("✅ Process finished successfully.")
            ui_print("=" * 65)
            return result

    except Exception as e:
        logger.error(f"❌ Error during timekeeping routine: {e}", exc_info=True)
        ui_print(f"❌ Error encountered: {e}. Check debug.log for full details.")
        return {"status": "ERROR", "message": str(e)}

def main():
    target = TARGET_TIME  # "17:45"
    now = datetime.now()

    # Safety Guard Check: Already completed today?
    if is_checked_out_today():
        ui_print("=================================================================")
        ui_print("🛡️ [SAFETY SHIELD] ALREADY CHECKED OUT TODAY!")
        ui_print("=================================================================")
        ui_print(f"📅 Date: {now.strftime('%Y-%m-%d')}")
        ui_print("🔒 SAFETY LOCK: Timekeeping checkout has ALREADY succeeded today.")
        ui_print("🛡️ The check-out button is 100% LOCKED to prevent accidental double-clicks.")
        ui_print("=================================================================")
        return

    # Check: Not yet time?
    if not is_time_reached(target):
        remaining = get_time_until_target(target)
        ui_print("=================================================================")
        ui_print("🛡️ [SAFETY SHIELD ACTIVE] NOT YET TIME FOR TIMEKEEPING!")
        ui_print("=================================================================")
        ui_print(f"⏰ Current Time:    {now.strftime('%H:%M:%S')}")
        ui_print(f"⏰ Scheduled Time:  {target}:00")
        ui_print(f"⏳ Time Remaining:  {remaining}")
        ui_print("🔒 SAFETY LOCK: Checkout button is 100% LOCKED against premature clicks.")
        ui_print("🤖 System is standing by. Chrome will auto-open and execute at exactly 17:45.")
        ui_print("💡 You may minimize this window. Press Ctrl + C to exit anytime.")
        ui_print("📝 Technical logs are recorded in: debug.log")
        ui_print("=================================================================")
    else:
        # Started after 17:45 and not yet checked out today:
        ui_print("=================================================================")
        ui_print(f"⏰ CURRENT TIME ({now.strftime('%H:%M:%S')}) IS PAST TARGET ({target})")
        ui_print("⚡ STARTING AUTOMATED CHECKOUT ROUTINE NOW...")
        ui_print("=================================================================")
        perform_attendance_job(dry_run=False, force_time=True)
        return

    # Register schedule for 17:45
    schedule.every().day.at(target).do(perform_attendance_job, dry_run=False, force_time=False)

    last_heartbeat = time.time()
    while True:
        schedule.run_pending()
        time.sleep(10)

        # Heartbeat update every 15 minutes
        if time.time() - last_heartbeat >= 900:
            last_heartbeat = time.time()
            rem = get_time_until_target(target)
            ui_print(f"⏳ [{datetime.now().strftime('%H:%M')}] Safety guard active... {rem} until {target}.")

if __name__ == "__main__":
    main()
