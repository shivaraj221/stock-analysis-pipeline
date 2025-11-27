# tasks/notify_task.py
from crewai import Task
from agents.notifier_agent import notifier_agent

notify_task = Task(
    description="""
    Send the existing classified_stocks.json to Discord.
    Use ONLY the discord_notify_tool.
    Do not think. Do not write. Just call the tool.
    """,
    expected_output="SUCCESS: Alerts sent to Discord",
    agent=notifier_agent,
    async_execution=False
)