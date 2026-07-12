import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"DEBUG: Yüklenen anahtarın ilk 5 karakteri: {api_key[:5] if api_key else 'YOK'}")

genai.configure(api_key=api_key)

try:
    print("Modeller listeleniyor...")
    models = list(genai.list_models())
    if not models:
        print("Hata: Liste boş döndü!")
    for m in models:
        print(f"Model: {m.name}")
except Exception as e:
    print(f"KRİTİK HATA: {e}")