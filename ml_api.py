import requests
import json


def get_embeddings(inputs):
    url = "http://localhost:11434/api/embed"
    data = {
        "model": "all-minilm",
        "input": inputs
    }
    response = requests.post(url, json=data)
    return response.json()['embeddings']


def prompt_response(prompt_text):
    url = "http://localhost:11434/api/chat"
    data = {
        "model": "granite3.2:2b",
        "messages": [
            {"role": "user", "content": f"{prompt_text}"}
        ]
    }
    
    response = requests.post(url, json=data, stream=True)

    if response.status_code == 200:
        response_text = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        response_text += data['message']['content']
                except json.JSONDecodeError:
                    print(f'Failed to parse the {line}')
    else:
        print(f'Error: {response.status_code}')
        print(response.text)

    return response_text
    