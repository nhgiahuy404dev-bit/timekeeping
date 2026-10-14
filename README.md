# BOM BADO Automated Timekeeping System

Automated attendance check-out system for BOM BADO (`https://bom.bado.vn`) built with **Playwright**, **Page Object Model (POM)**, and **100% pure XPath locators**.

---

## 🛡️ Ironclad 6-Layer Safety Shield

To guarantee absolute safety against accidental or premature clicks:

1. **Premature Click Time Lock**:
   - The check-out button is strictly locked until scheduled time (**17:45**).
   - If executed early (e.g. at 15:35), the system alerts `"NOT YET TIME FOR TIMEKEEPING!"`, keeps the button 100% locked, and stands by waiting for 17:45.
2. **Once-Per-Day Execution Guard**:
   - The routine only executes once per calendar day.
   - Once check-out succeeds on a day, all subsequent click attempts are blocked to prevent duplicate submissions.
3. **Dry-Run Safety Lock**:
   - In test/safe mode (`dry_run=True`), the system never triggers `.click()` on any timekeeping button.
4. **URL & Domain Verification Guard**:
   - Enforces that the browser must strictly reside at `https://bom.bado.vn/quan-ly/cham-cong`.
5. **Work Shift State Guard**:
   - Validates that the work shift is not already marked completed, not upcoming, and actually ready for check-out before touching the element.
6. **Error Isolation**:
   - If any exception or network error occurs during navigation or sign-in, the routine immediately stops without touching the timekeeping button.

---

## 🎯 Pure XPath Locators Table

All locators strictly use 100% pure XPath syntax (`//` or `(//`):

### 1. Timekeeping Page (`https://bom.bado.vn/quan-ly/cham-cong`):
| Element | XPath Locator |
| :--- | :--- |
| **Check-out Button (17:45 Target)** | `//button[contains(., 'Bắt đầu chấm công ra')]` |
| **Check-out Button (via span ancestor)** | `//span[text()='Bắt đầu chấm công ra']/ancestor::button` |
| **Check-in Button** | `//button[contains(., 'Bắt đầu chấm công vào')]` |
| **Check-in Button (via span ancestor)** | `//span[text()='Bắt đầu chấm công vào']/ancestor::button` |
| **Status: Not Yet Time** | `//span[text()='Chưa đến giờ chấm công']/ancestor::div[1]` |
| **Status: Shift Completed** | `//span[text()='Đã hoàn thành ca làm việc']/ancestor::div[1]` |
| **Status: No Shift Assigned** | `//span[text()='Chưa có ca làm việc']/ancestor::div[1]` |
| **Work Shift Card** | `//div[contains(@class, 'rounded-[10px]') or contains(@class, 'rounded-[12px]')]` |
| **Confirmation Modal** | `//div[@role='dialog']` |
| **Modal Confirm Button** | `//button[contains(., 'Xác nhận') or contains(., 'Đồng ý')]` |
| **Modal Cancel Button** | `//button[contains(., 'Hủy') or contains(., 'Đóng')]` |

### 2. Login Page & Google OAuth (`https://bom.bado.vn/quan-ly/dang-nhap`):
| Element | XPath Locator |
| :--- | :--- |
| **Google Sign-in Button** | `(//button[contains(., 'Đăng nhập với Google')])[last()]` |
| **Use Another Account Button** | `(//*[normalize-space()='Use another account' or normalize-space()='Sử dụng một tài khoản khác'] \| //*[@role='link' or @role='button' or self::li][contains(., 'Use another account') or contains(., 'Sử dụng một tài khoản khác')])[1]` |
| **Google Email Input** | `//input[@type='email' or @id='identifierId']` |
| **Google Password Input** | `//input[@type='password' or @name='Passwd' or @name='password']` |
| **Partner Login Button** | `//button[contains(., 'Đối tác đăng nhập')]` |
| **Username Input** | `//input[@placeholder='Tài khoản']` |
| **Password Input** | `//input[@placeholder='Mật khẩu']` |
| **Submit Login Button** | `//button[contains(@class, 'admin-submit-btn-custom') or normalize-space()='ĐĂNG NHẬP']` |

---

## 📁 Project Structure

```
d:/Workspace/timekeeping/
├── data/
│   ├── __init__.py
│   └── credentials.py            # User credentials
├── url/
│   ├── __init__.py
│   └── timekeeping_page.py       # URL constants, Chrome executable path, target time (17:45)
├── model/
│   ├── locator/
│   │   ├── __init__.py
│   │   └── timekeeping_locator.py # 100% pure XPath locators
│   └── page/
│       ├── __init__.py
│       ├── base_page.py           # BasePage with Playwright utilities
│       └── timekeeping_page.py    # POM with 6-layer Safety Guards
├── test/
│   ├── test_locators.py           # Unit tests for XPath syntax & Safety Shields
│   └── test_timekeeping_flow.py   # Safe test flow (stops at timekeeping page without clicking)
├── schedule_timekeeping.py        # Automated daily scheduler (17:45) with Safety Shield
├── run                            # Direct execution wrapper (./run)
├── run.sh                         # Bash execution script (./run.sh)
├── run.bat                        # Windows execution script (run.bat)
├── Makefile                       # Quick make tasks
└── README.md
```

---

## 🚀 How to Run

### Daily Automation (One-click):
```bash
./run
# Or in Windows Command Prompt:
run.bat
```
- If executed before 17:45: Displays prominent `"NOT YET TIME FOR TIMEKEEPING!"` alert, locks button, and waits.
- At 17:45: Automatically opens Chrome, signs in, and performs check-out once.
- If already checked out today: Notifies user that today's check-out is complete and keeps button locked.

### Testing & Verification:
```bash
# Safe test flow (navigates to timekeeping page and stops without clicking)
python test/test_timekeeping_flow.py

# Unit tests for pure XPath syntax and safety shields
python -m pytest test/test_locators.py -v
```
