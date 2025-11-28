import os
import requests
from crewai.llm import LLM

class HuggingFaceLLM(LLM):
    def __init__(self, model="moonshotai/Kimi-K2-Thinking:novita", temperature=0.1, max_tokens=1024):
        super().__init__()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
            "Content-Type": "application/json"
        }

    def call(self, messages, max_tokens=None):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }

        resp = requests.post(self.api_url, headers=self.headers, json=payload)
        data = resp.json()

        return data["choices"][0]["message"]["content"]
