import os

from aiogram import F, Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.utils.chat_action import ChatActionMiddleware
from moviepy import VideoFileClip

import secretsData
from STT import recognize_speech
from textToSum import textToSum
from getTest import getTest
from txtmarkdown import txtmarkdown
from convertPDF import convert_presentation

router = Router()
bot = Bot(token=secretsData.token_bot)
router.message.middleware(ChatActionMiddleware())

type_voice = "Голосовое сообщение"
type_audio = "Аудио лекции (в разработке)"
type_video = "Видео лекции (в разработке)"

@router.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=type_voice)],
        [KeyboardButton(text=type_audio)],
        [KeyboardButton(text=type_video)]],
        resize_keyboard = True,
        input_field_placeholder = "Выберите вариант данных?"
    )
    await message.answer("Добро пожаловать", reply_markup=keyboard)


@router.message(F.text == type_voice)
async def voice(message: Message):
    await message.answer("Запишите голосовое сообщение с описанием лекции, которую хотите провезти")


@router.message(F.text == type_audio)
async def audio(message: Message):
    print()
    # await message.answer("Пришлите аудио-файл с лекцией")


@router.message(F.text == type_video)
async def video(message: Message):
    print()
    # await message.answer("Пришлите видео-файл с лекцией")


@router.message(lambda message: message.video is not None)
async def handler_video(message: types.Message):
    user_id = message.from_user.id
    video_ = message.video
    file_id = video_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{user_id}_video.mp4")

    video_clip = VideoFileClip(f"{user_id}_video.mp4")
    audio_clip = video_clip.audio

    audio_clip.write_audiofile(f"{user_id}.ogg", codec='libvorbis')

    ogg_audio_file = FSInputFile(f"{user_id}.ogg")

    await message.answer_audio(ogg_audio_file)

    os.remove(f"{user_id}_video.mp4")
    os.remove(f"{user_id}.ogg")


@router.message(lambda message: message.voice is not None)
async def handler_voice(message: types.Message):
    voice_ = message.voice
    file_id = voice_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    user_id = str(message.from_user.id)
    await bot.download_file(file_path, f"docs/audio/{user_id}.ogg")

    text = recognize_speech(user_id)
    print(text == "")
    text_sum = textToSum(text)
    await message.answer(f"Конспект по теме:\n\n{text_sum}")
    test = getTest(text)
    await message.answer(f"Тесты по конспекту:\n\n{test}")
    markdown = txtmarkdown(text)
    await message.answer(f"Формат markdown для создания презентации:\n\n{markdown}")
    # f = open(f"docs/presentation/{user_id}.txt", "w")
    # f.write(markdown)
    # convert_presentation(f"docs/presentation/{user_id}.txt", output_format="pdf")



@router.message(lambda message: message.audio is not None)
async def handler_audio(message: types.Message):
    user_id = str(message.from_user.id)
    audio_ = message.audio
    file_id = audio_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "audio_file.mp3")

    audio_file = FSInputFile("audio_file.mp3")
    await message.reply_audio(audio_file)

    os.remove("audio_file.mp3")

















