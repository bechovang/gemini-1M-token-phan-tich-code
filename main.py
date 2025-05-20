#!/usr/bin/env python3
"""
Trợ lý Lập trình Thông minh (Smart Programming Assistant) - Phiên bản 1.0
Dependencies:
  pip install google-generativeai Flask python-dotenv
"""

import os
import sys
import json
import textwrap
import google.generativeai as genai
from flask import Flask, render_template, request
from markupsafe import Markup
from dotenv import load_dotenv

# Khởi tạo Flask app
app = Flask(__name__)

# Xác định thư mục chứa main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load biến môi trường từ .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Lấy key Gemini từ .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Chưa thiết lập GEMINI_API_KEY trong .env")
    sys.exit(1)

# Đường dẫn tuyệt đối tới key.json
KEY_FILE = os.path.join(BASE_DIR, 'key.json')

def load_keys():
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'w') as f:
            json.dump({}, f)
    with open(KEY_FILE) as f:
        return json.load(f)

def save_keys(keys):
    with open(KEY_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def validate_and_consume_key(key):
    keys = load_keys()
    if key not in keys:
        return False, "API Key không hợp lệ."
    if keys[key] >= 10:
        return False, "API Key đã hết hạn dùng (10 lần)."
    keys[key] += 1
    save_keys(keys)
    return True, None

# Biến global cho Gemini
model_name_global = None
gemini_model_global = None

def setup_gemini_api():
    """
    Cấu hình và test kết nối Google Gemini theo API key từ .env.
    Trả về True nếu thành công, False nếu thất bại.
    """
    global model_name_global, gemini_model_global

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY chưa được thiết lập trong .env")
        return False

    # Cấu hình genai
    genai.configure(api_key=api_key)

    try:
        model_to_use = "gemini-1.5-pro-latest"
        gemini_model_global = genai.GenerativeModel(model_to_use)
        # Test kết nối
        test_resp = gemini_model_global.generate_content("Hello")
        if not getattr(test_resp, "text", None):
            raise RuntimeError("Phản hồi rỗng từ Gemini")

        print(f"✅ Google Gemini API configured. Model: {model_to_use}")
        model_name_global = model_to_use
        return True

    except Exception as e:
        print(f"❌ Lỗi xác thực Gemini API: {e}")
        model_name_global = None
        gemini_model_global = None
        return False

# Gọi ngay khi module được import, để WSGI cũng khởi tạo model
setup_gemini_api()

def create_prompt(problem_description, source_code, language):
    return textwrap.dedent(f"""
    Bạn là một trợ lý lập trình thông minh chuyên phân tích và debug mã nguồn {language}.
    
    # Đề bài:
    {problem_description}
    
    # Mã nguồn {language} (DO NGƯỜI DÙNG CUNG CẤP):
    ```{language}
    {source_code}
    ```
    
    Hãy thực hiện các nhiệm vụ sau ĐỐI VỚI MÃ NGUỒN GỐC DO NGƯỜI DÙNG CUNG CẤP:
    
    ## 1. Phân tích mã nguồn
    - Phân tích cú pháp và ngữ nghĩa của mã nguồn {language} gốc.
    - Xác định xem mã nguồn gốc có thỏa mãn yêu cầu của đề bài không.
    - Tìm và liệt kê tất cả các lỗi trong mã nguồn gốc: lỗi cú pháp, lỗi logic, lỗi thời gian chạy tiềm ẩn.
    
    ## 2. Gợi ý sửa lỗi (Dành cho mã nguồn gốc)
    - Giải thích chi tiết từng lỗi đã tìm thấy trong mã nguồn gốc (nguyên nhân, dòng code có lỗi).
    - Đề xuất cách sửa lỗi cụ thể cho mã nguồn gốc.
    - Cung cấp đoạn mã đã sửa (nếu cần thiết, dựa trên mã nguồn gốc và các lỗi đã tìm thấy).
    
    ## 3. Mô phỏng thực thi từng bước
    - **Error Case Simulation**: tìm hoặc tạo test case gây lỗi, mô phỏng chi tiết từng bước.
    - **Happy Path Simulation**: tìm hoặc tạo test case chạy đúng, mô phỏng chi tiết.
    
    ## 4. Đánh giá tổng quát (Về mã nguồn gốc)
    - Tóm tắt, đánh giá hiệu suất, đề xuất cải thiện (nếu có).
    
    **LƯU Ý**: Chỉ trả về duy nhất một đối tượng JSON hợp lệ, không kèm text giải thích ngoài JSON.
    """)

def analyze_code_with_gemini(model_name, prompt_text):
    if not model_name or not gemini_model_global:
        return None, "Model hoặc Gemini client không được cấu hình."
    try:
        cfg = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 20480,
        }
        resp = gemini_model_global.generate_content(prompt_text, generation_config=cfg)
        raw = resp.text.strip()

        # Nếu model trả về trong markdown block, strip backticks
        json_str = raw
        if raw.startswith("```"):
            parts = raw.split("```", 2)
            if len(parts) >= 3:
                json_str = parts[1].strip()

        try:
            result = json.loads(json_str)
            return result, None
        except json.JSONDecodeError as e:
            return None, f"JSON parse error: {e}\\nResponse:\\n{json_str}"

    except Exception as e:
        return None, f"Lỗi khi gọi Gemini API: {e}"

def text_to_html(text_content):
    if not text_content:
        return ""
    s = str(text_content)
    return Markup(
        s.replace('&', '&amp;')
         .replace('<', '&lt;')
         .replace('>', '&gt;')
         .replace('\n', '<br>')
         .replace('  ', ' &nbsp;')
    )

@app.route('/', methods=['GET'])
def index():
    if not model_name_global:
        api_status = "API Key không hợp lệ hoặc model không khả dụng. Vui lòng kiểm tra console."
    else:
        api_status = f"API Key hợp lệ. Model: {model_name_global}"
    return render_template('index.html', api_status=api_status)

@app.route('/analyze', methods=['POST'])
def analyze():
    user_key = request.form.get('api_key', '').strip()
    valid, err = validate_and_consume_key(user_key)
    if not valid:
        return render_template('index.html', error_message=err)

    if not model_name_global:
        return render_template('result.html', error_message="Lỗi: Gemini API chưa được cấu hình đúng.", text_to_html=text_to_html)

    problem = request.form.get('problem_description','').strip()
    code    = request.form.get('source_code','').strip()
    lang    = request.form.get('language','Python')

    if not problem or not code:
        return render_template('index.html', error_message="Vui lòng nhập đề bài và mã nguồn.", api_status=f"Model: {model_name_global}")

    prompt = create_prompt(problem, code, lang)
    result, error = analyze_code_with_gemini(model_name_global, prompt)
    if error:
        return render_template('result.html', error_message=f"Lỗi phân tích: {error}", text_to_html=text_to_html)

    return render_template('result.html', result=result, language=lang, text_to_html=text_to_html)

if __name__ == '__main__':
    # Khi chạy trực tiếp, Flask sẽ serve ở port trong .env hoặc 5001 mặc định
    port = int(os.getenv('FLASK_RUN_PORT', '5001'))
    app.run(debug=True, port=port)