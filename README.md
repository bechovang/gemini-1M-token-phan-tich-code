# Smart Programming Assistant (Local Version)

## 🤖 Giới Thiệu

**Trợ Lý Lập Trình Thông Minh** là một ứng dụng Python được thiết kế để hỗ trợ các lập trình viên trong việc phân tích, gỡ lỗi, và tối ưu hóa mã nguồn. Sử dụng sức mạnh của mô hình ngôn ngữ lớn Gemini của Google, trợ lý này cung cấp nhiều công cụ hữu ích để nâng cao năng suất và chất lượng mã.

Phiên bản này đã được điều chỉnh để chạy cục bộ trên máy tính của bạn với giao diện người dùng đồ họa (GUI) được xây dựng bằng Tkinter.

## ✨ Tính Năng Chính

*   **Phân Tích Mã Nguồn**:
    *   Kiểm tra lỗi cú pháp cho Python và C.
    *   Thực thi mã (Python, C) và báo cáo lỗi runtime.
    *   Phân tích logic mã dựa trên yêu cầu, xác định các vấn đề và đề xuất giải pháp.
    *   Đánh giá mức độ tuân thủ của mã với yêu cầu đã cho.
    *   Đề xuất mã nguồn đã sửa lỗi.
*   **Mô Phỏng Thực Thi**:
    *   Mô phỏng từng bước thực thi của mã nguồn (Python, C).
    *   Hiển thị trạng thái biến và luồng điều khiển.
*   **Sinh Test Case**:
    *   Đề xuất các trường hợp kiểm thử (test cases) dựa trên mã nguồn và yêu cầu.
    *   Hỗ trợ tạo khung test case cho Python (unittest, pytest) và C (asserts).
*   **Giải Thích Mã Nguồn**:
    *   Cung cấp giải thích chi tiết về chức năng, cấu trúc và các thuật toán trong mã.
*   **So Sánh Phiên Bản**:
    *   So sánh hai phiên bản gần nhất của mã nguồn và hiển thị sự khác biệt.
*   **Quản Lý File**:
    *   Tải lên và xử lý các file mã nguồn đơn lẻ (`.py`, `.c`, `.h`) hoặc file nén ZIP chứa nhiều file.
*   **Giao Diện Người Dùng Thân Thiện**:
    *   GUI được xây dựng bằng Tkinter, dễ sử dụng.
    *   Yêu cầu nhập API Key của Gemini khi khởi động.
    *   Các vùng riêng biệt cho yêu cầu, nhập mã, và hiển thị kết quả.

## 🔧 Yêu Cầu Hệ Thống

*   Python 3.7+
*   Các thư viện Python (có thể cài đặt qua pip):
    *   `google-generativeai`
    *   `tiktoken`
    *   `pytest` (dùng cho việc sinh và chạy một số test case, không bắt buộc cho chức năng chính của trợ lý)
*   Trình biên dịch C (ví dụ: `gcc`) nếu bạn muốn làm việc với mã C.
*   Một API Key hợp lệ từ Google AI Studio cho mô hình Gemini.

## 🚀 Hướng Dẫn Cài Đặt và Chạy

1.  **Clone Repository (Nếu có):**
    ```bash
    git clone <URL_REPO_CUA_BAN>
    cd <TEN_THU_MUC_REPO>
    ```

2.  **Cài Đặt Thư Viện:**
    Mở terminal hoặc command prompt và chạy:
    ```bash
    pip install google-generativeai tiktoken pytest
    ```

3.  **Chạy Ứng Dụng:**
    Thực thi file Python chính (ví dụ: `Web_smart_programming_assistant.py` hoặc tên file bạn đã lưu):
    ```bash
    python Web_smart_programming_assistant.py
    ```

