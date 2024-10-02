
from LLM import LLM
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_huggingface import ChatHuggingFace
from langchain_groq import ChatGroq


class Gemma2(LLM):
    def load_model(self):
        self.id = 15
        self.llm = ChatGroq(
            model="gemma2-9b-it",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        