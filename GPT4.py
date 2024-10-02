import os
import getpass
from langchain.chat_models import ChatOpenAI
from LLM import LLM

class GPT4(LLM):
    def load_model(self):
        self.id=22
        self.llm=ChatOpenAI(
            temperature=0,
            max_tokens=512,
            model_name="gpt-4-turbo"  # This will be passed in the request
        )