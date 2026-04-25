import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('GEMINI_API_KEY')
print('key loaded', bool(key))
genai.configure(api_key=key)
for model in genai.list_models():
    print(model)
