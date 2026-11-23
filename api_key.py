import os

api_key = os.environ["OLAMA_API_KEY"]

print(api_key)
import os

import requests

api_url = "https://ollama.com/api/chat"
headers = {"Authorization": "Bearer " + os.environ["OLAMA_API_KEY"]}
payload = {
    "model": "gpt-oss:120b",
    "messages": [
        {"role": "user", "content": "how can we win the lottery"}

    
    "stream": False,
}

response = requests.post(
    api_url,
    headers=headers,
    json=payload,
    timeout=300,
)
response.raise_for_status()
data = response.json()

print(data["message"]["content"])