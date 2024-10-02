
from LLM import LLM
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_huggingface import ChatHuggingFace
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.chat_models import ChatOpenAI
import os
from langchain_groq import ChatGroq

class Llama3_1_8B(LLM):
    def load_model(self):
        self.id = 21
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )