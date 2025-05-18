# @title **Trợ lý Lập trình Thông minh (Smart Programming Assistant) - Phiên bản 1.0**

# Cài đặt thư viện cần thiết
# Make sure to install google-generativeai: pip install google-generativeai
# Make sure to install Flask: pip install Flask

import os
import re
import textwrap
import openai # Replaced google.generativeai
from openai import OpenAI, APIError, AuthenticationError, RateLimitError # Import specific exceptions
import json
from flask import Flask, render_template, request
from markupsafe import Markup

app = Flask(__name__)

# Global variables
model_name_global = None
openai_client_global = None # Global OpenAI client

# Thiết lập UI - No longer directly used for console, CSS will be in HTML
# def setup_css():
#   print("CSS setup would happen here in a GUI environment.")

# Hiển thị tiêu đề ứng dụng - Will be part of HTML template
# def display_header():
#   print("\\n" + "="*40)
#   print("Trợ lý Lập trình Thông minh")
#   print("Smart Programming Assistant - v1.0")
#   print("="*40 + "\\n")

# Cấu hình API key cho OpenAI
def setup_openai_api():
  global model_name_global, openai_client_global # Add openai_client_global
  try:
    api_key = "YOUR_OPENAI_API_KEY_HERE" # Key removed for security
    
    # Initialize the OpenAI client and store it globally
    openai_client_global = OpenAI(api_key=api_key)
    
    model_to_use = "gpt-4"
    # Test the connection by making a simple call, e.g., listing models (optional but good practice)
    # For example: openai_client_global.models.list()
    # This will raise an AuthenticationError if the key is bad.
    try:
        openai_client_global.models.list() # Simple call to test authentication
        print(f"✅ OpenAI API key configured and authenticated! Using model: {model_to_use}")
    except AuthenticationError as auth_err:
        print(f"❌ Lỗi xác thực OpenAI API: {str(auth_err)}")
        print("Vui lòng kiểm tra lại API key.")
        model_name_global = None
        openai_client_global = None
        return False
    except APIError as api_err:
        print(f"❌ Lỗi OpenAI API khi kiểm tra key: {str(api_err)}")
        model_name_global = None
        openai_client_global = None
        return False
        
    model_name_global = model_to_use
    return True
  except Exception as e:
    print(f"❌ Lỗi khi cấu hình OpenAI API: {str(e)}")
    model_name_global = None
    openai_client_global = None # Ensure client is None on error
    return False

# Tạo các prompt để làm việc với mã nguồn C và Python
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
  - Mô phỏng quá trình thực thi mã nguồn từng bước (giải thích dưới dạng văn bản).
  - Ở mỗi bước, hiển thị:
    + Dòng code đang được "thực thi"
    + Trạng thái của các biến quan trọng (tên và giá trị)
    + Luồng điều khiển (rẽ nhánh if/else, vòng lặp)
  
  ## 4. Đánh giá tổng quát
  - Tóm tắt về mã nguồn, hiệu suất, và đề xuất cải thiện (nếu có).
  
  Trả lời bằng định dạng JSON với cấu trúc sau:
  ```
  {{
    "analysis": {{
      "syntax_errors": [Danh sách các lỗi cú pháp],
      "logical_errors": [Danh sách các lỗi logic],
      "runtime_errors": [Danh sách các lỗi thời gian chạy tiềm ẩn],
      "meets_requirements": true/false
    }},
    "suggestions": [
      {{
        "line": số_dòng,
        "error": "Mô tả lỗi",
        "fix": "Đề xuất sửa lỗi",
        "fixed_code": "Đoạn mã đã sửa"
      }}
    ],
    "simulation": [
      {{
        "step": 1,
        "code_line": "Dòng code đang thực thi",
        "explanation": "Giải thích",
        "variables": {{
          "tên_biến_1": "giá_trị_1",
          "tên_biến_2": "giá_trị_2"
        }}
      }}
    ],
    "evaluation": "Nhận xét tổng thể về mã nguồn"
  }}
  ```
  
  Trả lời chỉ sử dụng định dạng JSON như trên, không thêm bất kỳ nội dung nào khác.
  """
  return prompt

# Hàm gửi prompt đến OpenAI API và nhận kết quả
def analyze_code_with_openai(model_name, prompt_text):
  global openai_client_global # Access the global client
  if not model_name or not openai_client_global:
    return None, "Model hoặc OpenAI client không được cấu hình."
  try:
    response = openai_client_global.chat.completions.create( # Use the client and new method
        model=model_name,
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )
    
    response_content = response.choices[0].message.content
    
    try:
      result = json.loads(response_content)
      return result, None
    except json.JSONDecodeError:
      json_match = re.search(r'```json\s*([\s\S]*?)\s*```|```\s*([\s\S]*?)\s*```|({[\s\S]*})', response_content)
      if json_match:
        json_str = next(group for group in json_match.groups() if group)
        try:
          result = json.loads(json_str)
          return result, None
        except json.JSONDecodeError as e_inner:
          return None, f"Lỗi khi parse JSON trích xuất từ OpenAI: {str(e_inner)}\nPhản hồi gốc: {response_content}"
      else:
        return None, f"Không thể trích xuất JSON từ phản hồi OpenAI.\nPhản hồi nhận được:\n{response_content}"

  except APIError as e:
    return None, f"Lỗi OpenAI API: {str(e)}"
  except AuthenticationError as e: # Should be caught during setup, but good to have
    return None, f"Lỗi xác thực OpenAI API: {str(e)}"
  except RateLimitError as e:
    return None, f"Lỗi giới hạn tỷ lệ OpenAI API: {str(e)}"
  except Exception as e:
    return None, f"Lỗi không xác định khi gọi OpenAI API: {str(e)}"

# Convert text to HTML, escaping special characters and preserving line breaks
def text_to_html(text_content):
    if not text_content:
        return ""
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
    return render_template('results.html', error_message="Lỗi: OpenAI API chưa được cấu hình đúng.", text_to_html=text_to_html)

  problem_description = request.form.get('problem_description', '')
  source_code = request.form.get('source_code', '')
  language = request.form.get('language', 'Python')

  if not problem_description.strip():
    return render_template('results.html', error_message="Vui lòng nhập đề bài.", text_to_html=text_to_html)
  if not source_code.strip():
    return render_template('results.html', error_message="Vui lòng nhập mã nguồn.", text_to_html=text_to_html)

  # Tạo prompt
  current_prompt = create_prompt(problem_description, source_code, language)
  
  # Gửi đến OpenAI API
  result, error = analyze_code_with_openai(model_name_global, current_prompt)
  
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
  if setup_openai_api(): # Setup API key and model when app starts
    app.run(debug=True, port=5001) # Changed port to 5001
  else:
    print("Không thể khởi chạy ứng dụng do lỗi cấu hình API. Vui lòng kiểm tra thông báo lỗi ở trên.")
