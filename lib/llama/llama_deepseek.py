import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def LlamaDeepseek(
    prompt,
    system="你现是一个叫小豆子的智能助手，回答简洁不超过100字，语气可爱",
    model="deepseek-chat",
):
    url = "https://api.deepseek.com/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    
    headers = {
        "Authorization": f"Bearer {os.getenv('LLAMA_DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"


if __name__ == "__main__":
    response = LlamaDeepseek("你好")
    print("回答:", response)
