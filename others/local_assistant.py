# -*- coding: utf-8 -*-
"""
# 🤖 Trợ Lý Lập Trình Thông Minh v1.1 
### Smart Programming Assistant
"""

# ===== PHẦN CÀI ĐẶT THƯ VIỆN =====
# Các thư viện này cần được cài đặt thủ công trong môi trường của bạn, ví dụ:
# pip install google-generativeai tiktoken pytest

# Import các thư viện cần thiết
import os
import sys
import tempfile
import zipfile
import io
import difflib
import re
import json
import time
import subprocess
import unittest
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import google.generativeai as genai
import tiktoken
import pytest
import traceback

# ===== PHẦN CẤU HÌNH =====

class Config:
    """Lớp chứa các cấu hình cho ứng dụng"""
    # Các ngôn ngữ được hỗ trợ
    SUPPORTED_LANGUAGES = ["c", "python"]
    
    # Cấu hình mô hình
    MODEL_NAME = "models/gemini-1.5-pro-latest"  # Mô hình 1M token
    TEMPERATURE = 0.2
    MAX_OUTPUT_TOKENS = 8192
    TOP_P = 0.95
    TOP_K = 64
    
    # Cấu hình hiển thị
    DEFAULT_DETAIL_LEVEL = "medium"  # low, medium, high
    MAX_CONTEXT_LENGTH = 900000  # Giới hạn ngữ cảnh để tối ưu token
    
    # Đường dẫn mặc định
    TEMP_DIR = tempfile.mkdtemp()

# ===== PHẦN TIỆN ÍCH =====

class Utils:
    """Các hàm tiện ích"""
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Đếm số lượng token trong text"""
        encoder = tiktoken.encoding_for_model("gpt-4")  # Sử dụng encoder của GPT-4 để ước lượng
        return len(encoder.encode(text))
    
    @staticmethod
    def read_file(filepath: str) -> str:
        """Đọc nội dung file văn bản"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    @staticmethod
    def write_file(filepath: str, content: str) -> bool:
        """Ghi nội dung vào file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            return False
    
    @staticmethod
    def extract_code_from_markdown(text: str) -> str:
        """Trích xuất code từ markdown"""
        pattern = r"```(?:\w+)?\s*([\s\S]*?)\s*```"
        matches = re.findall(pattern, text)
        if matches:
            return "\n".join(matches)
        return text
    
    @staticmethod
    def compare_code_versions(old_code: str, new_code: str) -> str:
        """So sánh hai phiên bản code và trả về diff dưới dạng text"""
        diff = difflib.unified_diff(
            old_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            fromfile="old_version",
            tofile="new_version"
        )
        return ''.join(diff)
    
    @staticmethod
    def create_displayable_diff(old_code: str, new_code: str) -> str:
        """Tạo diff đẹp để hiển thị trên notebook"""
        diff = difflib.ndiff(old_code.splitlines(), new_code.splitlines())
        result = []
        
        for line in diff:
            if line.startswith('+ '):
                result.append(f"<span style='color: green'>{line}</span>")
            elif line.startswith('- '):
                result.append(f"<span style='color: red'>{line}</span>")
            elif line.startswith('? '):
                continue
            else:
                result.append(line)
        
        return '<br>'.join(result)

    @staticmethod
    def unzip_file(zip_path: str, extract_to: str) -> List[str]:
        """Giải nén file zip và trả về danh sách các file được giải nén"""
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                extracted_files = zip_ref.namelist()
        except Exception as e:
            print(f"Error extracting zip file: {str(e)}")
        
        return extracted_files

    @staticmethod
    def get_relevant_language_files(directory: str, language: str) -> List[str]:
        """Tìm các file của ngôn ngữ được chỉ định trong thư mục"""
        extensions = {
            "c": [".c", ".h"],
            "python": [".py"]
        }
        
        if language not in extensions:
            return []
        
        relevant_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                for ext in extensions[language]:
                    if file.endswith(ext):
                        relevant_files.append(os.path.join(root, file))
        
        return relevant_files

# ===== PHẦN CỐT LÕI =====

class GeminiClient:
    """Xử lý tương tác với Gemini API"""
    
    def __init__(self, api_key: str):
        """Khởi tạo client với API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            generation_config={
                "temperature": Config.TEMPERATURE,
                "max_output_tokens": Config.MAX_OUTPUT_TOKENS,
                "top_p": Config.TOP_P,
                "top_k": Config.TOP_K
            }
        )
        self.conversation = self.model.start_chat(history=[])
    
    def query(self, prompt: str) -> str:
        """Gửi prompt và nhận phản hồi từ model"""
        try:
            response = self.conversation.send_message(prompt)
            return response.text
        except Exception as e:
            error_msg = f"Error querying Gemini API: {str(e)}"
            print(error_msg)
            return error_msg
    
    def add_to_history(self, role: str, content: str):
        """Thêm tin nhắn vào lịch sử hội thoại"""
        # Thêm tin nhắn vào lịch sử
        if role.lower() == "user":
            self.conversation.history.append({"role": "user", "parts": [content]})
        elif role.lower() == "model":
            self.conversation.history.append({"role": "model", "parts": [content]})
    
    def clear_history(self):
        """Xóa lịch sử hội thoại"""
        self.conversation = self.model.start_chat(history=[])
    
    def get_token_count(self) -> int:
        """Ước tính số lượng token trong lịch sử hội thoại"""
        full_text = ""
        for message in self.conversation.history:
            if isinstance(message["parts"], list):
                for part in message["parts"]:
                    if isinstance(part, str):
                        full_text += part
                    elif hasattr(part, "text"):
                        full_text += part.text
            elif isinstance(message["parts"], str):
                full_text += message["parts"]
        
        return Utils.count_tokens(full_text)
    
    def optimize_context(self):
        """Tối ưu ngữ cảnh khi quá dài"""
        token_count = self.get_token_count()
        
        if token_count > Config.MAX_CONTEXT_LENGTH:
            # Giữ lại tin nhắn đầu tiên (system prompt) và nửa sau của lịch sử
            retain_count = len(self.conversation.history) // 2
            self.conversation.history = [
                self.conversation.history[0],
                *self.conversation.history[-retain_count:]
            ]
            print(f"Context optimized. Retained {retain_count+1} messages.")

