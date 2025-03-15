import asyncio
import os
import subprocess

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
    await bot.download_file(file_path, f"{user_id}_{file_id}.mp4")

    video_clip = VideoFileClip(f"{user_id}_{file_id}.mp4")
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(f"{user_id}_{file_id}.mp3")

    audio_segment = AudioSegment.from_mp3(f"{user_id}_{file_id}.mp3")
    audio_segment.export(f"docs/audio/{user_id}_{file_id}.ogg", format="ogg")

    task = asyncio.create_task(print_info(message, user_id, file_id))

    await task

    os.remove(f"{user_id}_{file_id}.mp4")
    os.remove(f"{user_id}_{file_id}.mp3")


@router.message(lambda message: message.voice is not None)
async def handler_voice(message: types.Message):
    voice_ = message.voice
    file_id = voice_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    user_id = str(message.from_user.id)

    file_name = f"docs/audio/{user_id}_{file_id}.ogg"
    await bot.download_file(file_path, file_name)

    task = asyncio.create_task(print_info(message, user_id, file_id))

    await task


@router.message(lambda message: message.audio is not None)
async def handler_audio(message: types.Message):
    user_id = str(message.from_user.id)
    audio_ = message.audio
    file_id = audio_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{user_id}_{file_id}.mp3")

    audio_segment = AudioSegment.from_mp3(f"{user_id}_{file_id}.mp3")
    audio_segment.export(f"docs/audio/{user_id}_{file_id}.ogg", format="ogg")

    task = asyncio.create_task(print_info(message, user_id, file_id))

    await task

    os.remove(f"{user_id}_{file_id}.mp3")


@router.message(lambda message: message.video_note is not None)
async def handler_video_note(message: types.Message):
    user_id = str(message.from_user.id)
    video_note_ = message.video_note
    file_id = video_note_.file_id

    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{user_id}_{file_id}.mp4")

    video_clip = VideoFileClip(f"{user_id}_{file_id}.mp4")
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(f"{user_id}_{file_id}.mp3")

    audio_segment = AudioSegment.from_mp3(f"{user_id}_{file_id}.mp3")
    audio_segment.export(f"docs/audio/{user_id}_{file_id}.ogg", format="ogg")

    task = asyncio.create_task(print_info(message, user_id, file_id))

    await task

    os.remove(f"{user_id}_{file_id}.mp4")
    os.remove(f"{user_id}_{file_id}.mp3")


async def print_info(message: types.Message, user_id: str, file_id: str):
    try:
        text = await recognize_speech(f"{user_id}_{file_id}")
        if not text:
            await message.answer("Не удалось распознать речь.")
            return

        text_sum = await text_to_sum(text)
        await message.answer(f"Конспект по теме:\n\n{text_sum}")

        test = await get_test(text)
        await message.answer(f"Тест по теме:\n\n{test}")

        markdown = await txt_markdown(text)
        save_path_markdown = os.path.join("docs/markdown", f"{user_id}_{file_id}.txt")

        input_md = f"docs/markdown/{user_id}_{file_id}.txt"
        output_pdf = f"docs/presentation/{user_id}_{file_id}.pdf"
        command = [
            "pandoc",
            "-t",
            "beamer",
            input_md,
            "-o",
            output_pdf
        ]
        try:
            with open(save_path_markdown, "w", encoding="utf-8") as file:
                file.write(markdown)

            subprocess.run(command, check=True)
            pdf_file = FSInputFile(output_pdf)
            await message.reply_document(pdf_file)
        except subprocess.CalledProcessError as e:
            await message.answer(
                f"Формат markdown для создания презентации:\nСервисы для конвертации MD в PFD\nhttps://apitemplate.io/pdf-tools/convert-markdown-to-pdf/\n\nhttps://www.markdowntopdf.com/")
            await message.answer(markdown)
    except Exception as e:
        await message.answer(f"Ошибка обработки: {str(e)}")
