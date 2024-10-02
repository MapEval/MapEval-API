import os
import getpass
from LLM import LLM
from langchain_openai import AzureChatOpenAI

class GPTAzure(LLM):
    def load_model(self):
        self.id=6
        self.llm = AzureChatOpenAI(
            azure_deployment="gpt-4o-08-06",
            api_version="2024-02-15-preview",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )