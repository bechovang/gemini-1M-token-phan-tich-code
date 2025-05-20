# Smart Programming Assistant (Local Version)

## 🧠 Giới Thiệu

**Trợ Lý Lập Trình Thông Minh** là một ứng dụng Python được thiết kế để hỗ trợ các lập trình viên trong việc phân tích, gỡ lỗi, và tối ưu hóa mã nguồn. Sử dụng sức mạnh của mô hình ngôn ngữ lớn Gemini của Google, trợ lý này cung cấp nhiều công cụ hữu ích để nâng cao năng suất và chất lượng mã.

Phiên bản này đã được điều chỉnh để chạy cục bộ trên máy tính của bạn với giao diện người dùng đồ họa (GUI) được xây dựng bằng Tkinter.

## ✨ Tính Năng Chính

* **Phân Tích Mã Nguồn**:

  * Kiểm tra lỗi cú pháp cho Python và C.
  * Thực thi mã (Python, C) và báo cáo lỗi runtime.
  * Phân tích logic mã dựa trên yêu cầu, xác định các vấn đề và đề xuất giải pháp.
  * Đánh giá mức độ tuân thủ của mã với yêu cầu đã cho.
  * Đề xuất mã nguồn đã sửa lỗi.
* **Mô Phỏng Thực Thi**:

  * Mô phỏng từng bước thực thi của mã nguồn (Python, C).
  * Hiển thị trạng thái biến và luồng điều khiển.
* **Sinh Test Case**:

  * Đề xuất các trường hợp kiểm thử (test cases) dựa trên mã nguồn và yêu cầu.
  * Hỗ trợ tạo khung test case cho Python (unittest, pytest) và C (asserts).
* **Giải Thích Mã Nguồn**:

  * Cung cấp giải thích chi tiết về chức năng, cấu trúc và các thuật toán trong mã.
* **So Sánh Phiên Bản**:

  * So sánh hai phiên bản gần nhất của mã nguồn và hiển thị sự khác biệt.
* **Quản Lý File**:

  * Tải lên và xử lý các file mã nguồn đơn lẻ (`.py`, `.c`, `.h`) hoặc file nén ZIP chứa nhiều file.
* **Giao Diện Người Dùng Thân Thiện**:

  * GUI được xây dựng bằng Tkinter, dễ sử dụng.
  * Yêu cầu nhập API Key của Gemini khi khởi động.
  * Các vùng riêng biệt cho yêu cầu, nhập mã, và hiển thị kết quả.

## 🔧 Yêu Cầu Hệ Thống

* Python 3.7+
* Các thư viện Python (có thể cài đặt qua pip):

  * `google-generativeai`
  * `tiktoken`
  * `pytest`
* Trình biên dịch C (gcc)
* API Key từ Google AI Studio

## 🚀 Thiết Lập Nhanh cho Windows

```bash
:: Clone repo và về commit ổn định

git clone https://github.com/bechovang/gemini-1M-token-phan-tich-code
cd gemini-1M-token-phan-tich-code
git reset --hard 99c49c34e40df8d89fedce693a58076439ba156c

:: Cài Python 3.10.11 bằng Chocolatey
choco install python --version=3.10.11 -y

:: Tạo và kích hoạt vền
python -m venv venv
venv\Scripts\activate

:: Cài thư viện
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install matplotlib tqdm Flask google-generativeai

:: Chạy chương trình
python smart_programming_assistant.py
```

## 📚 Hướng Dẫn Sử Dụng

1. **Nhập API Key**
2. **Lưu Yêu Cầu** (tuỳ chọn)
3. **Nhập/Tải file mã nguồn** (.py, .c, .zip)
4. **Phân tích - Mô phỏng - Sinh test case - Giải thích - So sánh**
5. **Xem kết quả** ở vùng "Kết Quả"

## 📂 Cấu Trúc Thư Mục

```
smart_programming_assistant.py       # Main GUI
assistant/
└ gemini_api_test_v1.py
└ local_assistant.py
└ __init__.py

templates/
test_data/
└ test_dung.txt
└ test_sai.txt

.env.example
requirements.txt
README.md
```

## 💡 Gợi Ý Cải Tiến

* Thêm hỗ trợ ngôn ngữ khác
* Giao diện hiện đầu ra dể đọc hơn
* Lưu/Phiên làm việc
* Kết nối với IDE
* Tuỳ chỉnh tham số Gemini API
* Debug tương tác

---

Hy vọng Trợ Lý Lập Trình Thông Minh sẽ giúc bạn học nhanh và code tốt hơn! 🚀
