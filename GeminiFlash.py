import os
import getpass

from langchain_google_genai import ChatGoogleGenerativeAI
from LLM import LLM

class GeminiFlash(LLM):
    def load_model(self):
        self.id=14
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )