import requests
from aiogram.types import FSInputFile

from secretsData import stt_token_bot, folder_id

def recognize_speech(file_name, lang='ru-RU'):
    url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={folder_id}&lang={lang}"
    headers = {
        "Authorization": f"Api-Key {stt_token_bot}"
    }

    with open('docs/audio/' + file_name + '.ogg', "rb") as audio_file:
        response = requests.post(url, headers=headers, data=audio_file)

    if response.status_code == 200:
        return response.json().get("result", "Ошибка: не удалось распознать речь")
    else:
        return f"Ошибка: {response.status_code}, {response.text}"