import os
import google.generativeai as genai

# Test if API key is available
api_key = os.getenv("GOOGLE_AI_API_KEY")
print(f"API Key available: {bool(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Gemini model initialized successfully")
        
        # Test with a simple text prompt
        response = model.generate_content("Say 'Hello, Gemini!'")
        print(f"✅ Test response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No API key found")
