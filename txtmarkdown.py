import asyncio
import time

import requests

from secretsData import YANDEX_API_KEY,YANDEX_FOLDER_ID,gpt_model

folder_id = YANDEX_FOLDER_ID
api_key = YANDEX_API_KEY

async def txt_markdown(user_prompt: str) -> str:
    system_prompt = "Copy---title:- AI Playgroundauthor:- Ashwin Kumar Karnadtheme:- Copenhagendate:- March 22, 2020--- # What's AI?- Artificial Intelligence- The ability of machine to think and behave like humans.- How does the machine learn on its own? - That is called Machine Learning. ML is the study of computer algorithms that improve automatically with experience.- Just like humans learn with experience - Machines also learn with experience!- Examples of common AI? Alexa, Siri, Google Home, Self Driving Cars, Robots etc.# What's out there?![Verticles](img/Untitled.png)# How do computers make decisions?- Conditional statements are used to perform different actions based on different conditions.- In many programming languages, decisions (also called conditionals) take the form of an if-then construct. They start with a condition, which is then evaluated as either True or False.# How do computers make decisions?![Flow chart](img/Untitled 1.png){ width=250px } Сделай конспект на русском языке в этом стиле"
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
    if response.status_code != 200:
        return f"Ошибка запроса: {response.text}"

    operation_id = response.json().get('id')

    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {api_key}"}

    while True:
        print(operation_id)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Ошибка получения ответа: {response.text}"
        done = response.json().get("done", False)
        if done:
            break
        await asyncio.sleep(2)

    return response.json().get('response', {}).get('alternatives', [{}])[0].get('message', {}).get('text', "Ошибка обработки ответа")

