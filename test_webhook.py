import json

input_path = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\new_classified_stocks.json"
output_path = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\clean_classified_stocks.json"

# Read file as text
with open(input_path, "r", encoding="utf-8") as f:
    raw = f.read()

# Remove ALL ``` blocks
raw = raw.replace("```json", "").replace("```", "").strip()

# Convert to JSON
data = json.loads(raw)

# Save clean JSON
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✔ Clean JSON saved to:", output_path)
