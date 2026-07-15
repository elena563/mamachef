from functions.llms.llm_base import LLM_Base
from functions.llms.groq_config import Groq

class LLM:

    __llms = [
        Groq("llama-3.3-70b-versatile"),
    ]

    def __init__(self, model_name: str):
        self.model = None

        llm: LLM_Base
        for llm in self.__llms:
            if llm.get_name() == model_name:
                self.model = llm
                break

    def ask(self, prompt):
        if self.model is None:
            raise Exception("LLM not found")
        return self.model.ask(prompt)
    
    @staticmethod
    def get_all_models() -> list[str]:        
        return [llm.get_name() for llm in LLM.__llms]