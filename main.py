# @title **Trợ lý Lập trình Thông minh (Smart Programming Assistant) - Phiên bản 1.0**

# Cài đặt thư viện cần thiết
# Make sure to install google-generativeai: pip install google-generativeai
# Make sure to install Flask: pip install Flask
# Make sure to install python-dotenv: pip install python-dotenv

import os
import sys
import re
import textwrap
import google.generativeai as genai  # Use Google's Gemini API
import json
from flask import Flask, render_template, request
from markupsafe import Markup
from dotenv import load_dotenv # Added for loading .env file

app = Flask(__name__)

# Global variables
model_name_global = None
gemini_model_global = None  # Global Gemini model

# Key 10 lần dùng
KEY_FILE = 'key.json'

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
    # tăng bộ đếm
    keys[key] += 1
    save_keys(keys)
    return True, None

# Lấy API key từ .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Chưa thiết lập GEMINI_API_KEY trong .env")
    sys.exit(1)

genai.configure(api_key=api_key)


# Cấu hình API key cho Gemini
def setup_gemini_api():
  load_dotenv()  # Load environment variables from .env file
  global model_name_global, gemini_model_global
  try:
    api_key = "AIzaSyBYEKKI0v-5WvixUA4BY9EPLeOul92FYcQ"
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    model_to_use = "gemini-1.5-pro-latest"  # or "gemini-pro" if you prefer
    
    # Test the connection by initializing a model
    try:
        # Initialize the model
        gemini_model_global = genai.GenerativeModel(model_to_use)
        
        # Simple test to see if the model can be accessed
        test_response = gemini_model_global.generate_content("Hello")
        if test_response:
            print(f"✅ Google Gemini API key configured and authenticated! Using model: {model_to_use}")
        else:
            raise Exception("Model returned empty response")
            
    except Exception as auth_err:
        print(f"❌ Lỗi xác thực Gemini API: {str(auth_err)}")
        print("Vui lòng kiểm tra lại API key.")
        model_name_global = None
        gemini_model_global = None
        return False
        
    model_name_global = model_to_use
    return True
  except Exception as e:
    print(f"❌ Lỗi khi cấu hình Gemini API: {str(e)}")
    model_name_global = None
    gemini_model_global = None
    return False

