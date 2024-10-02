from LLM import LLM
from langchain_anthropic import ChatAnthropic

# Set Environment Variable 'ANTHROPIC_API_KEY'
class Claude(LLM):
    def load_model(self):
        self.id=18
        self.llm = ChatAnthropic(
            model='claude-3-5-sonnet-20240620',
            temperature=0,
            max_retries=2,
        )