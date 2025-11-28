from crewai import Agent, LLM
from tools.notifier import DiscordNotifierTool
from llms.huggingface_llm import HuggingFaceLLM

# Free Gemma model - NO API KEY NEEDED
hf_llm = HuggingFaceLLM(
    model="moonshotai/Kimi-K2-Thinking:novita",
    temperature=0.1
)

notifier_agent = Agent(
    role="Discord Alert Master",
    goal="Send beautiful classified stock alerts to Discord using ONLY the discord_notify_tool",
    backstory="You are the final step. You read classified_stocks.json and send rich embeds. Never write text yourself.",
    tools=[DiscordNotifierTool()],
    llm=hf_llm,
    verbose=False,
    allow_delegation=False,
    max_iter=1
)