# Cải thiện create_prompt cho phần mô phỏng thực thi rõ ràng hơn
def create_prompt(problem_description, source_code, language):
  prompt = f"""
  Bạn là một trợ lý lập trình thông minh chuyên phân tích và debug mã nguồn {language}.
  
  # Đề bài:
  {problem_description}
  
  # Mã nguồn {language} (DO NGƯỜỜI DÙNG CUNG CẤP):
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
  
  ## 3. Mô phỏng thực thi từng bước (Sử dụng MÃ NGUỒN GỐC của người dùng)
  Nhiệm vụ của bạn là tìm hoặc tạo ra các trường hợp kiểm thử (test cases) cho MÃ NGUỒN GỐC được cung cấp và mô phỏng chúng.
  
  - **Trường hợp tìm lỗi (Error Case Simulation):**
    + Cố gắng tìm hoặc tạo một ví dụ đầu vào (test case) cụ thể mà sẽ khiến MÃ NGUỒN GỐC gây ra lỗi (logic, runtime) hoặc cho kết quả sai dựa trên phân tích ở Mục 1.
    + Nếu bạn xác định được một test case gây lỗi:
      - Mô phỏng thực thi chi tiết MÃ NGUỒN GỐC từng bước với test case gây lỗi này.
      - Chỉ rõ giá trị đầu vào đang sử dụng.
      - Hiển thị từng dòng code gốc đang thực thi.
      - Hiển thị giá trị của các biến quan trọng sau mỗi bước.
      - Đánh dấu **CHÍNH XÁC** bước nào trong MÃ NGUỒN GỐC gây ra lỗi/kết quả sai.
      - Giải thích tại sao bước đó gây ra lỗi/kết quả sai.
    + Nếu bạn KHÔNG THỂ tìm thấy hoặc tạo ra một test case gây lỗi cho MÃ NGUỒN GỐC (ví dụ: mã nguồn gốc có vẻ đúng về mặt logic với các lỗi không thể hiện qua đầu vào đơn giản), hãy ghi rõ trong phần `input` của `error_case` là "Không tìm thấy trường hợp lỗi rõ ràng cho mã nguồn gốc." và có thể bỏ qua các bước mô phỏng chi tiết cho `error_case` hoặc cung cấp một mô phỏng rất ngắn gọn với một đầu vào thông thường nếu muốn.
  
  - **Trường hợp chạy đúng (Happy Path Simulation):**
    + Tìm hoặc tạo một ví dụ đầu vào (test case) khác mà MÃ NGUỒN GỐC sẽ hoạt động đúng và cho ra kết quả như mong đợi (happy path).
    + Nếu bạn xác định được một test case chạy đúng:
      - Mô phỏng thực thi chi tiết MÃ NGUỒN GỐC từng bước với test case này.
      - Chỉ rõ giá trị đầu vào đang sử dụng.
      - Hiển thị từng dòng code gốc đang thực thi.
      - Hiển thị giá trị của các biến quan trọng sau mỗi bước.
    + Nếu vì lý do nào đó không thể xác định một test case chạy đúng rõ ràng cho MÃ NGUỒN GỐC, hãy ghi rõ trong phần `input` của `happy_path_case` là "Không tìm thấy trường hợp chạy đúng rõ ràng cho mã nguồn gốc." và có thể bỏ qua các bước mô phỏng chi tiết.

  ## 4. Đánh giá tổng quát (Về mã nguồn gốc)
  - Tóm tắt về mã nguồn gốc, hiệu suất của nó, và đề xuất cải thiện chung (nếu có).
  
  **HƯỚNG DẪN TRẢ LỜI - CỰC KỲ QUAN TRỌNG:**
  
  **TOÀN BỘ PHẢN HỒI CỦA BẠN PHẢI LÀ MỘT ĐỐI TƯỢNG JSON HỢP LỆ DUY NHẤT.**
  **KHÔNG BAO GỒM bất kỳ văn bản giới thiệu, giải thích nào, hoặc các dấu markdown code fence (như ```json) trước hoặc sau đối tượng JSON.**
  
  **Yêu cầu chi tiết cho cấu trúc và nội dung JSON:**
  - Tất cả các giá trị chuỗi (string) trong JSON PHẢI được bao quanh bởi dấu ngoặc kép (`"`).
  - MỌI ký tự đặc biệt bên trong giá trị chuỗi PHẢI được escape đúng cách. Ví dụ:
    - Dấu ngoặc kép (`"`) trong chuỗi phải là `\\\"`.
    - Dấu gạch chéo ngược (`\\\\`) trong chuỗi phải là `\\\\\\\\`.
    - Ký tự xuống dòng mới phải là `\\\\n`.
    - Ký tự tab phải là `\\\\t`.
  - Các trường chứa mã nguồn (ví dụ: `fixed_code`, `code_line`) phải là một chuỗi JSON hợp lệ. KHÔNG sử dụng dấu backtick (`) để bao quanh giá trị của các trường này; thay vào đó, hãy đảm bảo mã nguồn là một phần của một chuỗi JSON được escape đúng cách.
  
  **Cấu trúc JSON bắt buộc (lưu ý tên trường `happy_path_case`):**
  ```json
  {{
    "analysis": {{  // Phân tích dựa trên mã nguồn gốc
      "syntax_errors": ["Danh sách các lỗi cú pháp..."],
      "logical_errors": ["Danh sách các lỗi logic..."],
      "runtime_errors": ["Danh sách các lỗi thời gian chạy tiềm ẩn..."],
      "meets_requirements": true/false
    }},
    "suggestions": [
      {{
        "line": số_dòng, 
        "error": "Mô tả lỗi chi tiết...",
        "fix": "Đề xuất sửa lỗi chi tiết...",
        "fixed_code": "Chỉ cung cấp CÁC DÒNG MÃ CẦN THAY ĐỔI hoặc một đoạn mã MINH HỌA NGẮN GỌN cho việc sửa lỗi. KHÔNG trả về toàn bộ mã nguồn đã sửa nếu không thực sự cần thiết. (Chuỗi JSON được escape đúng cách)."
      }}
    ],
    "simulation": {{ // Mô phỏng dựa trên mã nguồn gốc
      "error_case": {{
        "input": "Giá trị đầu vào gây lỗi cho mã gốc HOẶC 'Không tìm thấy trường hợp lỗi rõ ràng cho mã nguồn gốc.'",
        "steps": [
          {{
            "step": 1, 
            "code_line": "Dòng code GỐC đang thực thi...",
            "explanation": "Giải thích bước...",
            "variables": {{ 
              "tên_biến_1": "giá_trị_1",
              "tên_biến_2": "giá_trị_2"
            }},
            "is_error_step": false, 
            "error_explanation": null // Hoặc mô tả lỗi nếu bước này là bước lỗi
          }}
          // ... thêm các bước nếu có test case lỗi
        ],
        "result": "Kết quả sai/lỗi thu được từ mã gốc (nếu có test case lỗi)"
      }},
      "happy_path_case": {{ // Thay vì corrected_case
        "input": "Giá trị đầu vào chạy đúng cho mã gốc HOẶC 'Không tìm thấy trường hợp chạy đúng rõ ràng cho mã nguồn gốc.'",
        "steps": [
          {{
            "step": 1, 
            "code_line": "Dòng code GỐC đang thực thi...",
            "explanation": "Giải thích bước...",
            "variables": {{ 
              "tên_biến_1": "giá_trị_1",
              "tên_biến_2": "giá_trị_2"
            }}
          }}
          // ... thêm các bước nếu có test case chạy đúng
        ],
        "result": "Kết quả đúng thu được từ mã gốc (nếu có test case chạy đúng)"
      }}
    }},
    "evaluation": "Nhận xét tổng thể về mã nguồn gốc..."
  }}
  ```
  """
  return prompt

