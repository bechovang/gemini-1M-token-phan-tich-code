# @title **Trợ lý Lập trình Thông minh (Smart Programming Assistant) - Phiên bản 1.0**

# Cài đặt thư viện cần thiết
# Make sure to install google-generativeai: pip install google-generativeai
# Make sure to install Flask: pip install Flask

import os
import re
import textwrap
import google.generativeai as genai  # Use Google's Gemini API
import json
from flask import Flask, render_template, request
from markupsafe import Markup

app = Flask(__name__)

# Global variables
model_name_global = None
gemini_model_global = None  # Global Gemini model

# Thiết lập UI - No longer directly used for console, CSS will be in HTML
# def setup_css():
#   print("CSS setup would happen here in a GUI environment.")

# Hiển thị tiêu đề ứng dụng - Will be part of HTML template
# def display_header():
#   print("\\n" + "="*40)
#   print("Trợ lý Lập trình Thông minh")
#   print("Smart Programming Assistant - v1.0")
#   print("="*40 + "\\n")

# Cấu hình API key cho Gemini
def setup_gemini_api():
  global model_name_global, gemini_model_global
  try:
    api_key = "AIzaSyAa7zBQuCGvrsoQ3WF75JL76_0ZiD4_w6g"
    
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
  
  # Mã nguồn {language}:
  ```{language}
  {source_code}
  ```
  
  Hãy thực hiện các nhiệm vụ sau:
  
  ## 1. Phân tích mã nguồn
  - Phân tích cú pháp và ngữ nghĩa của mã nguồn {language}.
  - Xác định xem mã có thỏa mãn yêu cầu của đề bài không.
  - Tìm và liệt kê tất cả các lỗi: lỗi cú pháp, lỗi logic, lỗi thời gian chạy tiềm ẩn.
  
  ## 2. Gợi ý sửa lỗi
  - Giải thích chi tiết từng lỗi đã tìm thấy (nguyên nhân, dòng code có lỗi).
  - Đề xuất cách sửa lỗi cụ thể.
  - Cung cấp đoạn mã đã sửa (nếu cần).
  
  ## 3. Mô phỏng thực thi từng bước
  - **Bắt buộc**: Thực hiện mô phỏng với **CẢ HAI** trường hợp sau:
    + **Trường hợp lỗi**: Chọn một đầu vào cụ thể sẽ gây ra lỗi hoặc kết quả sai. Mô phỏng thực thi chi tiết với đầu vào này để chỉ ra lỗi.
    + **Trường hợp đúng** (Sau khi đã sửa lỗi): Mô phỏng thực thi với một đầu vào khác để chứng minh code đã sửa hoạt động đúng.
  
  - **Cho mỗi trường hợp**: Thực hiện mô phỏng chi tiết từng bước:
    + Chỉ rõ giá trị đầu vào đang sử dụng
    + Hiển thị từng dòng code đang thực thi
    + Hiển thị giá trị của các biến sau mỗi bước
    + Với trường hợp lỗi: Đánh dấu **CHÍNH XÁC** bước nào gây ra lỗi
    + Giải thích tại sao bước đó gây ra lỗi
  
  ## 4. Đánh giá tổng quát
  - Tóm tắt về mã nguồn, hiệu suất, và đề xuất cải thiện (nếu có).
  
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
  
  **Cấu trúc JSON bắt buộc:**
  ```json
  {{
    "analysis": {{
      "syntax_errors": ["Danh sách các lỗi cú pháp dưới dạng chuỗi"],
      "logical_errors": ["Danh sách các lỗi logic dưới dạng chuỗi"],
      "runtime_errors": ["Danh sách các lỗi thời gian chạy tiềm ẩn dưới dạng chuỗi"],
      "meets_requirements": true/false
    }},
    "suggestions": [
      {{
        "line": số_dòng, // integer
        "error": "Mô tả lỗi chi tiết (chuỗi JSON được escape đúng)",
        "fix": "Đề xuất sửa lỗi chi tiết (chuỗi JSON được escape đúng)",
        "fixed_code": "Đoạn mã đã sửa (TOÀN BỘ MÃ NGUỒN được đặt trong một chuỗi JSON duy nhất, được escape đúng cách, ví dụ: `#include <stdio.h>\\nint main() {{...}}`)"
      }}
    ],
    "simulation": {{
      "error_case": {{
        "input": "Giá trị đầu vào gây lỗi (chuỗi JSON)",
        "steps": [
          {{
            "step": 1, // integer
            "code_line": "Dòng code đang thực thi (chuỗi JSON được escape đúng)",
            "explanation": "Giải thích bước (chuỗi JSON được escape đúng)",
            "variables": {{ // Đối tượng chứa các biến và giá trị của chúng (chuỗi JSON)
              "tên_biến_1": "giá_trị_1",
              "tên_biến_2": "giá_trị_2"
            }},
            "is_error_step": false // boolean
          }},
          {{
            "step": 2, // integer
            "code_line": "Dòng code đang thực thi (chuỗi JSON được escape đúng)",
            "explanation": "Giải thích bước (chuỗi JSON được escape đúng)",
            "variables": {{ 
              "tên_biến_1": "giá_trị_1",
              "tên_biến_2": "giá_trị_2"
            }},
            "is_error_step": true, // boolean
            "error_explanation": "Chi tiết lý do tại sao lỗi xảy ra ở bước này (chuỗi JSON được escape đúng)"
          }}
        ],
        "result": "Kết quả sai/lỗi thu được (chuỗi JSON)"
      }},
      "corrected_case": {{
        "input": "Giá trị đầu vào chạy đúng (chuỗi JSON)",
        "steps": [
          {{
            "step": 1, // integer
            "code_line": "Dòng code đã sửa đang thực thi (chuỗi JSON được escape đúng)",
            "explanation": "Giải thích bước (chuỗi JSON được escape đúng)",
            "variables": {{ 
              "tên_biến_1": "giá_trị_1",
              "tên_biến_2": "giá_trị_2"
            }}
          }}
        ],
        "result": "Kết quả đúng thu được (chuỗi JSON)"
      }}
    }},
    "evaluation": "Nhận xét tổng thể về mã nguồn (chuỗi JSON được escape đúng)"
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
