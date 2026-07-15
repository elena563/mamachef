import os
from openai import OpenAI
from functions.llms.llm_base import LLM_Base
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Groq(LLM_Base):
    def get_client(self):
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def query(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.get_name(),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return response.choices[0].message.content