class CodeExecutor:
    """Thực thi và phân tích mã nguồn"""
    
    @staticmethod
    def execute_python(code: str, input_data: str = "") -> Dict[str, Any]:
        """Thực thi mã Python và trả về kết quả"""
        result = {
            "output": "",
            "error": None,
            "status": "success"
        }
        
        try:
            # Tạo file tạm thời để thực thi
            temp_file = os.path.join(Config.TEMP_DIR, "temp_code.py")
            Utils.write_file(temp_file, code)
            
            # Thực thi file python với input_data nếu có
            process = subprocess.Popen(
                [sys.executable, temp_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=input_data, timeout=30)
            
            result["output"] = stdout
            if stderr:
                result["error"] = stderr
                result["status"] = "error"
            
        except subprocess.TimeoutExpired:
            result["error"] = "Execution timed out (30s limit)"
            result["status"] = "timeout"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
        
        return result
    
    @staticmethod
    def compile_and_execute_c(code: str, input_data: str = "") -> Dict[str, Any]:
        """Biên dịch và thực thi mã C và trả về kết quả"""
        result = {
            "output": "",
            "error": None,
            "compilation_error": None,
            "status": "success"
        }
        
        try:
            # Tạo file tạm thời để thực thi
            temp_c_file = os.path.join(Config.TEMP_DIR, "temp_code.c")
            temp_exe_file = os.path.join(Config.TEMP_DIR, "temp_code")
            
            Utils.write_file(temp_c_file, code)
            
            # Biên dịch mã C
            compile_process = subprocess.Popen(
                ["gcc", temp_c_file, "-o", temp_exe_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            _, compile_stderr = compile_process.communicate(timeout=30)
            
            if compile_process.returncode != 0:
                result["compilation_error"] = compile_stderr
                result["status"] = "compilation_error"
                return result
            
            # Thực thi chương trình sau khi biên dịch
            if os.path.exists(temp_exe_file):
                run_process = subprocess.Popen(
                    [temp_exe_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = run_process.communicate(input=input_data, timeout=30)
                
                result["output"] = stdout
                if stderr:
                    result["error"] = stderr
                    result["status"] = "runtime_error"
            else:
                result["error"] = "Executable not found after compilation"
                result["status"] = "error"
            
        except subprocess.TimeoutExpired:
            result["error"] = "Execution timed out (30s limit)"
            result["status"] = "timeout"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
        
        return result
    
    @staticmethod
    def run_code(language: str, code: str, input_data: str = "") -> Dict[str, Any]:
        """Chạy mã nguồn dựa vào ngôn ngữ và trả về kết quả"""
        if language.lower() == "python":
            return CodeExecutor.execute_python(code, input_data)
        elif language.lower() == "c":
            return CodeExecutor.compile_and_execute_c(code, input_data)
        else:
            return {
                "output": "",
                "error": f"Unsupported language: {language}",
                "status": "error"
            }
    
    @staticmethod
    def generate_test_cases(language: str, code: str, description: str) -> Dict[str, str]:
        """Sinh test case dựa vào mô tả yêu cầu và mã nguồn"""
        test_cases = {}
        
        if language.lower() == "python":
            # Tạo file tạm thời
            module_name = "temp_code"
            temp_file = os.path.join(Config.TEMP_DIR, f"{module_name}.py")
            Utils.write_file(temp_file, code)
            
            # Tạo test file
            test_file_content = f"""
import unittest
import sys
from pathlib import Path
import importlib.util

# Import module cần test
sys.path.append('{Config.TEMP_DIR}')
spec = importlib.util.spec_from_file_location("{module_name}", "{temp_file}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestGeneratedCases(unittest.TestCase):
    # Test cases sẽ được thêm ở đây
    
    def test_basic_functionality(self):
        # Đây là test case cơ bản
        pass

if __name__ == '__main__':
    unittest.main()
"""
            test_file = os.path.join(Config.TEMP_DIR, f"test_{module_name}.py")
            Utils.write_file(test_file, test_file_content)
            
            test_cases = {
                "unit_test": test_file_content,
                "pytest": f"# Pytest cho {module_name}\n\n# Sẽ thêm test cases\n\ndef test_basic():\n    # Test case cơ bản\n    pass"
            }
        
        elif language.lower() == "c":
            # Tạo file test cơ bản cho C
            test_file_content = """
#include <stdio.h>
#include <assert.h>

// Test cases cho chương trình C
void run_tests() {
    // Các test case sẽ được thêm ở đây
    printf("Running tests...\n");
    
    // Test case mẫu
    // assert(function_to_test(input) == expected_output);
    
    printf("All tests passed!\n");
}

int main() {
    run_tests();
    return 0;
}
"""
            test_file = os.path.join(Config.TEMP_DIR, "test_program.c")
            Utils.write_file(test_file, test_file_content)
            
            test_cases = {
                "assert_tests": test_file_content
            }
        
        return test_cases

class CodeAnalyzer:
    """Phân tích mã nguồn và tìm lỗi"""
    
    def __init__(self, gemini_client: GeminiClient):
        """Khởi tạo với client Gemini"""
        self.gemini_client = gemini_client
    
    def analyze_code(self, language: str, code: str, requirement: str) -> Dict[str, Any]:
        """Phân tích mã nguồn và trả về thông tin chi tiết"""
        
        # 1. Phân tích lỗi cú pháp
        syntax_result = self._check_syntax(language, code)
        
        # 2. Chạy code để tìm runtime errors
        execution_result = CodeExecutor.run_code(language, code)
        
        # 3. Phân tích code dựa vào yêu cầu và kết quả ở trên
        analysis_prompt = f"""
# YÊU CẦU PHÂN TÍCH MÃ NGUỒN 

## Ngôn ngữ: {language}

## Mô tả yêu cầu:
{requirement}

## Mã nguồn cần phân tích:
```{language}
{code}
```

## Thông tin thêm:
- Kết quả kiểm tra cú pháp: {syntax_result["status"]}
- Chi tiết lỗi cú pháp: {syntax_result.get("error", "Không có")}
- Kết quả thực thi: {execution_result["status"]}
- Output: {execution_result.get("output", "Không có")}
- Runtime error: {execution_result.get("error", "Không có")}
- Lỗi biên dịch (cho C): {execution_result.get("compilation_error", "Không áp dụng")}

## YÊU CẦU PHÂN TÍCH:
1. Phân tích chính xác dựa trên các lỗi đã phát hiện 
2. Đánh giá mã nguồn so với yêu cầu đề bài
3. Nhận diện và giải thích các lỗi cú pháp, lỗi logic, và runtime errors
4. Đề xuất cách sửa cụ thể cho từng lỗi
5. Đánh giá độ hiệu quả của giải pháp và tối ưu hóa nếu cần

## ĐỊNH DẠNG PHẢN HỒI:
Tạo phản hồi dưới dạng JSON với các trường:
- "syntax_issues": [danh sách các vấn đề cú pháp, mỗi mục gồm "line", "description", "fix"]
- "logic_issues": [danh sách các vấn đề logic, mỗi mục gồm "description", "affected_lines", "fix"]
- "runtime_issues": [danh sách các vấn đề runtime, mỗi mục gồm "description", "fix"]
- "requirement_compliance": đánh giá mức độ đáp ứng yêu cầu (0-100%)
- "optimizations": [đề xuất tối ưu hóa]
- "suggested_fixes": mã nguồn đã được sửa hoàn chỉnh
- "explanation": diễn giải tổng quan về các vấn đề và giải pháp

Trả về KẾT QUẢ dưới định dạng JSON HỢP LỆ.
"""
        
        analysis_response = self.gemini_client.query(analysis_prompt)
        
        # Trích xuất phản hồi JSON từ kết quả
        try:
            # Tìm JSON trong phản hồi
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', analysis_response)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Nếu không tìm thấy trong code block, thử lấy toàn bộ nội dung
                json_str = analysis_response
            
            # Parse JSON
            analysis_result = json.loads(json_str)
        except json.JSONDecodeError:
            # Nếu không parse được, trả về kết quả dạng text
            analysis_result = {
                "syntax_issues": [],
                "logic_issues": [],
                "runtime_issues": [],
                "requirement_compliance": "Unknown",
                "optimizations": [],
                "suggested_fixes": code,  # Giữ nguyên code
                "explanation": analysis_response  # Sử dụng toàn bộ phản hồi làm giải thích
            }
        
        return {
            "syntax_check": syntax_result,
            "execution_result": execution_result,
            "analysis": analysis_result
        }
    
    def _check_syntax(self, language: str, code: str) -> Dict[str, Any]:
        """Kiểm tra lỗi cú pháp của mã nguồn"""
        result = {
            "status": "success",
            "error": None
        }
        
        if language.lower() == "python":
            try:
                compile(code, "<string>", "exec")
            except SyntaxError as e:
                result["status"] = "error"
                result["error"] = str(e)
                result["line"] = e.lineno
                result["offset"] = e.offset
                result["text"] = e.text
        
        elif language.lower() == "c":
            # Tạo file tạm thời
            temp_file = os.path.join(Config.TEMP_DIR, "syntax_check.c")
            Utils.write_file(temp_file, code)
            
            # Chỉ kiểm tra cú pháp mà không biên dịch
            process = subprocess.Popen(
                ["gcc", "-fsyntax-only", temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            _, stderr = process.communicate()
            
            if stderr:
                result["status"] = "error"
                result["error"] = stderr
        
        return result
    
    def simulate_execution(self, language: str, code: str, detail_level: str = "medium") -> str:
        """Mô phỏng thực thi mã nguồn từng bước"""
        
        simulation_prompt = f"""
# YÊU CẦU MÔ PHỎNG THỰC THI MÃ NGUỒN

## Ngôn ngữ: {language}

## Mã nguồn cần mô phỏng:
```{language}
{code}
```

## Mức độ chi tiết: {detail_level} (low/medium/high)

## YÊU CẦU MÔ PHỎNG:
Mô phỏng quá trình thực thi mã nguồn trên TỪNG BƯỚC, bao gồm:
1. Dòng code thực thi
2. Trạng thái biến (tên, kiểu, giá trị) sau mỗi thay đổi
3. Luồng điều khiển (if/else, loop, return)
4. Cấu trúc bộ nhớ (stack, heap cho C hoặc các đối tượng cho Python)

## Chi tiết dựa trên mức độ:
- LOW: Chỉ thể hiện các biến quan trọng và luồng điều khiển
- MEDIUM: Thêm thông tin về tất cả biến và stack đơn giản
- HIGH: Chi tiết đầy đủ về bộ nhớ, con trỏ (cho C), và các đối tượng (cho Python)

## ĐỊNH DẠNG PHẢN HỒI:
Tạo bảng mô phỏng với các cột: Bước, Dòng code, Biến được thay đổi, Trạng thái bộ nhớ, Ghi chú.
Sử dụng markdown để định dạng.
"""
        
        simulation_response = self.gemini_client.query(simulation_prompt)
        return simulation_response
    
    def suggest_test_cases(self, language: str, code: str, requirement: str) -> str:
        """Đề xuất test case cho mã nguồn"""
        
        test_case_prompt = f"""
# YÊU CẦU SINH TEST CASE

## Ngôn ngữ: {language}

## Mô tả yêu cầu:
{requirement}

## Mã nguồn:
```{language}
{code}
```

## YÊU CẦU TEST CASE:
1. Tạo các test case bao phủ các trường hợp:
   - Cơ bản (happy path)
   - Biên (boundary values)
   - Ngoại lệ (exceptions, error cases)
   
2. Định dạng test case phù hợp với ngôn ngữ:
   - Python: unittest và pytest
   - C: assert statements

3. Giải thích mục đích của từng test case

## ĐỊNH DẠNG PHẢN HỒI:
- Danh sách các test case với input, expected output
- Code test đầy đủ, có thể chạy được
- Giải thích ngắn gọn từng test case
"""
        
        test_case_response = self.gemini_client.query(test_case_prompt)
        return test_case_response

class SmartProgrammingAssistant:
    """Trợ lý lập trình thông minh - lớp chính của ứng dụng"""
    
    def __init__(self, api_key: str):
        """Khởi tạo trợ lý với API key"""
        self.api_key = api_key
        self.gemini_client = GeminiClient(api_key)
        self.code_analyzer = CodeAnalyzer(self.gemini_client)
        self.current_code = {}  # Lưu trữ mã nguồn hiện tại theo ngôn ngữ
        self.code_history = {}  # Lưu trữ lịch sử các phiên bản mã nguồn
        self.current_requirements = ""  # Lưu trữ yêu cầu hiện tại
        
        # Khởi tạo system prompt
        self._initialize_system_prompt()
    
    def _initialize_system_prompt(self):
        """Khởi tạo system prompt cho Gemini"""
        system_prompt = """
# TRỢ LÝ LẬP TRÌNH THÔNG MINH

Bạn là một trợ lý lập trình thông minh, chuyên hỗ trợ phân tích, debug và tối ưu hóa mã nguồn.

## VAI TRÒ
- Phát hiện và giải thích lỗi trong mã nguồn (C và Python)
- Mô phỏng quá trình thực thi từng bước
- Phân tích logic và hiệu suất mã
- Đề xuất cải tiến và tối ưu hóa
- Sinh test case và kiểm thử

## NGUYÊN TẮC
- Giải thích mọi vấn đề và giải pháp một cách chi tiết, rõ ràng
- Sử dụng ngôn ngữ dễ hiểu, phù hợp với mọi trình độ
- Cung cấp mã nguồn đã sửa lỗi và được tối ưu
- Phân tích sâu các vấn đề phức tạp

## ĐỊNH DẠNG PHẢN HỒI
- Sử dụng markdown để định dạng phản hồi
- Tổ chức thông tin theo cấu trúc rõ ràng
- Highlight code và lỗi để dễ nhận biết
- Sử dụng bảng và biểu đồ khi cần thiết
"""
        
        # Thêm system prompt vào lịch sử
        self.gemini_client.add_to_history("user", system_prompt)
        self.gemini_client.add_to_history("model", "Tôi sẽ làm việc như một trợ lý lập trình thông minh, tuân theo các nguyên tắc và hướng dẫn đã nêu.")
    
    def set_requirements(self, requirements: str):
        """Cập nhật yêu cầu đề bài"""
        self.current_requirements = requirements
        
        # Thêm yêu cầu vào lịch sử
        requirements_prompt = f"""
# YÊU CẦU ĐỀ BÀI

{requirements}

Hãy phân tích yêu cầu này và cho tôi biết các điểm chính cần lưu ý.
"""
        
        self.gemini_client.add_to_history("user", requirements_prompt)
        analysis_response = self.gemini_client.query(requirements_prompt)
        
        return analysis_response
    
    def add_code(self, language: str, code: str, filename: str = None):
        """Thêm mã nguồn vào trợ lý"""
        if language.lower() not in Config.SUPPORTED_LANGUAGES:
            return f"Ngôn ngữ '{language}' không được hỗ trợ. Các ngôn ngữ hỗ trợ: {', '.join(Config.SUPPORTED_LANGUAGES)}"
        
        # Lưu lịch sử nếu đã có mã nguồn trước đó
        if language in self.current_code:
            if language not in self.code_history:
                self.code_history[language] = []
            self.code_history[language].append(self.current_code[language])
        
        # Cập nhật mã nguồn hiện tại
        self.current_code[language] = {
            "code": code,
            "filename": filename or f"code.{language.lower()}"
        }
        
        # Thêm code vào lịch sử
        code_prompt = f"""
# MÃ NGUỒN MỚI

## Ngôn ngữ: {language}
## Tên file: {filename or f"code.{language.lower()}"}

```{language}
{code}
```

Hãy phân tích mã nguồn này và cho tôi biết nó làm gì.
"""
        
        self.gemini_client.add_to_history("user", code_prompt)
        analysis_response = self.gemini_client.query(code_prompt)
        
        return analysis_response
    
    def analyze_current_code(self, language: str):
        """Phân tích mã nguồn hiện tại"""
        if language.lower() not in self.current_code:
            return f"Không có mã nguồn {language} để phân tích. Vui lòng thêm mã nguồn trước."
        
        code_data = self.current_code[language]
        analysis_result = self.code_analyzer.analyze_code(
            language, 
            code_data["code"],
            self.current_requirements
        )
        
        # Tạo markdown để hiển thị kết quả
        markdown_result = self._format_analysis_result(analysis_result, language)
        
        return markdown_result
    
    def _format_analysis_result(self, analysis_result: Dict[str, Any], language: str) -> str:
        """Định dạng kết quả phân tích thành markdown"""
        md = "# Kết Quả Phân Tích Mã Nguồn\n\n"
        
        # Thêm phần header
        md += f"## Tổng Quan\n\n"
        
        # Thêm thông tin về cú pháp
        syntax_check = analysis_result["syntax_check"]
        execution_result = analysis_result["execution_result"]
        analysis = analysis_result["analysis"]
        
        # Trạng thái cú pháp
        syntax_status = "✅ Không có lỗi cú pháp" if syntax_check["status"] == "success" else f"❌ Có lỗi cú pháp"
        md += f"- **Cú pháp:** {syntax_status}\n"
        
        # Trạng thái thực thi
        execution_status = "✅ Thực thi thành công" if execution_result["status"] == "success" else f"❌ Lỗi khi thực thi"
        md += f"- **Thực thi:** {execution_status}\n"
        
        # Độ phù hợp với yêu cầu
        requirement_compliance = analysis.get("requirement_compliance", "Không xác định")
        md += f"- **Đáp ứng yêu cầu:** {requirement_compliance}\n\n"
        
        # Chi tiết các lỗi
        md += "## Chi Tiết Các Vấn Đề\n\n"
        
        # Lỗi cú pháp
        md += "### Lỗi Cú Pháp\n\n"
        syntax_issues = analysis.get("syntax_issues", [])
        if not syntax_issues:
            md += "Không phát hiện lỗi cú pháp.\n\n"
        else:
            for issue in syntax_issues:
                md += f"- **Dòng {issue.get('line', 'N/A')}:** {issue.get('description', 'Không có mô tả')}\n"
                md += f"  - **Cách sửa:** {issue.get('fix', 'Không có gợi ý')}\n\n"
        
        # Lỗi logic
        md += "### Lỗi Logic\n\n"
        logic_issues = analysis.get("logic_issues", [])
        if not logic_issues:
            md += "Không phát hiện lỗi logic.\n\n"
        else:
            for issue in logic_issues:
                affected_lines = issue.get('affected_lines', ['N/A'])
                if isinstance(affected_lines, list):
                    lines_str = ", ".join(str(line) for line in affected_lines)
                else:
                    lines_str = str(affected_lines)
                
                md += f"- **Dòng {lines_str}:** {issue.get('description', 'Không có mô tả')}\n"
                md += f"  - **Cách sửa:** {issue.get('fix', 'Không có gợi ý')}\n\n"
        
        # Lỗi runtime
        md += "### Lỗi Runtime\n\n"
        runtime_issues = analysis.get("runtime_issues", [])
        if not runtime_issues:
            md += "Không phát hiện lỗi runtime.\n\n"
        else:
            for issue in runtime_issues:
                md += f"- **Vấn đề:** {issue.get('description', 'Không có mô tả')}\n"
                md += f"  - **Cách sửa:** {issue.get('fix', 'Không có gợi ý')}\n\n"
        
        # Mã nguồn được đề xuất sửa
        suggested_fixes = analysis.get("suggested_fixes", "")
        if suggested_fixes:
            md += "## Mã Nguồn Đã Sửa\n\n"
            md += f"```{language}\n{suggested_fixes}\n```\n\n"
        
        # Giải thích
        explanation = analysis.get("explanation", "")
        if explanation:
            md += "## Giải Thích Chi Tiết\n\n"
            md += f"{explanation}\n\n"
        
        # Đề xuất tối ưu hóa
        md += "## Đề Xuất Tối Ưu Hóa\n\n"
        optimizations = analysis.get("optimizations", [])
        if not optimizations:
            md += "Không có đề xuất tối ưu hóa.\n\n"
        else:
            for i, opt in enumerate(optimizations, 1):
                md += f"{i}. {opt}\n"
        
        return md
    
    def simulate_execution(self, language: str, detail_level: str = None):
        """Mô phỏng thực thi mã nguồn từng bước"""
        if language.lower() not in self.current_code:
            return f"Không có mã nguồn {language} để mô phỏng. Vui lòng thêm mã nguồn trước."
        
        detail_level = detail_level or Config.DEFAULT_DETAIL_LEVEL
        code_data = self.current_code[language]
        
        simulation_result = self.code_analyzer.simulate_execution(
            language,
            code_data["code"],
            detail_level
        )
        
        return simulation_result
    
    def generate_test_cases(self, language: str):
        """Sinh test case cho mã nguồn hiện tại"""
        if language.lower() not in self.current_code:
            return f"Không có mã nguồn {language} để sinh test case. Vui lòng thêm mã nguồn trước."
        
        code_data = self.current_code[language]
        
        # Gọi API để sinh test case
        test_cases_result = self.code_analyzer.suggest_test_cases(
            language,
            code_data["code"],
            self.current_requirements
        )
        
        # Thực thi để tạo file test
        CodeExecutor.generate_test_cases(
            language,
            code_data["code"],
            self.current_requirements
        )
        
        return test_cases_result
    
    def compare_versions(self, language: str, version1: int = -2, version2: int = -1):
        """So sánh hai phiên bản mã nguồn"""
        if language.lower() not in self.code_history or len(self.code_history[language]) < 2:
            return f"Không đủ phiên bản mã nguồn {language} để so sánh. Cần ít nhất 2 phiên bản."
        
        # Lấy phiên bản code
        history = self.code_history[language]
        
        # Xử lý chỉ số âm
        if version1 < 0:
            version1 = len(history) + version1
        if version2 < 0:
            version2 = len(history) + version2
        
        # Kiểm tra phạm vi
        if version1 < 0 or version1 >= len(history) or version2 < 0 or version2 >= len(history):
            return f"Chỉ số phiên bản không hợp lệ. Phạm vi hợp lệ: 0-{len(history)-1}."
        
        # So sánh
        old_code = history[version1]["code"]
        new_code = history[version2]["code"]
        diff = Utils.compare_code_versions(old_code, new_code)
        
        # Tạo diff đẹp để hiển thị
        html_diff = Utils.create_displayable_diff(old_code, new_code)
        
        return {
            "text_diff": diff,
            "html_diff": html_diff
        }
    
    def update_from_file(self, file_upload_path: str):
        """Cập nhật mã nguồn từ file được tải lên"""
        file_ext = file_upload_path.split('.')[-1].lower()
        
        if file_ext == 'zip':
            # Giải nén file zip
            extract_dir = os.path.join(Config.TEMP_DIR, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            extracted_files = Utils.unzip_file(file_upload_path, extract_dir)
            
            result = {
                "message": f"Đã giải nén {len(extracted_files)} file.",
                "files": []
            }
            
            # Tìm các file theo ngôn ngữ được hỗ trợ
            for language in Config.SUPPORTED_LANGUAGES:
                relevant_files = Utils.get_relevant_language_files(extract_dir, language)
                
                for file_path in relevant_files:
                    file_content = Utils.read_file(file_path)
                    file_name = os.path.basename(file_path)
                    
                    # Thêm mã nguồn vào trợ lý
                    analysis = self.add_code(language, file_content, file_name)
                    
                    result["files"].append({
                        "path": file_path,
                        "language": language,
                        "name": file_name,
                        "analysis": analysis
                    })
            
            return result
        
        elif file_ext in ['c', 'h']:
            # File C
            file_content = Utils.read_file(file_upload_path)
            file_name = os.path.basename(file_upload_path)
            analysis = self.add_code("c", file_content, file_name)
            
            return {
                "message": f"Đã đọc file {file_name}",
                "analysis": analysis
            }
        
        elif file_ext == 'py':
            # File Python
            file_content = Utils.read_file(file_upload_path)
            file_name = os.path.basename(file_upload_path)
            analysis = self.add_code("python", file_content, file_name)
            
            return {
                "message": f"Đã đọc file {file_name}",
                "analysis": analysis
            }
        
        else:
            return {
                "message": f"Không hỗ trợ file có phần mở rộng '{file_ext}'.",
                "supported_extensions": [".c", ".h", ".py", ".zip"]
            }
    
    def explain_code(self, language: str):
        """Giải thích mã nguồn chi tiết"""
        if language.lower() not in self.current_code:
            return f"Không có mã nguồn {language} để giải thích. Vui lòng thêm mã nguồn trước."
        
        code_data = self.current_code[language]
        
        explain_prompt = f"""
# YÊU CẦU GIẢI THÍCH MÃ NGUỒN

## Ngôn ngữ: {language}

## Mã nguồn:
```{language}
{code_data['code']}
```

## YÊU CẦU:
1. Giải thích tổng quan về mục đích và chức năng của mã nguồn
2. Mô tả cấu trúc và tổ chức của mã
3. Giải thích từng phần, hàm, và thuật toán quan trọng
4. Chỉ ra các điểm mạnh và hạn chế của mã
5. Đề xuất cách cải thiện về mặt cấu trúc và tổ chức

## ĐỊNH DẠNG PHẢN HỒI:
- Tạo phản hồi dưới dạng markdown
- Phân chia thành các phần rõ ràng
- Sử dụng code snippets khi cần thiết
- Giải thích các thuật ngữ kỹ thuật
"""
        
        explanation = self.gemini_client.query(explain_prompt)
        return explanation

# ===== PHẦN GIAO DIỆN =====

class UI:
    """Xử lý giao diện người dùng với Tkinter"""

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Programming Assistant v1.1 (Local)")
        self.root.geometry("1000x800")

        self.assistant: Optional[SmartProgrammingAssistant] = None

        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam') # Options: 'clam', 'alt', 'default', 'classic'

        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # API Key section (initially visible)
        self.api_key_frame = ttk.LabelFrame(self.main_frame, text="API Key Configuration", padding="10")
        self.api_key_frame.pack(fill=tk.X, pady=5)
        self.create_api_key_input()

        # Main content section (initially hidden/disabled)
        self.content_frame = ttk.Frame(self.main_frame)
        # self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10) # Packed later

        self.output_text = None # Will be created in create_main_interface

    def create_api_key_input(self):
        """Tạo input cho API key"""
        ttk.Label(self.api_key_frame, text="Nhập API Key của Gemini:").pack(side=tk.LEFT, padx=5)
        self.api_key_entry = ttk.Entry(self.api_key_frame, width=50, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.save_api_key_button = ttk.Button(self.api_key_frame, text="Lưu API Key", command=self.handle_save_api_key)
        self.save_api_key_button.pack(side=tk.LEFT, padx=5)

    def handle_save_api_key(self):
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("Lỗi", "Vui lòng nhập API Key.")
            return

        try:
            # Khởi tạo trợ lý
            self.assistant = SmartProgrammingAssistant(api_key)
            messagebox.showinfo("Thành công", "API Key đã được lưu và Trợ lý đã được khởi tạo.")
            
            # Ẩn phần API key và hiển thị giao diện chính
            self.api_key_frame.pack_forget()
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            self.create_main_interface()

        except Exception as e:
            messagebox.showerror("Lỗi Khởi Tạo Assistant", f"Không thể khởi tạo trợ lý: {str(e)}")
            self.assistant = None


    def create_main_interface(self):
        """Tạo giao diện chính"""
        # PanedWindow for resizable sections
        paned_window = ttk.PanedWindow(self.content_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Top frame for inputs
        input_controls_frame = ttk.Frame(paned_window, height=350) #  Explicit height
        paned_window.add(input_controls_frame, weight=1)

        # Bottom frame for output
        output_frame = ttk.LabelFrame(paned_window, text="Kết Quả", padding="5")
        paned_window.add(output_frame, weight=3) # More weight for output

        # --- Input Controls Frame ---
        # Requirements
        req_frame = ttk.LabelFrame(input_controls_frame, text="📝 Yêu Cầu Đề Bài", padding="5")
        req_frame.pack(fill=tk.X, pady=5)
        self.requirements_text = scrolledtext.ScrolledText(req_frame, height=4, width=80, wrap=tk.WORD)
        self.requirements_text.pack(fill=tk.X, expand=True, pady=(0,5))
        ttk.Button(req_frame, text="Lưu Yêu Cầu", command=self.handle_save_requirements).pack(anchor=tk.E)

        # Code Input
        code_frame = ttk.LabelFrame(input_controls_frame, text="💻 Nhập Mã Nguồn", padding="5")
        code_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        lang_file_frame = ttk.Frame(code_frame)
        lang_file_frame.pack(fill=tk.X)
        
        ttk.Label(lang_file_frame, text="Ngôn ngữ:").pack(side=tk.LEFT, padx=(0,5))
        self.language_var = tk.StringVar(value="python")
        lang_options = ["python", "c"]
        self.language_dropdown = ttk.Combobox(lang_file_frame, textvariable=self.language_var, values=lang_options, state="readonly", width=10)
        self.language_dropdown.pack(side=tk.LEFT, padx=(0,10))

        ttk.Button(lang_file_frame, text="Tải File Lên (.py, .c, .h, .zip)", command=self.handle_process_file).pack(side=tk.LEFT, padx=5)
        
        self.code_text = scrolledtext.ScrolledText(code_frame, height=10, width=80, wrap=tk.WORD, font=("Courier New", 10))
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=(5,5))
        ttk.Button(code_frame, text="Lưu Mã Nguồn Này", command=self.handle_save_code).pack(anchor=tk.E)

        # Action Buttons
        actions_frame = ttk.LabelFrame(input_controls_frame, text="📊 Công Cụ", padding="5")
        actions_frame.pack(fill=tk.X, pady=5)

        actions_inner_frame = ttk.Frame(actions_frame) # To center buttons
        actions_inner_frame.pack()

        ttk.Button(actions_inner_frame, text="Phân Tích Mã", command=self.handle_analyze_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_inner_frame, text="Mô Phỏng Thực Thi", command=self.handle_simulate_execution).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_inner_frame, text="Sinh Test Case", command=self.handle_generate_test_cases).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_inner_frame, text="Giải Thích Mã", command=self.handle_explain_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_inner_frame, text="So Sánh Phiên Bản (cuối & trước đó)", command=self.handle_compare_versions).pack(side=tk.LEFT, padx=5)


        # --- Output Frame ---
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def display_output(self, title: str, content: str):
        if not self.output_text: return
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        if title:
            self.output_text.insert(tk.END, f"--- {title.upper()} ---\n\n", "title_style")
        self.output_text.insert(tk.END, content)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.tag_config("title_style", font=("Arial", 12, "bold"))


    def handle_save_requirements(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo. Vui lòng nhập API Key.")
            return
        requirements = self.requirements_text.get("1.0", tk.END).strip()
        if requirements:
            try:
                result = self.assistant.set_requirements(requirements)
                self.display_output("Phân Tích Yêu Cầu", result)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi lưu yêu cầu: {str(e)}")
        else:
            messagebox.showwarning("Chú ý", "Yêu cầu không được để trống.")

    def handle_save_code(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo.")
            return
        code = self.code_text.get("1.0", tk.END).strip()
        language = self.language_var.get()
        if code and language:
            try:
                result = self.assistant.add_code(language, code)
                self.display_output(f"Phân Tích Mã Nguồn {language.upper()} Mới", result)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi lưu mã nguồn: {str(e)}")
        else:
            messagebox.showwarning("Chú ý", "Mã nguồn hoặc ngôn ngữ không được để trống.")

    def handle_analyze_code(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo.")
            return
        language = self.language_var.get()
        if language not in self.assistant.current_code:
             messagebox.showwarning("Chú ý", f"Không có mã nguồn {language} để phân tích. Vui lòng thêm mã nguồn trước.")
             return
        try:
            result = self.assistant.analyze_current_code(language)
            self.display_output(f"Kết Quả Phân Tích Mã {language.upper()}", result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi phân tích mã: {str(e)}")
            self.display_output(f"Lỗi Phân Tích Mã {language.upper()}", f"Đã xảy ra lỗi: {traceback.format_exc()}")


    def handle_simulate_execution(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo.")
            return
        language = self.language_var.get()
        if language not in self.assistant.current_code:
             messagebox.showwarning("Chú ý", f"Không có mã nguồn {language} để mô phỏng. Vui lòng thêm mã nguồn trước.")
             return
        try:
            # Add detail level option later if needed
            result = self.assistant.simulate_execution(language)
            self.display_output(f"Mô Phỏng Thực Thi Mã {language.upper()}", result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi mô phỏng: {str(e)}")

    def handle_generate_test_cases(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo.")
            return
        language = self.language_var.get()
        if language not in self.assistant.current_code:
             messagebox.showwarning("Chú ý", f"Không có mã nguồn {language} để sinh test case. Vui lòng thêm mã nguồn trước.")
             return
        try:
            result = self.assistant.generate_test_cases(language)
            self.display_output(f"Test Cases Cho Mã {language.upper()}", result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi sinh test case: {str(e)}")
    
    def handle_explain_code(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo.")
            return
        language = self.language_var.get()
        if language not in self.assistant.current_code:
             messagebox.showwarning("Chú ý", f"Không có mã nguồn {language} để giải thích. Vui lòng thêm mã nguồn trước.")
             return
        try:
            result = self.assistant.explain_code(language)
            self.display_output(f"Giải Thích Mã {language.upper()}", result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi giải thích mã: {str(e)}")

    def handle_compare_versions(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo.")
            return
        language = self.language_var.get()
        try:
            comparison = self.assistant.compare_versions(language) # Default: last two versions
            if isinstance(comparison, str): # Error message
                messagebox.showwarning("So sánh", comparison)
                self.display_output(f"So Sánh Phiên Bản {language.upper()}", comparison)
            else:
                self.display_output(f"So Sánh Phiên Bản {language.upper()} (Phiên bản -2 và -1)", comparison['text_diff'])
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi so sánh phiên bản: {str(e)}")


    def handle_process_file(self):
        if not self.assistant:
            messagebox.showerror("Lỗi", "Trợ lý chưa được khởi tạo. Vui lòng nhập API Key trước.")
            return

        filepath = filedialog.askopenfilename(
            title="Chọn file mã nguồn hoặc file ZIP",
            filetypes=(("Python files", "*.py"),
                       ("C/C++ files", "*.c *.h"),
                       ("Zip archives", "*.zip"),
                       ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            self.display_output("Xử Lý File", f"Đang xử lý file: {filepath}...")
            # The assistant.update_from_file expects a path to a file that it can read.
            # If it's a complex interaction where google.colab.files.upload() was involved,
            # this part might need adjustment in SmartProgrammingAssistant if it assumed content bytes.
            # For now, assuming update_from_file can handle a local file path.
            
            # The original `update_from_file` was called inside a callback that first uploaded
            # and saved the file to Config.TEMP_DIR. We'll replicate that logic.
            filename = os.path.basename(filepath)
            temp_file_path = os.path.join(Config.TEMP_DIR, filename)
            
            # Copy uploaded file to temp_dir because `update_from_file` might expect it there or operate within it
            # (e.g. for unzipping relative paths)
            import shutil
            shutil.copy(filepath, temp_file_path)

            result = self.assistant.update_from_file(temp_file_path) # Pass path to temp file
            
            output_str = f"Đã xử lý file: {filename}\n\n"
            
            if isinstance(result, dict):
                if "message" in result:
                    output_str += result["message"] + "\n\n"
                
                if "files" in result and result["files"]: # For ZIP
                    for f_info in result["files"]:
                        output_str += f"--- Phân tích cho {f_info.get('name', 'N/A')} ({f_info.get('language', 'N/A')}) ---\n"
                        output_str += f_info.get("analysis", "Không có phân tích.") + "\n\n"
                        # If code from zip should be loaded into editor:
                        if f_info.get('language') == self.language_var.get():
                           loaded_code_content = Utils.read_file(f_info['path'])
                           if not loaded_code_content.startswith("Error reading file"):
                               self.code_text.delete("1.0", tk.END)
                               self.code_text.insert("1.0", loaded_code_content)
                               self.language_var.set(f_info.get('language'))

                elif "analysis" in result: # For single file
                    output_str += result["analysis"]
                    # Load code into editor if it's the current language
                    file_ext = filename.split('.')[-1].lower()
                    current_lang = self.language_var.get()
                    is_python_file = file_ext == 'py' and current_lang == 'python'
                    is_c_file = file_ext in ['c', 'h'] and current_lang == 'c'

                    if is_python_file or is_c_file:
                        file_content = Utils.read_file(temp_file_path)
                        if not file_content.startswith("Error reading file:"):
                             self.code_text.delete("1.0", tk.END)
                             self.code_text.insert("1.0", file_content)


                self.display_output("Kết Quả Xử Lý File", output_str)

            else: # Should not happen if assistant.update_from_file is consistent
                self.display_output("Kết Quả Xử Lý File", "Không có phản hồi hoặc định dạng không rõ.")

        except Exception as e:
            messagebox.showerror("Lỗi Xử Lý File", f"Không thể xử lý file: {str(e)}\n{traceback.format_exc()}")
            self.display_output("Lỗi Xử Lý File", f"Lỗi: {str(e)}\n{traceback.format_exc()}")


# ===== PHẦN KHỞI ĐỘNG ỨNG DỤNG =====

def run_application_local():
    """Khởi động ứng dụng Tkinter"""
    root = tk.Tk()
    app_ui = UI(root)
    root.mainloop()

    # Dọn dẹp thư mục tạm khi đóng ứng dụng
    import shutil
    try:
        shutil.rmtree(Config.TEMP_DIR)
        print(f"Đã dọn dẹp thư mục tạm: {Config.TEMP_DIR}")
    except Exception as e:
        print(f"Lỗi khi dọn dẹp thư mục tạm: {e}")

# Chạy ứng dụng khi script được thực thi
if __name__ == "__main__":
    run_application_local()
