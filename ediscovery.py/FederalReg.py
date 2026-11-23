import os
from datetime import date, timedelta

import requests

# --- Settings ---
API_URL = "https://ollama.com/api/chat"
HEADERS = {"Authorization": "Bearer " + os.environ["OLAMA_API_KEY"]}
MODEL = "gpt-oss:20b"
FEDERAL_REGISTER_URL = "https://www.federalregister.gov/api/v1/documents.json"
DAYS_BACK = 30


# Step 1: get Department of Education proposed rules and final rules
def get_rules():
    start_date = date.today() - timedelta(days=DAYS_BACK)
    params = {
        "conditions[agencies][]": "education-department",
        "conditions[type][]": ["RULE", "PRORULE"],
        "conditions[publication_date][gte]": start_date.isoformat(),
        "fields[]": ["title", "type", "publication_date", "abstract", "html_url"],
        "per_page": 100,
    }
    response = requests.get(FEDERAL_REGISTER_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["results"]


# Step 3: ask Ollama for a plain-English summary of one rule
def summarize(rule):
    prompt = (
        "Explain this Department of Education rule in plain English "
        "in 2 to 4 short sentences: what it changes, who it affects, and why.\n\n"
        f"Title: {rule['title']}\n"
        f"Abstract: {rule['abstract']}"
    )
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=300)
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


# Run it
rules = get_rules()
print(f"Found {len(rules)} rules from the last {DAYS_BACK} days.\n")

# Step 2: split into final rules and proposed rules
final_rules = [rule for rule in rules if rule["type"] == "Rule"]
proposed_rules = [rule for rule in rules if rule["type"] == "Proposed Rule"]

report = "# Department of Education rules\n\n"
for heading, group in [("Final rules", final_rules), ("Proposed rules", proposed_rules)]:
    report += f"## {heading} ({len(group)})\n\n"
    for rule in group:
        print(f"Summarizing: {rule['title']}")
        summary = summarize(rule)
        report += f"### {rule['title']}\n"
        report += f"Published {rule['publication_date']}\n\n"
        report += f"{summary}\n\n"
        report += f"Link: {rule['html_url']}\n\n"

# Step 4: save the report
with open("education_rules_report.md", "w") as file:
    file.write(report)

print()
print(report)
print("Saved to education_rules_report.md")