# Trợ lý Lập trình Thông Minh (Smart Programming Assistant) - Phiên bản Web Flask

## 🤖 Giới Thiệu

**Trợ Lý Lập Trình Thông Minh** là một ứng dụng web Python được thiết kế để hỗ trợ các lập trình viên trong việc phân tích và gỡ lỗi mã nguồn. Sử dụng sức mạnh của mô hình ngôn ngữ lớn Gemini của Google, trợ lý này cung cấp các phân tích chi tiết và mô phỏng thực thi mã.

Phiên bản này được xây dựng bằng Flask, cung cấp một giao diện web trực quan để người dùng tương tác.

## ✨ Tính Năng Chính

*   **Phân Tích Mã Nguồn Sâu Sắc**:
    *   Nhận diện lỗi cú pháp, lỗi logic, và các lỗi thời gian chạy tiềm ẩn trong mã nguồn (hỗ trợ Python, C).
    *   Đánh giá xem mã nguồn có đáp ứng yêu cầu của đề bài hay không.
*   **Gợi Ý Sửa Lỗi Chi Tiết**:
    *   Giải thích nguyên nhân của từng lỗi được phát hiện.
    *   Đề xuất các cách sửa lỗi cụ thể, kèm theo ví dụ mã đã sửa (nếu cần).
*   **Mô Phỏng Thực Thi Từng Bước**:
    *   Mô phỏng thực thi mã nguồn gốc với các trường hợp kiểm thử (test cases) do AI tạo ra.
    *   **Trường hợp lỗi**: Hiển thị chi tiết từng bước thực thi dẫn đến lỗi, giá trị biến, và giải thích tại sao lỗi xảy ra.
    *   **Trường hợp chạy đúng (Happy Path)**: Hiển thị chi tiết từng bước thực thi khi mã chạy đúng với một đầu vào phù hợp.
*   **Đánh Giá Tổng Quát**:
    *   Cung cấp nhận xét chung về mã nguồn, hiệu suất (nếu có thể đánh giá), và các đề xuất cải thiện khác.
*   **Giao Diện Web Hiện Đại**:
    *   Giao diện người dùng trực quan, dễ sử dụng được xây dựng bằng Flask và HTML/CSS/JavaScript.
    *   Hỗ trợ chế độ **Dark Mode** để làm việc thoải mái hơn trong điều kiện ánh sáng yếu.
    *   Hiệu ứng **Loading Animation** khi xử lý yêu cầu phân tích.
    *   Hiệu ứng **Pháo Bông (Confetti)** khi mã nguồn được đánh giá là đúng và đáp ứng yêu cầu.
*   **Cấu Hình API Linh Hoạt**:
    *   Cho phép người dùng cấu hình Google Gemini API key. (Hiện tại API key đang được hardcode trong `smart_programming_assistant.py` - cần cải thiện để bảo mật hơn).

## 🔧 Yêu Cầu Hệ Thống

*   Python 3.7+
*   Các thư viện Python (có thể cài đặt qua pip, xem `requirements.txt` nếu có, hoặc cài đặt thủ công):
    *   `google-generativeai`
    *   `Flask`
    *   `MarkupSafe` (thường được cài đặt cùng với Flask)
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
    pip install google-generativeai Flask markupsafe
    ```
    (Lưu ý: Tạo file `requirements.txt` với các thư viện này là một good practice.)

3.  **Cấu Hình API Key:**
    *   Hiện tại, API key đang được đặt trực tiếp trong file `smart_programming_assistant.py` tại hàm `setup_gemini_api()`:
        ```python
        api_key = "AIzaSyAa7zBQuCGvrsoQ3WF75JL76_0ZiD4_w6g" 
        ```
    *   **Khuyến nghị:** Để bảo mật, bạn nên thay thế bằng cách sử dụng biến môi trường hoặc một file cấu hình riêng không được commit vào repository.

4.  **Chạy Ứng Dụng Web:**
    Thực thi file Python chính:
    ```bash
    python smart_programming_assistant.py
    ```

5.  **Truy Cập Ứng Dụng:**
    *   Sau khi chạy lệnh trên, ứng dụng Flask sẽ khởi động một web server cục bộ.
    *   Mở trình duyệt web của bạn và truy cập vào địa chỉ được hiển thị trong terminal (thường là `http://127.0.0.1:5001/`).

