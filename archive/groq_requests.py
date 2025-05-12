

import requests


INPUT_FILE_PATH = r"" # <Cesta ke vstupnímu textovému souboru, který má být zpracován>
GROQ_API_KEY = "" # <Groq API klíč>


URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GROQ_API_KEY}"
}

TEST_PROMPT = "Dokázal bys vyznačit osobní údaje v českých textech?\
                (např. jména, telefonní čisla, ...)"

data = {
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.3,
    "messages": [
        {"role": "user", "content": TEST_PROMPT}
    ]
}

response = requests.post(URL, headers=headers, json=data, timeout=10)


if response.status_code == 200:
    response_json = response.json()
    content = response_json["choices"][0]["message"]["content"]
    print(content)
else:
    print(f"Error {response.status_code}: {response.text}")


