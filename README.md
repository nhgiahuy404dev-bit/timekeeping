# Hệ Thống Automation Chấm Công Tự Động (BOM BADO)

Hệ thống tự động hóa chấm công cho tài khoản công ty BOM BADO sử dụng **Playwright** và mô hình **Page Object Model (POM)** với **100% Locator thuần XPath**.

---

## 🔒 NGUYÊN TẮC AN TOÀN TUYỆT ĐỐI (SAFETY LOCK)
- **Mặc định toàn bộ code chạy ở chế độ An Toàn (`dry_run=True`)**:
  - Chỉ quét DOM, kiểm tra ca làm việc, hiển thị trạng thái và lấy thông tin Locator.
  - **TUYỆT ĐỐI KHÔNG GỌI LỆNH CLICK LÊN NÚT CHẤM CÔNG** trong mọi lần chạy thử nghiệm hay kiểm thử.
- Chỉ khi đến đúng thời gian quy định (**17:45**) và chạy với cờ kích hoạt rõ ràng (`--live`), lệnh click mới được phép thực thi.

---

## 🎯 BẢNG LOCATOR THUẦN XPATH (BOM BADO)

Toàn bộ Locator trong dự án chỉ sử dụng duy nhất mã **XPath**:

### 1. Trang Chấm Công (`https://bom.bado.vn/quan-ly/cham-cong`):
| Thành phần | Mã XPath |
| :--- | :--- |
| **Nút Chấm công Ra ca (Mục tiêu 17h45)** | `//button[contains(., 'Bắt đầu chấm công ra')]` |
| **Nút Chấm công Ra ca (qua thẻ span)** | `//span[text()='Bắt đầu chấm công ra']/ancestor::button` |
| **Nút Chấm công Vào ca** | `//button[contains(., 'Bắt đầu chấm công vào')]` |
| **Nút Chấm công Vào ca (qua thẻ span)** | `//span[text()='Bắt đầu chấm công vào']/ancestor::button` |
| **Trạng thái: Chưa đến giờ chấm công** | `//span[text()='Chưa đến giờ chấm công']/ancestor::div[1]` |
| **Trạng thái: Đã hoàn thành ca** | `//span[text()='Đã hoàn thành ca làm việc']/ancestor::div[1]` |
| **Trạng thái: Chưa có ca làm việc** | `//span[text()='Chưa có ca làm việc']/ancestor::div[1]` |
| **Thẻ thông tin ca làm việc** | `//div[contains(@class, 'rounded-[10px]') or contains(@class, 'rounded-[12px]')]` |
| **Modal / Dialog xác nhận** | `//div[@role='dialog']` |
| **Nút Xác nhận trên modal** | `//button[contains(., 'Xác nhận') or contains(., 'Đồng ý')]` |
| **Nút Hủy trên modal** | `//button[contains(., 'Hủy') or contains(., 'Đóng')]` |

### 2. Trang Đăng Nhập (`https://bom.bado.vn/quan-ly/dang-nhap`):
| Thành phần | Mã XPath |
| :--- | :--- |
| **Nút Đăng nhập với Google** | `//button[contains(., 'Đăng nhập với Google')]` |
| **Nút Đối tác đăng nhập** | `//button[contains(., 'Đối tác đăng nhập')]` |
| **Ô nhập Tài khoản** | `//input[@placeholder='Tài khoản']` |
| **Ô nhập Mật khẩu** | `//input[@placeholder='Mật khẩu']` |
| **Nút Submit ĐĂNG NHẬP** | `//button[contains(@class, 'admin-submit-btn-custom') or normalize-space()='ĐĂNG NHẬP']` |

---

## 📁 Cấu Trúc Dự Án

```
d:/Workspace/timekeeping/
├── data/
│   ├── __init__.py
│   ├── credentials.py            # Lưu thông tin tài khoản đăng nhập
│   └── pass.py                   # Alias kết nối credentials
├── url/
│   └── timekeeping_page.py       # Cấu hình URL, Chrome Path, giờ hẹn 17:45
├── model/
│   ├── locator/
│   │   ├── __init__.py
│   │   └── timekeeping_locator.py # 100% Locator thuần XPath
│   └── page/
│       ├── __init__.py
│       ├── base_page.py           # BasePage với Playwright utils
│       └── timekeeping_page.py    # POM xử lý trang chấm công với khóa an toàn
├── test/
│   └── test_locators.py           # Unit tests kiểm thử cú pháp XPath và khóa dry-run
├── view_timekeeping_live.py       # Mở trực quan có giao diện để quan sát (Không click)
├── schedule_timekeeping.py        # Hẹn giờ chạy tự động lúc 17:45
└── README.md
```

---

## 🚀 Hướng Dẫn Sử Dụng

1. **Mở trình duyệt trực quan trên màn hình để kiểm tra Locator (Không click):**
   ```bash
   python view_timekeeping_live.py
   ```

2. **Chạy kiểm thử cú pháp XPath (Pytest):**
   ```bash
   python -m pytest test/test_locators.py -v
   ```

3. **Chạy tiến trình hẹn giờ lúc 17h45:**
   - *Mặc định (Chế độ An toàn - KHÔNG bấm nút):*
     ```bash
     python schedule_timekeeping.py
     ```
   - *Chế độ thực thi thật (Chỉ bật khi muốn hệ thống tự bấm lúc 17:45):*
     ```bash
     python schedule_timekeeping.py --live
     ```
