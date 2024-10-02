import os
import getpass
from langchain.chat_models import ChatOpenAI
from LLM import LLM

class GPT_4o_mini(LLM):
    def load_model(self):
        self.id=23
        self.llm=ChatOpenAI(
            temperature=0,
            max_tokens=512,
            model_name="gpt-4o-mini"  # This will be passed in the request
        )