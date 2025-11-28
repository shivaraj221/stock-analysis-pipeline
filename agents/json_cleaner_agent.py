from crewai import Agent
from tools.json_cleaner_tool import JSONCleanerTool
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hugging Face configuration
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set")

class HuggingFaceLLM:
    def __init__(self, model="moonshotai/Kimi-K2-Thinking:novita", temperature=0.1):
        self.model = model
        self.temperature = temperature
        self.api_url = API_URL
        self.headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def call(self, messages, max_tokens=None):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()

# Create Hugging Face LLM instance
hf_llm = HuggingFaceLLM(
    model="moonshotai/Kimi-K2-Thinking:novita",
    temperature=0.1
)

json_cleaner_agent = Agent(
    role="JSON Cleaner",
    goal="Clean malformed JSON files and save corrected versions",
    backstory="Specialized agent for sanitizing JSON output from other pipelines.",
    tools=[JSONCleanerTool()],
    llm=hf_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=128
)
