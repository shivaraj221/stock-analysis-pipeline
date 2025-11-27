from crewai import Agent, LLM
from tools.notifier import DiscordNotifierTool

# Free Gemma model - NO API KEY NEEDED
llama_llm = LLM(
    model="meta-llama/llama-3.1-8b-instruct:free",
    base_url="https://openrouter.ai/api/v1", 
    api_key="null",
    temperature=0.1
)

notifier_agent = Agent(
    role="Discord Alert Master",
    goal="Send beautiful classified stock alerts to Discord using ONLY the discord_notify_tool",
    backstory="You are the final step. You read classified_stocks.json and send rich embeds. Never write text yourself.",
    tools=[DiscordNotifierTool()],
    llm=llama_llm,
    verbose=False,
    allow_delegation=False,
    max_iter=1
)
