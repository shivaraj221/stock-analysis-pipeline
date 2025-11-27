# agents/notifier_agent.py
from crewai import Agent, LLM
from tools.notifier import DiscordNotifierTool

# FORCE OLLAMA — NO OPENAI EVER
ollama_llm = LLM(
    model="ollama/qwen2.5:7b-instruct",
    base_url="http://localhost:11434",
    temperature=0.1
)

notifier_agent = Agent(
    role="Discord Alert Master",
    goal="Send beautiful classified stock alerts to Discord using ONLY the discord_notify_tool",
    backstory="You are the final step. You read classified_stocks.json and send rich embeds. Never write text yourself.",
    tools=[DiscordNotifierTool()],
    llm=ollama_llm,           # THIS LINE KILLS THE OPENAI ERROR
    verbose=False,
    allow_delegation=False,
    max_iter=1
)