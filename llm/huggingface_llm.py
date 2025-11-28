import requests
import os

class HuggingFaceLLM:
    def __init__(self, model="moonshotai/Kimi-K2-Thinking:novita", temperature=0.1, max_tokens=2500):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
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

        # CrewAI expects a STRING, not raw JSON
        return data["choices"][0]["message"]["content"]
