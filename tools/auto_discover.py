# auto_discover.py
# WordForge Cortex - Auto Concept Discovery

import os
import json
import re
from datetime import datetime

# === Configuration ===
BASE_PATH = os.path.expanduser("~/my_ai_project_cortex/brain_memory_modules/science")

# === Sample input snippet ===
snippet = "Photosynthesis converts light energy into chemical energy in plants."
# === Step 1: Extract Concept Candidate ===
def extract_concept(text):
    # Simulate NLP keyword detection with simple regex or keyword match
    keyword_map = {
        "quantum tunneling": ["particles", "energy", "barriers"],
        "gravity": ["force", "mass", "attraction"],
        "photosynthesis": ["light", "plants", "glucose"]
    }
    for concept, keywords in keyword_map.items():
        if concept.lower() in text.lower():
            return concept.title(), "physics" if "quantum" in concept else "biology", keywords
    return None, None, []

concept, field, keywords = extract_concept(snippet)
if not concept:
    print("❌ No known concept detected in snippet.")
    exit()

# === Step 2: Format Concept JSON ===
semantic_id = f"{field[:4]}*{concept.lower().replace(' ', '*')}_001"
concept_entry = {
    "domain": "science",
    "field": field,
    "concept": concept,
    "status": "discovered_from_snippet",
    "semantic_id": semantic_id,
    "keywords": keywords
}

# === Step 3: Ensure directory structure ===
entry_dir = os.path.join(BASE_PATH, field, "entries")
os.makedirs(entry_dir, exist_ok=True)

# === Step 4: Write concept entry ===
entry_filename = concept.lower().replace(" ", "_") + ".json"
entry_path = os.path.join(entry_dir, entry_filename)

with open(entry_path, 'w') as f:
    json.dump(concept_entry, f, indent=2)
print(f"✅ Concept saved: {entry_path}")

# === Step 5: Update field index ===
index_path = os.path.join(BASE_PATH, field, f"{field}_index.json")
if os.path.exists(index_path):
    with open(index_path, 'r') as f:
        index_data = json.load(f)
else:
    index_data = {"entries": []}

if entry_filename not in index_data["entries"]:
    index_data["entries"].append(entry_filename)
    with open(index_path, 'w') as f:
        json.dump(index_data, f, indent=2)
    print(f"🧠 Index updated: {index_path}")
else:
    print("ℹ️ Entry already exists in index.")
