import time

import requests

from secretsData import YANDEX_API_KEY,YANDEX_FOLDER_ID,gpt_model

folder_id = YANDEX_FOLDER_ID
api_key = YANDEX_API_KEY

def text_to_sum(user_prompt) -> str:
    system_prompt = 'Please continue taking notes in the established format. Remember to: 1. Create concise, easy-to-understand advanced bullet-point notes. 2. Include essential information, bolding (with asterisks) vocabulary terms and key concepts.3. Remove extraneous language, focusing on critical aspects.4. Base your notes strictly on the provided passages.5. Conclude with to indicate completion, where represents the total number of messages that I have sent (message counter).Your notes will help me better understand the material and prepare for the exams. Отвечай строго на русском языке!!!'
    body = {
        'modelUri': f'gpt://{folder_id}/{gpt_model}',
        'completionOptions': {'stream': False, 'temperature': 0.3, 'maxTokens': 2000},
        'messages': [
        {'role': 'system', 'text': system_prompt},
        {'role': 'user', 'text': user_prompt},
        ],
        }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync'
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {api_key}'
        }

    response = requests.post(url, headers=headers, json=body)
    operation_id = response.json().get('id')

    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        done = response.json()["done"]
        if done:
            break
        time.sleep(2)

    return response.json()['response']['alternatives'][0]['message']['text']