# Sửa hàm analyze_code_with_gemini để xử lý JSON đúng cách
def analyze_code_with_gemini(model_name, prompt_text):
  global gemini_model_global
  if not model_name or not gemini_model_global:
    return None, "Model hoặc Gemini client không được cấu hình."
  try:
    generation_config = {
      "temperature": 0.2,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 20480, 
    }
    
    response = gemini_model_global.generate_content(
      prompt_text,
      generation_config=generation_config
    )
    
    response_content = response.text.strip()
    # print(f"---- RAW RESPONSE ----\\n{response_content}\\n---------------------") # For debugging

    # 1. Extract JSON string from potential markdown block if present
    #    Or, if the model *only* returns JSON, this step might be bypassed.
    json_str = response_content
    if response_content.startswith("```json") and response_content.endswith("```"):
        json_str = response_content[len("```json"):-(len("```"))].strip()
    elif response_content.startswith("```") and response_content.endswith("```"):
        json_str = response_content[len("```"):-(len("```"))].strip()
    # If it wasn't in a markdown block, we assume json_str is the response_content itself,
    # hoping it's a direct JSON string as per the refined prompt.

    # print(f"---- EXTRACTED/RAW JSON STRING ----\\n{json_str}\\n----------------------------------") # For debugging

    # 2. Attempt to parse the JSON string directly
    try:
        result = json.loads(json_str)
        return result, None
    except json.JSONDecodeError as e_parse:
        # If parsing fails, it means the LLM didn't adhere to the strict JSON prompt
        error_message = f"Lỗi khi phân tích JSON từ phản hồi của Gemini: {str(e_parse)}\\n"
        error_message += f"Phản hồi nhận được (đã cố gắng trích xuất từ markdown nếu có):\\n{json_str}"
        # Include the original full response if it was different (e.g., markdown was stripped)
        if json_str != response_content:
            error_message += f"\\n\\nPhản hồi gốc đầy đủ từ Gemini:\\n{response_content}"
        return None, error_message

  except Exception as e_api_call:
    return None, f"Lỗi khi gọi Gemini API hoặc lỗi không xác định khác: {str(e_api_call)}"

# Convert text to HTML, escaping special characters and preserving line breaks
def text_to_html(text_content):
    if not text_content:
        return ""
    # Convert to string first to handle non-string values (like integers)
    text_content = str(text_content)
    return Markup(text_content.replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;')
                           .replace('\\n', '<br>')
                           .replace('  ', ' &nbsp;'))

# Hiển thị kết quả phân tích - This will now return HTML content or data for a template
# For now, we'll adapt it to be used by the template later, or simplify it.
# The main logic will be in the template itself for display.

@app.route('/', methods=['GET'])
def index():
  if not model_name_global:
    api_status = "API Key không hợp lệ hoặc model không khả dụng. Vui lòng kiểm tra console."
  else:
    api_status = f"API Key hợp lệ. Model: {model_name_global}"
  return render_template('index.html', api_status=api_status)

@app.route('/analyze', methods=['POST'])
def analyze():
  api_key = request.form.get('api_key', '').strip()
  ok, err = validate_and_consume_key(api_key)
  if not ok:
      # quay về index với thông báo lỗi
      return render_template('index.html', error_message=err)

  if not model_name_global:
    return render_template('results.html', error_message="Lỗi: Gemini API chưa được cấu hình đúng.", text_to_html=text_to_html)

  problem_description = request.form.get('problem_description', '')
  source_code = request.form.get('source_code', '')
  language = request.form.get('language', 'Python')

  if not problem_description.strip():
    return render_template('results.html', error_message="Vui lòng nhập đề bài.", text_to_html=text_to_html)
  if not source_code.strip():
    return render_template('results.html', error_message="Vui lòng nhập mã nguồn.", text_to_html=text_to_html)

  # Tạo prompt
  current_prompt = create_prompt(problem_description, source_code, language)
  
  # Gửi đến Gemini API
  result, error = analyze_code_with_gemini(model_name_global, current_prompt)
  
  if error:
    return render_template('results.html', error_message=f"Lỗi phân tích: {error}", text_to_html=text_to_html)
  
  if result:
    # Prepare data for the template (example, you might need to adjust based on your actual result structure)
    # The 'text_to_html' function can be used in the template with Jinja2 filters if needed
    # or applied here before passing to the template.
    return render_template('results.html', result=result, language=language, text_to_html=text_to_html)
  else:
    return render_template('results.html', error_message="Không thể phân tích mã nguồn. Vui lòng thử lại.", text_to_html=text_to_html)

# Chạy ứng dụng Flask
if __name__ == "__main__":
  if setup_gemini_api():  # Setup API key and model when app starts
    app.run(debug=True, port=5001)
  else:
    print("Không thể khởi chạy ứng dụng do lỗi cấu hình API. Vui lòng kiểm tra thông báo lỗi ở trên.")
