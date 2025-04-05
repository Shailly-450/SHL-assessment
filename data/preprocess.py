import json
import re

INPUT_FILE = "data/assessments.json"
OUTPUT_FILE = "data/assessments_enhanced.json"

def enhance_assessment(assessment):
    # Extract name from URL
    url = assessment["url"]
    name_match = re.search(r"view/(.+?)/?$", url)
    if name_match:
        assessment["name"] = name_match.group(1).replace("-", " ").title()

    # Infer test type and duration if not specified
    if "cognitive" in assessment["test_type"].lower():
        assessment["duration"] = "30 mins" if assessment["duration"] == "Not specified" else assessment["duration"]
    elif "skill" in assessment["name"].lower() or "coding" in assessment["name"].lower():
        assessment["test_type"] = "Skill"
        assessment["duration"] = "40 mins"
    elif "safety" in assessment["name"].lower():
        assessment["test_type"] = "Behavioral"
        assessment["duration"] = "25 mins"

    # Placeholder description
    assessment["description"] = f"Assessment for {assessment['name']} focusing on {assessment['test_type'].lower()} abilities."
    return assessment

with open(INPUT_FILE, 'r') as f:
    assessments = json.load(f)

enhanced_assessments = [enhance_assessment(a) for a in assessments]

with open(OUTPUT_FILE, 'w') as f:
    json.dump(enhanced_assessments, f, indent=2)

print(f"Enhanced data saved to {OUTPUT_FILE}")