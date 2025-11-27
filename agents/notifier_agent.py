from crewai import Agent, LLM
from tools.notifier import DiscordNotifierTool

# GPT Model with your API key
gpt_llm = LLM(
    model="openai/gpt-oss-20b",
    api_key="OPENAI_API_KEY",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1
)

notifier_agent = Agent(
    role="Discord Alert Master",
    goal="Send beautiful classified stock alerts to Discord using ONLY the discord_notify_tool",
    backstory="You are the final step. You read classified_stocks.json and send rich embeds. Never write text yourself.",
    tools=[DiscordNotifierTool()],
    llm=gpt_llm,
    verbose=False,
    allow_delegation=False,
    max_iter=1
)
