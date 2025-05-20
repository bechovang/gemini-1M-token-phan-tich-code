import requests
import json
import google.generativeai as genai

# Thay thế bằng API key của bạn
API_KEY = "AIzaSyAa7zBQuCGvrsoQ3WF75JL76_0ZiD4_w6g"

def test_gemini_api_with_requests():
    """Phương pháp 1: Sử dụng requests trực tiếp với API"""
    print("\n===== TEST BẰNG REQUESTS =====")
    
    # API endpoint của Gemini (version 1 - stable)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"
    
    # Tạo yêu cầu test đơn giản
    payload = {
        "contents": [{
            "parts": [{
                "text": "Hello, can you introduce yourself briefly?"
            }]
        }]
    }
    
    # Gửi yêu cầu
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Đang gửi yêu cầu đến API Gemini...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Kiểm tra mã trạng thái
        if response.status_code == 200:
            print("✅ API key hoạt động tốt!")
            print("\nPhản hồi từ Gemini:")
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0]["content"]
                if "parts" in content and len(content["parts"]) > 0:
                    print(content["parts"][0]["text"])
            else:
                print("Không thể trích xuất nội dung phản hồi.")
                print("Dữ liệu phản hồi thô:", result)
                
            # Hiển thị thông tin về usage để kiểm tra token count
            if "usageMetadata" in result:
                usage = result["usageMetadata"]
                print("\nThông tin sử dụng:")
                print(f"Tokens đã sử dụng: {usage.get('promptTokenCount', 'N/A')} (prompt) + {usage.get('candidatesTokenCount', 'N/A')} (response)")
                print(f"Tổng token: {usage.get('totalTokenCount', 'N/A')}")
        else:
            print(f"❌ Lỗi API (HTTP {response.status_code}):")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Lỗi khi kết nối với API Gemini: {str(e)}")

def test_gemini_api_with_library():
    """Phương pháp 2: Sử dụng thư viện chính thức của Google"""
    print("\n===== TEST BẰNG THƯ VIỆN CHÍNH THỨC =====")
    
    try:
        # Cấu hình API key
        genai.configure(api_key=API_KEY)
        
        # Kiểm tra mô hình có sẵn
        print("Đang kiểm tra các mô hình có sẵn...")
        models = genai.list_models()
        gemini_models = [model.name for model in models if "gemini" in model.name.lower()]
        print(f"Các mô hình Gemini có sẵn: {gemini_models}")
        
        # Sử dụng mô hình gemini-1.5-pro-latest
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Tạo response
        print("Đang gửi yêu cầu đến mô hình Gemini...")
        response = model.generate_content("Hello, can you introduce yourself briefly?")
        
        print("✅ API key hoạt động tốt!")
        print("\nPhản hồi từ Gemini:")
        print(response.text)
        
        # Hiển thị thông tin về usage
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            print("\nThông tin sử dụng:")
            print(f"Tokens đã sử dụng: {usage}")
        
    except Exception as e:
        print(f"❌ Lỗi khi sử dụng thư viện Google Generative AI: {str(e)}")

if __name__ == "__main__":
    print("Đang kiểm tra API key Gemini...")
    
    # Cần cài đặt thư viện trước khi chạy phương pháp 2:
    # pip install google-generativeai
    
    # Thử cả hai phương pháp
    # test_gemini_api_with_requests()
    
    try:
        test_gemini_api_with_library()
    except ImportError:
        print("\n⚠️ Bạn cần cài đặt thư viện Google Generative AI để chạy phương pháp thứ hai:")
        print("pip install google-generativeai")