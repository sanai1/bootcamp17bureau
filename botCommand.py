import os

from aiogram import F, Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.utils.chat_action import ChatActionMiddleware
from moviepy import VideoFileClip
from pydub import AudioSegment

import secretsData
from STT import recognize_speech
from textToSum import text_to_sum
from getTest import get_test
from txtmarkdown import txt_markdown
from convertPDF import convert_presentation

router = Router()
bot = Bot(token=secretsData.token_bot)
router.message.middleware(ChatActionMiddleware())

type_voice = "Голосовое сообщение"
type_audio = "Аудио лекции"
type_video = "Видео лекции"
type_video_note = "Кружочек с лекции"

@router.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=type_voice), KeyboardButton(text=type_audio)],
        [KeyboardButton(text=type_video),KeyboardButton(text=type_video_note)]
    ],
        resize_keyboard = True,
        input_field_placeholder = "Выберите вариант данных?"
    )
    await message.answer("Добро пожаловать", reply_markup=keyboard)


@router.message(F.text == type_voice)
async def voice(message: Message):
    await message.answer("Запишите голосовое сообщение с описанием лекции, которую хотите провезти")


@router.message(F.text == type_audio)
async def audio(message: Message):
    await message.answer("Пришлите аудио-файл с лекцией")


@router.message(F.text == type_video)
async def video(message: Message):
    await message.answer("Пришлите видео-файл с лекцией")


@router.message(F.text == type_video_note)
async def video_note(message: Message):
    await message.answer("Пришлите кружочек с лекцией")


@router.message(lambda message: message.video is not None)
async def handler_video(message: types.Message):
    user_id = str(message.from_user.id)
    video_ = message.video
    file_id = video_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{user_id}.mp4")

    video_clip = VideoFileClip(f"{user_id}.mp4")
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(f"{user_id}.mp3")

    audio_segment = AudioSegment.from_mp3(f"{user_id}.mp3")
    audio_segment.export(f"docs/audio/{user_id}.ogg", format="ogg")

    await print_info(message, user_id)

    os.remove(f"{user_id}.mp4")
    os.remove(f"{user_id}.mp3")


@router.message(lambda message: message.voice is not None)
async def handler_voice(message: types.Message):
    voice_ = message.voice
    file_id = voice_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    user_id = str(message.from_user.id)
    await bot.download_file(file_path, f"docs/audio/{user_id}.ogg")

    await print_info(message, user_id)


@router.message(lambda message: message.audio is not None)
async def handler_audio(message: types.Message):
    user_id = str(message.from_user.id)
    audio_ = message.audio
    file_id = audio_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{user_id}.mp3")

    audio_segment = AudioSegment.from_mp3(f"{user_id}.mp3")
    audio_segment.export(f"docs/audio/{user_id}.ogg", format="ogg")

    await print_info(message, user_id)

    os.remove(f"{user_id}.mp3")


@router.message(lambda message: message.video_note is not None)
async def handler_video_note(message: types.Message):
    user_id = str(message.from_user.id)
    video_note_ = message.video_note

    file = await bot.get_file(video_note_.file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{user_id}.mp4")

    video_clip = VideoFileClip(f"{user_id}.mp4")
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(f"{user_id}.mp3")

    audio_segment = AudioSegment.from_mp3(f"{user_id}.mp3")
    audio_segment.export(f"docs/audio/{user_id}.ogg", format="ogg")

    await print_info(message, user_id)

    os.remove(f"{user_id}.mp4")
    os.remove(f"{user_id}.mp3")


async def print_info(message: types.Message, user_id: str):
    text = recognize_speech(user_id)
    print(text == "")
    text_sum = text_to_sum(text)
    await message.answer(f"Конспект по теме:\n\n{text_sum}")

    tests = get_test(text_sum)
    await message.answer(f"Тесты по конспекту:\n\n{tests}")

    markdown = txt_markdown(text_sum)
    await message.answer(f"Формат markdown для создания презентации:\nСервисы для конвертации MD в PFD\nhttps://apitemplate.io/pdf-tools/convert-markdown-to-pdf/\n\nhttps://www.markdowntopdf.com/")
    await message.answer(markdown)












