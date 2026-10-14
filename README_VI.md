# 📘 TÀI LIỆU HƯỚNG DẪN VÀ CƠ CHẾ HOẠT ĐỘNG HỆ THỐNG AUTOMATION CHẤM CÔNG BOM BADO

Tài liệu này giải thích chi tiết, toàn diện về **kiến trúc**, **nguyên lý vận hành**, **cơ chế khiên bảo vệ an toàn 6 lớp** và **cách sử dụng hàng ngày** của hệ thống tự động hóa chấm công BOM BADO (`https://bom.bado.vn`).

---

## 📑 MỤC LỤC
1. [Mục Tiêu & Công Nghệ](#1-mục-tiêu--công-nghệ)
2. [Cơ Chế Hoạt Động Chi Tiết (Từ A - Z)](#2-cơ-chế-hoạt-động-chi-tiết-từ-a---z)
3. [Khiên Bảo Vệ An Toàn 6 Lớp (Ironclad Safety Shield)](#3-khiên-bảo-vệ-an-toàn-6-lớp-ironclad-safety-shield)
4. [Cơ Chế Tự Đăng Nhập Google Thông Minh](#4-cơ-chế-tự-đăng-nhập-google-thông-minh)
5. [Ý Nghĩa Từng File Trong Dự Án](#5-ý-nghĩa-từng-file-trong-dự-án)
6. [Bảng Tra Cứu Locator 100% XPath Thuần](#6-bảng-tra-cứu-locator-100-xpath-thuần)
7. [Hướng Dẫn Sử Dụng Hàng Ngày](#7-hướng-dẫn-sử-dụng-hàng-ngày)

---

## 1. Mục Tiêu & Công Nghệ

- **Mục tiêu**: Tự động mở máy, mở trình duyệt, điều hướng vào đúng trang Chấm công công ty BOM BADO, tự động đăng nhập (nếu hết phiên) và **tự động bấm nút "Bắt đầu chấm công ra" lúc đúng 17:45 hàng ngày**.
- **Công nghệ cốt lõi**:
  - **Python 3.12**: Ngôn ngữ lập trình chính.
  - **Playwright**: Thư viện điều khiển trình duyệt hiện đại, nhanh và ổn định hơn Selenium.
  - **Page Object Model (POM)**: Mô hình chuẩn trong kỹ nghệ kiểm thử phần mềm tự động, tách bạch giữa **Locator** (định vị phần tử) và **Action** (hành vi thực thi).
  - **100% XPath thuần**: Tất cả locator đều bắt đầu bằng `//` hoặc `(//`, tuân thủ tiêu chuẩn định danh giao diện web.
  - **Google Chrome Persistent Context**: Profile lưu trữ riêng (`automation_profile/`), không xung đột với Chrome cá nhân đang duyệt web.

---

## 2. Cơ Chế Hoạt Động Chi Tiết (Từ A - Z)

Quy trình tự động hóa diễn ra theo sơ đồ các bước sau:

```
[Bật ./run hoặc run.bat]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ BƯỚC 1: KIỂM TRA KHÓA AN TOÀN TRƯỚC GIỜ HẸN (17:45)    │
│ - Đã chấm công hôm nay chưa?                           │
│   -> Nếu ĐÃ CHẤM RỒI: Khóa nút, thông báo và dừng.     │
│ - Chưa tới 17:45? (Ví dụ đang là 15:30)                │
│   -> Khóa cứng nút 100%, bật thông báo "Chưa tới giờ", │
│      hiển thị đồng hồ đếm ngược và đứng chờ.           │
└────────────────────────────────────────────────────────┘
          │ (Đến đúng 17:45)
          ▼
┌────────────────────────────────────────────────────────┐
│ BƯỚC 2: TỰ ĐỘNG KHỞI ĐỘNG GOOGLE CHROME                │
│ - Mở Chrome với profile riêng biệt (automation_profile)│
│ - Tắt cờ automation để tránh Google chặn bot.          │
│ - Mở URL: https://bom.bado.vn/quan-ly/cham-cong        │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ BƯỚC 3: KIỂM TRA PHIÊN ĐĂNG NHẬP                       │
│ - Đã có session sẵn -> Vào thẳng trang Chấm Công.      │
│ - Hết hạn phiên -> Kích hoạt đăng nhập Google:         │
│   + Mở Popup Google Accounts.                          │
│   + ƯU TIÊN click 'Use another account' trước.         │
│   + Tự động điền email huy.nguyenn@bado.vn -> Enter.   │
│   + Tự động điền mật khẩu -> Enter.                    │
│   + Popup đóng -> Điều hướng vào /quan-ly/cham-cong.   │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ BƯỚC 4: KÍCH HOẠT KHIÊN AN TOÀN TRẠNG THÁI CA          │
│ - Ca đã hoàn thành? -> Không bấm nữa.                  │
│ - Chưa tới giờ ca?  -> Không bấm.                      │
│ - Đúng ca đang chạy -> Tìm nút 'Bắt đầu chấm công ra'. │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ BƯỚC 5: THỰC THI CHẤM CÔNG RA & XÁC NHẬN               │
│ - Bấm nút: "Bắt đầu chấm công ra"                      │
│ - Kiểm tra popup hỏi xác nhận -> Tự bấm "Xác nhận".    │
│ - Chụp ảnh màn hình lưu bằng chứng:                    │
│   timekeeping_result_YYYYMMDD_HHMMSS.png               │
│ - Ghi nhận vào .attendance_state.json (Khóa 1 lần/ngày)│
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ BƯỚC 6: HOÀN TẤT & ĐÓNG TRÌNH DUYỆT                    │
│ - Giữ màn hình 6 giây để hệ thống lưu dữ liệu xong.    │
│ - Đóng Chrome an toàn, giải phóng bộ nhớ.              │
└────────────────────────────────────────────────────────┘
```

---

## 3. Khiên Bảo Vệ An Toàn 6 Lớp (Ironclad Safety Shield)

Điểm cốt lõi được lập trình để **ngăn chặn 100% rủi ro bấm nhầm nút chấm công** khi chưa đến giờ hoặc khi tiến trình gặp sự cố:

| Lớp bảo vệ | Tên gọi | Cách thức bảo vệ |
| :---: | :--- | :--- |
| **Lớp 1** | **Khóa thời gian (Time Lock)** | Nút chấm công bị khóa cứng ở mức mã nguồn nếu thời gian máy tính `< 17:45`. Nếu vô tình chạy `./run` lúc 10h sáng hay 15h chiều, hệ thống **tuyệt đối không bao giờ bấm nút**, chỉ hiển thị cảnh báo `NOT YET TIME FOR TIMEKEEPING!` và đứng canh giờ. |
| **Lớp 2** | **Khóa 1 lần mỗi ngày (Once-Per-Day)** | Mỗi khi bấm chấm công thành công, ngày hôm đó sẽ được đóng dấu vào `.attendance_state.json`. Nếu bạn chạy lại script trong cùng ngày, hệ thống báo `ALREADY CHECKED OUT TODAY!` và khóa nút vĩnh viễn trong ngày đó. |
| **Lớp 3** | **Khóa kiểm thử (Dry-Run Lock)** | Khi chạy các file test (`test_timekeeping_flow.py`, `test_locators.py`), cờ `dry_run=True` luôn được kích hoạt. Lệnh `btn.click()` bị ngắt hoàn toàn ở tầng hàm `execute_timekeeping`. |
| **Lớp 4** | **Khóa xác thực URL (URL Guard)** | Hệ thống chỉ kích hoạt chấm công khi URL hiện tại **chính xác 100%** là `https://bom.bado.vn/quan-ly/cham-cong`. Nếu đang ở trang đăng nhập, trang tổng quan hay trang khác, script từ chối bấm. |
| **Lớp 5** | **Khóa trạng thái ca (Shift Guard)** | Hệ thống kiểm tra phần tử DOM: Nếu phát hiện nhãn `Đã hoàn thành ca làm việc` hoặc `Chưa đến giờ chấm công`, hệ thống sẽ hủy lệnh click ngay lập tức. |
| **Lớp 6** | **Cô lập lỗi (Error Isolation)** | Toàn bộ các bước mạng, mở trang, đăng nhập đều bọc trong khối `try...except`. Nếu mạng rớt hay web tải chậm, tiến trình sẽ dừng lại và báo lỗi vào `debug.log`, **không bao giờ rơi vào tình trạng bấm bậy linh tinh**. |

---

## 4. Cơ Chế Tự Đăng Nhập Google Thông Minh

Tại sao có cơ chế **ưu tiên click "Use another account" trước**?
1. Khi đăng nhập Google trên trình duyệt, Google thường hiển thị danh sách tài khoản đã đăng nhập trước đó (màn hình *Choose an account*).
2. Nếu phiên của tài khoản đó đã hết hạn (Signed out), việc bấm trực tiếp vào tài khoản đó có thể khiến Google chuyển sang màn hình xác thực phức tạp hoặc bị treo.
3. Vì vậy, hệ thống được lập trình:
   - Khi popup Google xuất hiện, nó lập tức tìm và **bấm vào nút "Use another account" (Sử dụng một tài khoản khác)**.
   - Nhờ đó, Google chuyển sang form nhập Email sạch (`//input[@id='identifierId']`).
   - Script tự động điền `huy.nguyenn@bado.vn` -> ấn Enter.
   - Script tự động điền mật khẩu -> ấn Enter.
   - Sau khi đăng nhập thành công, session được lưu lại trong thư mục `automation_profile/` để các ngày tiếp theo không cần gõ lại mật khẩu nữa!

---

## 5. Ý Nghĩa Từng File Trong Dự Án

```
d:/Workspace/timekeeping/
│
├── schedule_timekeeping.py      # FILE CHÍNH: Quản lý hẹn giờ 17:45 hàng ngày,
│                                # điều phối khiên bảo vệ và kích hoạt chấm công.
│
├── run                          # Phím tắt thực thi nhanh trên Linux/macOS/Git Bash: ./run
├── run.sh                       # File bash script thực thi: ./run.sh
├── run.bat                      # File thực thi cho Windows Command Prompt / Double-click.
│
├── model/                       # MÔ HÌNH PAGE OBJECT MODEL (POM)
│   ├── locator/
│   │   └── timekeeping_locator.py # Chứa 100% Locator thuần XPath cho nút bấm, ô nhập, ca làm việc.
│   └── page/
│       ├── base_page.py         # Lớp cơ sở chứa tiện ích Playwright.
│       └── timekeeping_page.py  # Chứa logic đăng nhập Google và 6 tầng khiên bảo vệ execute_timekeeping.
│
├── test/                        # BỘ KIỂM THỬ TỰ ĐỘNG
│   ├── test_locators.py         # Unit test kiểm tra cú pháp XPath và thử nghiệm các khóa an toàn.
│   └── test_timekeeping_flow.py # Test flow an toàn: Chạy tới trang chấm công rồi DỪNG (không bấm nút).
│
├── data/                        # DỮ LIỆU TÀI KHOẢN
│   └── credentials.py           # Lưu thông tin tài khoản đăng nhập bảo mật.
│
├── url/
│   └── timekeeping_page.py      # Cấu hình URL trang chấm công, đường dẫn Chrome và giờ hẹn 17:45.
│
├── automation_profile/          # Thư mục lưu cache và cookie phiên đăng nhập Chrome riêng biệt.
├── .attendance_state.json       # File ghi nhận lịch sử chấm công thành công từng ngày (Khóa 1 lần/ngày).
├── debug.log                    # File ghi toàn bộ nhật ký kỹ thuật chi tiết của mọi lần chạy.
├── Makefile                     # File hỗ trợ các lệnh make tiện lợi.
├── README.md                    # Tài liệu tiếng Anh.
└── README_VI.md                 # Tài liệu tiếng Việt (File này).
```

---

## 6. Bảng Tra Cứu Locator 100% XPath Thuần

Tất cả phần tử trên giao diện BOM BADO đều được định vị bằng mã **XPath chuẩn**:

### 1. Trang Chấm Công (`https://bom.bado.vn/quan-ly/cham-cong`)
| Mục tiêu phần tử | Cú pháp XPath |
| :--- | :--- |
| **Nút Chấm công Ra ca (17:45)** | `//button[contains(., 'Bắt đầu chấm công ra')]` |
| **Nút Chấm công Ra ca (qua thẻ span)** | `//span[text()='Bắt đầu chấm công ra']/ancestor::button` |
| **Nút Chấm công Vào ca** | `//button[contains(., 'Bắt đầu chấm công vào')]` |
| **Trạng thái: Chưa đến giờ chấm công** | `//span[text()='Chưa đến giờ chấm công']/ancestor::div[1]` |
| **Trạng thái: Đã hoàn thành ca làm việc** | `//span[text()='Đã hoàn thành ca làm việc']/ancestor::div[1]` |
| **Trạng thái: Chưa có ca làm việc** | `//span[text()='Chưa có ca làm việc']/ancestor::div[1]` |
| **Khung ca làm việc (Shift Card)** | `//div[contains(@class, 'rounded-[10px]') or contains(@class, 'rounded-[12px]')]` |
| **Modal / Dialog xác nhận** | `//div[@role='dialog']` |
| **Nút Xác nhận trên popup** | `//button[contains(., 'Xác nhận') or contains(., 'Đồng ý')]` |
| **Nút Hủy trên popup** | `//button[contains(., 'Hủy') or contains(., 'Đóng')]` |

### 2. Trang Đăng Nhập & Google OAuth (`https://bom.bado.vn/quan-ly/dang-nhap`)
| Mục tiêu phần tử | Cú pháp XPath |
| :--- | :--- |
| **Nút 'Đăng nhập với Google'** | `(//button[contains(., 'Đăng nhập với Google')])[last()]` |
| **Nút 'Use another account'** | `(//*[normalize-space()='Use another account' or normalize-space()='Sử dụng một tài khoản khác'] \| //*[@role='link' or @role='button' or self::li][contains(., 'Use another account') or contains(., 'Sử dụng một tài khoản khác')])[1]` |
| **Ô điền Email Google** | `//input[@type='email' or @id='identifierId']` |
| **Nút Tiếp theo (Email)** | `(//*[@id='identifierNext']//button \| //*[@id='identifierNext'] \| //button[contains(., 'Tiếp theo') or contains(., 'Next')])[1]` |
| **Ô điền Mật khẩu Google** | `//input[@type='password' or @name='Passwd' or @name='password']` |
| **Nút Tiếp theo (Password)** | `(//*[@id='passwordNext']//button \| //*[@id='passwordNext'] \| //button[contains(., 'Tiếp theo') or contains(., 'Next')])[1]` |

---

## 7. Hướng Dẫn Sử Dụng Hàng Ngày

### Cách 1: Chạy hàng ngày chỉ với 1 thao tác duy nhất
Mở terminal hoặc double-click vào file thực thi:
```bash
./run
# Hoặc trên Windows:
run.bat
```

- **Nếu bạn bật lúc sáng hoặc chiều (trước 17:45)**:
  Màn hình sẽ hiển thị thông báo an toàn, khóa nút chấm công và bắt đầu đếm ngược:
  ```text
  =================================================================
  🛡️ [SAFETY SHIELD ACTIVE] NOT YET TIME FOR TIMEKEEPING!
  =================================================================
  ⏰ Current Time:    15:30:00
  ⏰ Scheduled Time:  17:45:00
  ⏳ Time Remaining:  2h 15m
  🔒 SAFETY LOCK: Checkout button is 100% LOCKED against premature clicks.
  🤖 System is standing by. Chrome will auto-open and execute at exactly 17:45.
  💡 You may minimize this window. Press Ctrl + C to exit anytime.
  📝 Technical logs are recorded in: debug.log
  =================================================================
  ```
  👉 **Bạn chỉ cần thu nhỏ cửa sổ này lại và làm việc bình thường**. Đến đúng **17:45**, script sẽ tự động bật Chrome, tự đăng nhập và bấm chấm công ra cho bạn.

- **Nếu hôm nay đã chấm công rồi mà bạn vô tình bấm lại `./run`**:
  Hệ thống bảo vệ ngay lập tức:
  ```text
  =================================================================
  🛡️ [SAFETY SHIELD] ALREADY CHECKED OUT TODAY!
  =================================================================
  📅 Date: 2026-10-14
  🔒 SAFETY LOCK: Timekeeping checkout has ALREADY succeeded today.
  🛡️ The check-out button is 100% LOCKED to prevent accidental double-clicks.
  =================================================================
  ```

---

### Cách 2: Kiểm tra hệ thống (Test flow an toàn tuyệt đối)
Nếu muốn mở Chrome lên xem hệ thống tự vào trang Chấm Công mà **hoàn toàn không bấm nút**:
```bash
python test/test_timekeeping_flow.py
```

### Cách 3: Kiểm thử cú pháp XPath và các tầng khóa an toàn
```bash
python -m pytest test/test_locators.py -v
```
*(Kết quả: 4/4 test passed)*

---

## 💡 Lưu Ý Quan Trọng
1. Giữ máy tính không ở chế độ Ngủ sâu (Sleep) vào thời điểm 17:45 để tiến trình hẹn giờ có thể kích hoạt Chrome đúng giờ.
2. Mọi thông tin log chi tiết từng giây của từng lần chạy đều được lưu ngầm trong file [debug.log](file:///d:/Workspace/timekeeping/debug.log).
3. Ảnh bằng chứng sau mỗi lần chấm công thành công sẽ được lưu tự động với tên dạng `timekeeping_result_YYYYMMDD_HHMMSS.png` ngay trong thư mục gốc.
