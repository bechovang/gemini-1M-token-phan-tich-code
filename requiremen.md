**Tài liệu Yêu Cầu (Requirements Document) - Phiên bản 1.1**

**1. Tên Ứng Dụng:** Trợ Lý Lập Trình Thông Minh (Smart Programming Assistant) - Phiên bản 1.1

**2. Mục Tiêu:**

* Hỗ trợ người dùng (lập trình viên, sinh viên, người tự học) phát hiện, hiểu và sửa lỗi trong các đoạn mã nguồn C và Python.
* Diễn giải quá trình thực thi từng bước, quá trình thay đổi giá trị biến, điều khiển luồng và bộ nhớ.
* Tận dụng mô hình ngôn ngữ lớn (LLM) có token lớn (đến 1 triệu token) để duy trì ngữ cảnh dài và so sánh nhiều phiên bản code.

**3. Đối Tượng Người Dùng:**

* Lập trình viên (mới bắt đầu đến trung cấp) làm việc với C và Python.
* Sinh viên ngành CNTT, kỹ thuật điện - điện tử.
* Người muốn hiểu luồng thực thi mã và hành vi chương trình.

**4. Phạm Vi:**

* Chạy trên Google Colaboratory (Colab), tích hợp Gemini API (1M token).
* Hỗ trợ ngôn ngữ: C và Python trong giai đoạn đầu.
* Nhận nhiều file code, gợi file zip hoặc paste trực tiếp.
* Lịch sử, phiên bản mã và ngữ cảnh toàn vện được duy trì theo cuộc hội thoại.

**5. Yêu Cầu Chức Năng (Functional Requirements):**

* **FR01: Nhận Đầu Vào:**

  * Nhận đề bài dưới dạng ngôn ngữ tự nhiên (Việt/Anh).
  * Nhận nhiều file mã nguồn, zip, hoặc input trực tiếp.
  * Cho phép chọn ngôn ngữ (C hoặc Python).

* **FR02: Phân Tích Mã Nguồn:**

  * Xác định lỗi cú pháp, lỗi logic, và runtime errors.
  * So sánh mã với yêu cầu đề bài, highlight đoạn sai.
  * Phân tích phiên bản cũ/phiên bản mới (diff context).

* **FR03: Gợi Ý Sửa Lỗi:**

  * Giải thích nguyên nhân lỗi theo dòng.
  * Đề xuất cách sửa cụ thể, khởi phục mã.
  * Đề xuất thư viện, khai báo biến, đổi kiểu.

* **FR04: Mô Phỏng Thực Thi Từng Bước:**

  * Diễn giải theo dõi:

    * Dòng code thực thi.
    * Trạng thái biến (tên, kiểu, giá trị).
    * Luồng điều khiển: if/else, loop, return.
    * Cấu trúc bộ nhớ: stack, heap (C), thông dịch (Python).
  * Cho phép:

    * **Chọn mức chi tiết** (biến chính hoặc chi tiết toàn stack).
    * **Tua lại, xem trước**, breakpoint logic (giả sử giá trị).

* **FR05: Hiển Thị KếT QuẢ:**

  * Diễn đạt dễ hiểu với markdown, highlight lỗi, code block.
  * Gợi nhớ dạng interactive (output theo tab: lỗi - mô phỏng - sửa).

* **FR06: Quản Lý Ngữ Cảnh:**

  * Ghi nhớ lịch sử code, tương tác, câu hỏi trước.
  * So sánh phiên bản, trả lời ngữu cảnh.

* **FR07: Tự Động Tạo Test Case:**

  * Sinh test case theo đề bài, bao gồm:

    * Trường hợp bên trong, ngoại biên.
    * Tài liệu input/output, đoạn `assert`, `unittest`, `pytest`.

* **FR08: Trợ Lý Học Tập Cá Nhân:**

  * Nhận diện lỗi thường gặp, ghi nhớ khóa học người dùng tương tác.
  * Đề xuất bài tập bài ở mức độ phù hợp.

**6. Yêu Cầu Phi Chức Năng (Non-Functional Requirements):**

* **NFR01: Hiệu Suất:** Phản hồi nhất quán trong vòng 10s với code nhỏ.
* **NFR02: Giao Diện:** Dễ dùng, hỗ trợ markdown/code block/tab.
* **NFR03: Tin Cậy:** Nên ghi rõ AI chỉ gợi ý - người dùng kiểm tra lại.
* **NFR04: Mở Rộng:** Kiến trúc tôi ưu để hỗ trợ ngôn ngữ mới sau (Java, C++).
* **NFR05: Bảo Mật:** Bảo vệ API key, không hardcode.
* **NFR06: Tối Ưu Token:** Dùng token lâu dài hợp lý, lánh lặp prompt vô ích.

**7. Ràng Buộc (Constraints):**

* **CON01:** Chạy trên Google Colab.
* **CON02:** Sử dụng Gemini API (hoặc tương đương).
* **CON03:** Hỗ trợ ngôn ngữ C và Python giai đoạn đầu.
* **CON04:** Tuân thủ giới hạn token và tốc độ API.
* **CON05:** Tích hợp qua `google.generativeai`, không lạm mất key.

**8. Tiêu Chí Chấp Nhận (Acceptance Criteria):**

* Nhận được đề bài + nhiều file code.
* Phân tích, highlight đúng lỗi cú pháp/logic/runtime.
* Gợi ý chi tiết cách sửa.
* Mô phỏng theo dõi biến/tình trạng từng bước.
* Cho test case, assert, unittest/pytest.
* Duy trì ngữ cảnh dài, so sánh phiên bản.
* Trình bày rõ ràng và có hướng dẫn trong Colab.

**9. Ghi Chú Tùy Chọn Tương Lai:**

* Hỗ trợ ngôn ngữ Java, C++, Rust.
* Kết nối gdb (C), pdb (Python) ở dạng mô phỏng.
* Sinh đề thi, quiz theo tiểu chí chọn sẵn.
* Kết hợp dạng chatbot nhị gờ code + nhận xét.
