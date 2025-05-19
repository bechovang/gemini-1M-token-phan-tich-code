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
  - **Quan trọng**: Dựa vào "Phân tích mã nguồn" (mục 1) và "Gợi ý sửa lỗi" (mục 2):
    - Nếu có lỗi logic hoặc lỗi thời gian chạy tiềm ẩn được xác định có thể dẫn đến hành vi sai với một số đầu vào nhất định:
      + **Chọn một ví dụ đầu vào cụ thể (test case) sẽ gây ra lỗi đó.**
      + **Mô phỏng thực thi từng bước với test case gây lỗi này.**
      + Trong quá trình mô phỏng, khi đến bước gây ra lỗi, hãy chỉ rõ: "Tại bước này, với đầu vào [ví dụ đầu vào], mã nguồn sẽ [mô tả hành vi sai] do [giải thích nguyên nhân dựa trên lỗi logic đã xác định]."
    - Nếu không có lỗi logic nào được xác định hoặc các lỗi không dẫn đến hành vi sai rõ ràng trong thực thi (ví dụ: chỉ là vấn đề về tối ưu hoặc coding style), hoặc nếu mã đã được coi là đúng:
      + Mô phỏng với một ví dụ đầu vào "happy path" (trường hợp chạy đúng).
      + Nếu mã nguồn thực thi thành công và đúng yêu cầu, hãy kết thúc với thông báo "Chúc mừng, mã nguồn hoạt động chính xác với đầu vào này!"
  
  - Ở mỗi bước mô phỏng, hiển thị:
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
        }},
        "error": null,  // "null" nếu không có lỗi ở bước này, mô tả lỗi nếu có
        "is_problem_step": false // true nếu bước này là nơi lỗi logic/runtime được kích hoạt
      }}
    ],
    "execution_result": "success/failure/not_applicable",  // Kết quả thực thi chung của test case mô phỏng
    "simulated_input": "[Giá trị đầu vào được sử dụng cho mô phỏng]", // Thêm trường này
    "success_message": "Chúc mừng, mã nguồn hoạt động chính xác!",  // Chỉ có khi thành công
    "evaluation": "Nhận xét tổng thể về mã nguồn"
  }}
  ```
  
  Trả lời chỉ sử dụng định dạng JSON như trên, không thêm bất kỳ nội dung nào khác.
  """
  return prompt

# Hàm gửi prompt đến Gemini API và nhận kết quả
def analyze_code_with_gemini(model_name, prompt_text):
  global gemini_model_global
  if not model_name or not gemini_model_global:
    return None, "Model hoặc Gemini client không được cấu hình."
  try:
    # Generate content with Gemini
    response = gemini_model_global.generate_content(prompt_text)
    
    # Get the response text
    response_content = response.text
    
    try:
      # Try to parse the response as JSON directly
      result = json.loads(response_content)
      return result, None
    except json.JSONDecodeError as e_direct_parse:
      # If direct parsing fails, try to extract JSON from markdown code blocks or other formats
      # and then attempt to fix common issues like unescaped newlines in code snippets.
      json_match = re.search(r'```json\s*([\s\S]*?)\s*```|```\s*([\s\S]*?)\s*```|({[\s\S]*})', response_content)
      if json_match:
        json_str = next(group for group in json_match.groups() if group)
        
        # Attempt to fix unescaped newlines within "fixed_code" fields
        # This is a common issue with LLM-generated JSON containing code.
        # def escape_newlines_in_fixed_code(match): # This function was defined but not used, consider removing or implementing
        #     # The content of fixed_code is in match.group(1)
        #     # Escape newlines and also backslashes that are not already part of an escape sequence
        #     escaped_content = match.group(1).replace('\\', '\\\\').replace('\n', '\\n').replace('\"', '\\\"')
        #     return f'"fixed_code": "{escaped_content}"'

        try:
            json_str_fixed = json_str # Start with original extracted string

            # 1. Replace backtick-enclosed strings for "fixed_code" with proper double-quoted strings,
            #    escaping inner double quotes and backslashes.
            def replace_backtick_string(match):
                code_content = match.group(1)
                # Escape backslashes first, then double quotes
                escaped_code_content = code_content.replace('\\', '\\\\').replace('"', '\\"')
                return f'"fixed_code": "{escaped_code_content}"'
            
            # This regex looks for "fixed_code": `...` (non-greedy) a
            json_str_fixed = re.sub(r'(\"fixed_code\":\s*)\`([\\s\\S]*?)\`', replace_backtick_string, json_str_fixed)
            
            # 2. Iteratively replace unescaped newlines that are likely part of string content
            # This pattern looks for `\n` not preceded by another backslash.
            # It also tries to handle `\r\n`.
            json_str_fixed = re.sub(r'(?<!\\)(\\r)?\\n', r'\\\\n', json_str_fixed)
            
            # If you still face issues with other characters, you might add more specific regex fixes here for:
            # - Unescaped backslashes not part of a valid escape sequence (if not covered by replace_backtick_string)
            
            result = json.loads(json_str_fixed)
            return result, None
        except json.JSONDecodeError as e_inner:
          # If fixing also fails, return the original error and the attempted fixed string for debugging
          return None, f"Lỗi khi parse JSON trích xuất từ Gemini (sau khi thử sửa): {str(e_inner)}\nPhản hồi gốc: {response_content}\nChuỗi JSON đã thử sửa: {json_str_fixed}"
      else:
        # If no JSON block is found at all, use the original parsing error
        return None, f"Không thể trích xuất JSON từ phản hồi Gemini. Lỗi parse ban đầu: {str(e_direct_parse)}\nPhản hồi nhận được:\n{response_content}"

  except Exception as e:
    return None, f"Lỗi khi gọi Gemini API: {str(e)}"

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
