import os
import getpass
from LLM import LLM
from langchain_openai import AzureChatOpenAI

class ChatGPT(LLM):
    def load_model(self):
        self.id=16
        self.llm = AzureChatOpenAI(
            azure_deployment="gpt-35-turbo-0125",
            api_version="2024-05-01-preview",
            temperature=0,
            max_retries=2,
        )