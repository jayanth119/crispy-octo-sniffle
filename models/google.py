from __future__ import annotations
import time
import os
from dotenv import load_dotenv
from agno.models.google import Gemini


# Load environment variables
load_dotenv()
api_key = os.environ.get('GOOGLE_API_KEY')

def get_llm_instance(max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            return Gemini(id="gemini-2.5-flash", api_key=api_key)
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}. Retrying in {2**attempt}s …")
            time.sleep(2**attempt)
            attempt += 1
    raise Exception("Failed to instantiate Gemini after several attempts")

llm = get_llm_instance()