## 🛠️ Cách Sử Dụng

1.  **Truy Cập Giao Diện Web**: Mở trình duyệt và đi đến địa chỉ của ứng dụng (ví dụ: `http://127.0.0.1:5001/`).
2.  **Kiểm Tra Trạng Thái API**: Giao diện sẽ hiển thị trạng thái kết nối API Key.
3.  **Nhập Thông Tin Phân Tích**:
    *   **Đề bài (Mô tả yêu cầu)**: Nhập mô tả chi tiết về vấn đề hoặc yêu cầu của mã nguồn.
    *   **Ngôn ngữ lập trình**: Chọn ngôn ngữ của mã nguồn (hiện tại hỗ trợ Python, C).
    *   **Mã nguồn**: Dán hoặc gõ mã nguồn cần phân tích vào ô tương ứng.
4.  **Phân Tích Mã Nguồn**:
    *   Nhấn nút "Phân tích Mã nguồn".
    *   Một hiệu ứng loading sẽ xuất hiện trong khi trợ lý xử lý.
5.  **Xem Kết Quả Phân Tích**:
    *   Kết quả sẽ được hiển thị trên một trang mới, bao gồm:
        *   Phân tích tổng quan về mã (đáp ứng yêu cầu, các loại lỗi).
        *   Gợi ý sửa lỗi chi tiết.
        *   Mô phỏng thực thi từng bước cho trường hợp lỗi và trường hợp chạy đúng.
        *   Đánh giá chung về mã nguồn.
    *   Nếu mã được phân tích là hoàn toàn chính xác và đáp ứng yêu cầu, một hiệu ứng pháo bông (confetti) sẽ xuất hiện.
6.  **Chuyển Đổi Giao Diện (Dark Mode)**:
    *   Sử dụng nút "Giao diện Sáng/Tối" để chuyển đổi giữa chế độ sáng và tối. Lựa chọn sẽ được lưu lại cho lần truy cập sau.

## 📂 Cấu Trúc Dự Án

*   `smart_programming_assistant.py`: File Python chính chứa logic của ứng dụng Flask, bao gồm:
    *   Thiết lập API Gemini.
    *   Định nghĩa các route của Flask (`/`, `/analyze`).
    *   Hàm tạo prompt cho Gemini.
    *   Hàm xử lý yêu cầu phân tích và tương tác với API Gemini.
    *   Hàm chuyển đổi văn bản sang HTML.
*   `templates/`: Thư mục chứa các file template HTML:
    *   `index.html`: Trang chính để nhập liệu.
    *   `results.html`: Trang hiển thị kết quả phân tích.
*   **(Đề xuất) `static/`**: Thư mục có thể được tạo để chứa các file tĩnh như CSS, JavaScript riêng (nếu cần mở rộng ngoài việc nhúng trực tiếp vào HTML).
*   **(Đề xuất) `requirements.txt`**: File liệt kê các thư viện Python cần thiết.

## 💡 Cải Tiến Tiềm Năng

*   **Bảo Mật API Key**: Sử dụng biến môi trường hoặc file config an toàn cho API key.
*   **Tạo `requirements.txt`**: Tự động hóa việc cài đặt dependencies.
*   **Hỗ trợ Thêm Ngôn Ngữ**: Mở rộng khả năng phân tích cho nhiều ngôn ngữ lập trình hơn.
*   **Lưu/Tải Phiên Làm Việc**: Cho phép người dùng lưu lại trạng thái phân tích hoặc mã nguồn.
*   **Tích Hợp Git**: Cho phép phân tích mã từ repository Git.
*   **Cải Thiện UI/UX**: Nâng cao trải nghiệm người dùng với các tính năng tương tác phong phú hơn.
*   **Phân Tách CSS/JS**: Di chuyển CSS và JavaScript ra các file riêng trong thư mục `static/` để dễ quản lý hơn.

---

Hy vọng Trợ Lý Lập Trình Thông Minh (phiên bản Web Flask) này sẽ hữu ích cho bạn! 