from abc import ABC, abstractmethod

class LLM(ABC):
    @abstractmethod
    def load_model(self):
        pass
