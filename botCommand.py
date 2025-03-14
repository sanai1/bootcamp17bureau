import os

from aiogram import F, Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.utils.chat_action import ChatActionMiddleware
from moviepy import VideoFileClip
from pydub import AudioSegment

import secretsData

router = Router()
bot = Bot(token=secretsData.token_bot)
router.message.middleware(ChatActionMiddleware())

type_voice = "Голосовое сообщение"
type_audio = "Аудио лекции"
type_video = "Видео лекции"

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
    await message.answer("Пришлите аудио-файл с лекцией")


@router.message(F.text == type_video)
async def video(message: Message):
    await message.answer("Пришлите видео-файл с лекцией")


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

    import os
    os.remove(f"{user_id}_video.mp4")
    os.remove(f"{user_id}.ogg")


@router.message(lambda message: message.voice is not None)
async def handler_voice(message: types.Message):
    voice_ = message.voice
    file_id = voice_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "voice.ogg")

    # audio = AudioSegment.from_file("voice.ogg", format="ogg")
    # audio.export("voice.mp3", format="mp3")

    audio_file = FSInputFile("voice.ogg")
    await message.reply_audio(audio_file)

    os.remove("voice.ogg")


@router.message(lambda message: message.audio is not None)
async def handler_audio(message: types.Message):
    audio_ = message.audio
    file_id = audio_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "audio_file.mp3")

    audio_file = FSInputFile("audio_file.mp3")
    await message.reply_audio(audio_file)

    os.remove("audio_file.mp3")

















