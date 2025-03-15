import asyncio
import time

import requests

from secretsData import YANDEX_API_KEY, YANDEX_FOLDER_ID, gpt_model

folder_id = YANDEX_FOLDER_ID
api_key = YANDEX_API_KEY


async def txt_markdown(user_prompt: str) -> str:
    # system_prompt = "Напиши ответ СТРОГО НА АНГЛИЙСКОМ!!! Создай markdown для pandoc презентации на основе текста. Для заголовка используй # после, которой должно идти название слайда. Для перечисления используй '-' перед пунктами списка. Запиши только основные моменты в эту презентацию. Длина презентации составляет 5 слайдов. Не пронумеровывай слайды. После символа # должно идти название слайда, не его номер. ОТВЕЧАЙ СТРОГО НА АНГЛИЙСКОМ! НЕ НУМЕРУЙ СЛАЙДЫ! ЗРИТЕЛЬ НЕ ДОЛЖЕН ЗНАТЬ КАКОЙ НОМЕР У СЛАЙДА! НЕ НУЖНО ЕМУ ЕГО СООБЩАТЬ! Переведи результат на английский язык"
    system_prompt = "Write the answer STRICTLY IN ENGLISH!!! Create markdown for pandoc text-based presentations. For the title, use the # after which the slide name should go. To list, use the '-' before the list items. Write down only the main points in this presentation. The presentation is 5 slides long. Don't number the slides. The # symbol should be followed by the slide name, not its number. ANSWER STRICTLY IN ENGLISH! ONLY IN ENGLISH LANGUAGE! DO NOT USE RUSSIAN. TRANSLATE ON ENGLISH!!!"
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
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Ошибка получения ответа: {response.text}"
        done = response.json().get("done", False)
        if done:
            break
        await asyncio.sleep(2)

    return response.json().get('response', {}).get('alternatives', [{}])[0].get('message', {}).get('text',
                                                                                                   "Ошибка обработки ответа")
