from crewai import Agent, LLM
from tools.notifier import DiscordNotifierTool

# Free Gemma model - NO API KEY NEEDED
gemma_llm = LLM(
    model="google/gemma-3-4b-it:free",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1
)

notifier_agent = Agent(
    role="Discord Alert Master",
    goal="Send beautiful classified stock alerts to Discord using ONLY the discord_notify_tool",
    backstory="You are the final step. You read classified_stocks.json and send rich embeds. Never write text yourself.",
    tools=[DiscordNotifierTool()],
    llm=gemma_llm,
    verbose=False,
    allow_delegation=False,
    max_iter=1
)
