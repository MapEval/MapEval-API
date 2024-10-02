from langchain_groq import ChatGroq


from LLM import LLM
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_huggingface import ChatHuggingFace
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.chat_models import ChatOpenAI
import os
from langchain_groq import ChatGroq

class Mixtral(LLM):
    def load_model(self):
        self.id = 5
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
                
