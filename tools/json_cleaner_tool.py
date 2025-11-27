from crewai.tools import BaseTool
import json
import os

class JSONCleanerTool(BaseTool):
    name: str = "json_cleaner_tool"   # MUST have type annotation
    description: str = (
        "Cleans LLM-generated JSON files by removing ``` blocks "
        "and saving valid JSON to a new file."
    )

    def _run(self, input_path: str, output_path: str) -> str:
        if not os.path.exists(input_path):
            return f"❌ Input file not found: {input_path}"

        # Read raw text (may contain ``` garbage)
        with open(input_path, "r", encoding="utf-8") as f:
            raw = f.read()

        # Clean formatting noise
        raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            # Convert to JSON
            data = json.loads(raw)
        except Exception as e:
            return f"❌ JSON decode error: {e}"

        # Save cleaned JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return f"✅ Clean JSON saved to: {output_path}"
