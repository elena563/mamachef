from abc import ABC, abstractmethod

class LLM_Base(ABC):

    def __init__(self, model_name: str | None = None):
        self.__model_name = model_name
        self.client = None

    def get_name(self) -> str:
        return self.__model_name
    
    
    def ask(self, prompt: str) -> str:
        if self.client is None:
            try:
                self.client = self.get_client()
            except Exception as e:
                self.client = None
                raise Exception(f"Error initializing {self.get_name()} client: {str(e)}")
        return self.query(prompt)


    @abstractmethod
    def query(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_client(self):
        pass