import requests
from datetime import datetime


def LlamaOllama(
    prompt,
    system="你现是一个叫小云小云的智能助手，回答简洁不超过100字，语气可爱",
    model="qwen2.5:14b",
):
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"


if __name__ == "__main__":
    begin = datetime.now().timestamp()
    response = LlamaOllama("你好")
    print("回答:", response, (datetime.now().timestamp() - begin) * 1000)