4.  **Nhập API Key:**
    *   Khi ứng dụng khởi chạy, một cửa sổ sẽ yêu cầu bạn nhập API Key của Gemini.
    *   Lấy API Key của bạn từ [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Nhập API Key và nhấn "Lưu API Key". Nếu thành công, giao diện chính của ứng dụng sẽ xuất hiện.

## 🛠️ Cách Sử Dụng

1.  **Nhập API Key**: Bước đầu tiên khi khởi động ứng dụng.
2.  **(Tùy chọn) Lưu Yêu Cầu Đề Bài**:
    *   Nhập mô tả hoặc yêu cầu của dự án/bài toán vào ô "Yêu Cầu Đề Bài".
    *   Nhấn "Lưu Yêu Cầu". Trợ lý sẽ phân tích sơ bộ yêu cầu này.
3.  **Nhập hoặc Tải Mã Nguồn**:
    *   **Nhập trực tiếp**:
        *   Chọn ngôn ngữ (Python hoặc C) từ danh sách thả xuống.
        *   Dán hoặc gõ mã nguồn vào ô "Nhập Mã Nguồn".
        *   Nhấn "Lưu Mã Nguồn Này". Trợ lý sẽ phân tích sơ bộ mã này.
    *   **Tải file**:
        *   Nhấn nút "Tải File Lên (.py, .c, .h, .zip)".
        *   Chọn file mã nguồn hoặc file ZIP từ máy tính của bạn.
        *   Mã từ file sẽ được xử lý. Nếu là file mã nguồn đơn lẻ và phù hợp với ngôn ngữ đang chọn, nó có thể được tải vào ô nhập mã.
4.  **Sử Dụng Các Công Cụ**:
    Sau khi có mã nguồn và (tùy chọn) yêu cầu, bạn có thể sử dụng các nút trong phần "Công Cụ":
    *   **Phân Tích Mã**: Phân tích chi tiết mã nguồn hiện tại dựa trên yêu cầu.
    *   **Mô Phỏng Thực Thi**: Mô phỏng từng bước chạy của mã.
    *   **Sinh Test Case**: Tạo các gợi ý test case cho mã.
    *   **Giải Thích Mã**: Yêu cầu trợ lý giải thích chức năng và logic của mã.
    *   **So Sánh Phiên Bản**: So sánh phiên bản mã hiện tại với phiên bản trước đó (nếu có ít nhất 2 phiên bản đã được lưu).
5.  **Xem Kết Quả**:
    *   Tất cả các phản hồi, phân tích, và kết quả từ trợ lý sẽ được hiển thị trong ô "Kết Quả" ở phía dưới giao diện.

## 📂 Cấu Trúc Dự Án (Sơ Lược)

*   `Web_smart_programming_assistant.py` (hoặc tên tương tự): File Python chính chứa toàn bộ logic của ứng dụng.
    *   `Config`: Lớp chứa các cấu hình chung (tên model, ngôn ngữ hỗ trợ, v.v.).
    *   `Utils`: Lớp chứa các hàm tiện ích (đếm token, đọc/ghi file, so sánh code, v.v.).
    *   `GeminiClient`: Lớp quản lý tương tác với API Gemini.
    *   `CodeExecutor`: Lớp thực thi mã Python và C, biên dịch mã C.
    *   `CodeAnalyzer`: Lớp phân tích mã, kiểm tra cú pháp, mô phỏng thực thi, sinh test case bằng cách sử dụng `GeminiClient`.
    *   `SmartProgrammingAssistant`: Lớp chính điều phối các hoạt động của trợ lý, quản lý mã nguồn, lịch sử phiên bản, và yêu cầu.
    *   `UI`: Lớp xây dựng và quản lý giao diện người dùng đồ họa bằng Tkinter.

## 💡 Cải Tiến Tiềm Năng

*   Hỗ trợ thêm nhiều ngôn ngữ lập trình.
*   Cải thiện khả năng định dạng Markdown trong đầu ra Tkinter (hiện tại là text thuần).
*   Tích hợp với các IDE phổ biến.
*   Lưu và tải lại phiên làm việc.
*   Cho phép tùy chỉnh chi tiết hơn các tham số của mô hình Gemini.
*   Thêm tính năng gỡ lỗi tương tác.

---

Hy vọng Trợ Lý Lập Trình Thông Minh này sẽ hữu ích cho bạn! 