import os
import requests

class HuggingFaceLLM:
    def __init__(self, model="moonshotai/Kimi-K2-Thinking:novita", temperature=0.1):
        self.model = model
        self.temperature = temperature
        self.headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
            "Content-Type": "application/json"
        }
        self.api_url = "https://router.huggingface.co/v1/chat/completions"

    def call(self, messages, max_tokens=512):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens
        }

        resp = requests.post(self.api_url, headers=self.headers, json=payload)
        data = resp.json()

        return data["choices"][0]["message"]["content"]
