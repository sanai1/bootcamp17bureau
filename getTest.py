import time

import requests

from secretsData import YANDEX_API_KEY,YANDEX_FOLDER_ID,gpt_model

folder_id = YANDEX_FOLDER_ID
api_key = YANDEX_API_KEY

def get_test(user_prompt):
    system_prompt = 'Тебе дается текст лекции. Сделай тест с выбором ответа на основе текста лекции. Сделай 5 вопросов. Для каждого вопроса должно быть 4 варианта ответа и только один верный. Пометь правильный ответ на вопрос с помощью символа звездочки. НЕ ГОВОРИ НИЧЕГО КРОМЕ ЭТОГО'
    body = {
        'modelUri': f'gpt://{folder_id}/{gpt_model}',
        'completionOptions': {'stream': False, 'temperature': 0.4, 'maxTokens': 1000},
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

    data = response.json()
    answer = data['response']['alternatives'][0]['message']['text']
    return(answer)
