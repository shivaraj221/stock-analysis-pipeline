from crewai import Task
from agents.json_cleaner_agent import json_cleaner_agent

json_cleaner_task = Task(
    description=(
        "Clean the JSON file by removing invalid formatting. "
        "Call json_cleaner_tool with the following parameters:\n"
        "{\n"
        "  \"input_path\": \"C:/Users/Admin/Desktop/crewai-1/crewai/data/new_classified_stocks.json\",\n"
        "  \"output_path\": \"C:/Users/Admin/Desktop/crewai-1/crewai/data/clean_classified_stocks.json\"\n"
        "}\n\n"
        "After cleaning is complete, reply ONLY with: SUCCESS."
    ),
    expected_output="SUCCESS",
    agent=json_cleaner_agent,
    async_execution=False,
)
