import os

import requests

API_URL = "https://ollama.com/api/chat"
HEADERS = {"Authorization": "Bearer " + os.environ["OLAMA_API_KEY"]}

FEDERAL_REGISTER_URL = "https://www.federalregister.gov/api/v1/documents.json"
START_DATE = "2026-10-24"


def get_rules():
    params = {
        "conditions[agencies][]": "education-department",
        "conditions[type][]": ["RULE", "PRORULE"],
        "conditions[publication_date][gte]": START_DATE,
        "fields[]": ["title", "type", "publication_date", "abstract", "html_url"],
        "per_page": 100,
    }
    response = requests.get(FEDERAL_REGISTER_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    rules_text = ""
    for rule in data["results"]:
        rules_text += f"Title: {rule['title']}\n"
        rules_text += f"Type: {rule['type']}\n"
        rules_text += f"Published: {rule['publication_date']}\n"
        rules_text += f"Abstract: {rule['abstract']}\n"
        rules_text += f"Link: {rule['html_url']}\n\n"
    return rules_text


def agent(messages):
    system_message = {
        "role": "system",
        "content": "You are a helpful education policy AI assistant, "
            "only provide information that is provided to you in the message history."
    }

    messages.insert(0, system_message)

    rules_text = get_rules()

    rules_message = {
        "role": "system",
        "content": f"Here are the Department of Education rules from the Federal Register "
            f"published since {START_DATE}:\n{rules_text}"
    }

    messages.insert(1, rules_message)

    payload = {
        "model": "gpt-oss:120b",
        "messages": messages,
        "stream": False,
    }
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


question = """
Summarize these Department of Education rules in plain English.
    Put final rules first, then proposed rules. For each one, say in
    2 to 4 short sentences what it changes, who it affects, and why,
    and include its link.
"""

messages = [{"role": "user", "content": question}]
answer = agent(messages)
print(answer)

with open("education_rules_report.md", "w") as file:
    file.write(answer)