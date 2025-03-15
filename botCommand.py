import asyncio
import os
import subprocess

from PyPDF2 import PdfReader
from aiogram import F, Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InputFile, ReplyKeyboardRemove
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

type_your = "На основе моих идей / записей"
type_books = "Наши материалы"

@router.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=type_your), KeyboardButton(text=type_books)]
    ],
        resize_keyboard = True,
        input_field_placeholder = "Выберите, на основе чего вы хотите получить базу для вашей лекции:"
    )
    await message.answer("Добро пожаловать\n\nЯ - помощник в создании плана для лекции, помогу вам составить:\n- План лекции по пунктам\n- тесты по данной теме\n- Презентацию для лекции по данной теме\n\nДля основы для формирования плана лекции ты можешь использовать:\n- Голосовое сообщение\n- Аудио-файл (формат mp3)\n- Запись вашей/чужой лекции, структуру которой вы хотите повторить\n- Использовать официальные учебники по предмету", reply_markup=keyboard)


@router.message(F.text == type_your)
async def classic(message: Message):
    await message.answer("Вы можете прислать для обратки:\n- Голосовые сообщения\n- Телеграм-кружочек\n- Аудио файл\n- Видео файл", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == type_books)
async def books(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Биология"), KeyboardButton(text="Иные предметы (в скором времени)")]
    ],
        resize_keyboard = True
    )
    await message.answer("Выберите предмет", reply_markup=keyboard)


@router.message(F.text == "Биология")
async def biology(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="1 параграф"), KeyboardButton(text="2 параграф")]
    ],
        resize_keyboard=True
    )
    await message.answer("Выберите параграф", reply_markup=keyboard)

@router.message(F.text == "Иные предметы (в скором времени)")
async def biology(message: Message):
    await message.answer("Тут пока что пусто, загляните в другие вкладки, там много интересного!", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "1 параграф")
async def paragraph_one(message: Message):
    wait = await message.answer('Загружаю параграф...', reply_markup=ReplyKeyboardRemove())
    user_id = str(message.from_user.id)
    with open("docs/books/biology/paragraph_one.txt", "r") as file:
        result = file.read()
        await wait.delete()
        task = asyncio.create_task(print_info(message, user_id, result, True))
        await task


@router.message(F.text == "2 параграф")
async def paragraph_two(message: Message):
    wait = await message.answer('Загружаю параграф...', reply_markup=ReplyKeyboardRemove())
    user_id = str(message.from_user.id)
    with open("docs/books/biology/paragraph_two.txt", "r") as file:
        result = file.read()
        await wait.delete()
        task = asyncio.create_task(print_info(message, user_id, result, True))
        await task


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

    task = asyncio.create_task(print_info(message, user_id, file_id, False))

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

    task = asyncio.create_task(print_info(message, user_id, file_id, False))

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

    task = asyncio.create_task(print_info(message, user_id, file_id, False))

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

    task = asyncio.create_task(print_info(message, user_id, file_id, False))

    await task

    os.remove(f"{user_id}_{file_id}.mp4")
    os.remove(f"{user_id}_{file_id}.mp3")


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text


@router.message(lambda message: message.document is not None)
async def handle_pdf(message: types.Message):
    if message.document.mime_type == 'application/pdf':
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await bot.download_file(file_path)

        temp_file = f"temp_{file_id}.pdf"
        with open(temp_file, 'wb') as f:
            f.write(downloaded_file.read())

        text = extract_text_from_pdf(temp_file)

        os.remove(temp_file)

        if text:
            task = asyncio.create_task(print_info(message, str(message.from_user.id), text, True))
            await task
        else:
            await message.reply("Не удалось извлечь текст из PDF.")
    else:
        await message.reply("Пожалуйста, отправьте PDF-файл.")


async def print_info(message: types.Message, user_id: str, file_id: str, book: bool):
    try:
        if not book:
            wait = await message.answer('Распознаю речь...')
            text = await recognize_speech(f"{user_id}_{file_id}")
            if not text:
                await wait.delete()
                await message.answer("Не удалось распознать речь. Вы можете попробовать ещё раз, а я попробую вам помочь")
                return

            await wait.delete()
        else:
            text = file_id

        wait = await message.answer('Создаю план лекции...')

        try:
            text_sum = await text_to_sum(text)
            await message.answer(f"План лекции по теме:\n\n{text_sum}")
        except Exception as e:
            await message.answer("Это интересная тема, но у меня не удалось создать план. Повтори попозже, пожалуйста.")

        await wait.delete()

        wait = await message.answer('Придумываю вопросы по теме... ')

        try:
            test = await get_test(text)
            await message.answer(f"Тест по теме:\n\n{test}")
        except Exception as e:
            await message.answer("Извините, у меня не получилось придумать тесты. Повтори попозже, пожалуйста.")

        await wait.delete()

        wait = await message.answer('Верстаю презентацию по теме...')

        markdown = await txt_markdown(text)
        if books:
            file_id = user_id + "biology"
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
            await wait.delete()
            await message.reply_document(pdf_file)
        except subprocess.CalledProcessError as e:
            await wait.delete()
            await message.answer(
                f"У меня не получилось создать файл pdf, вы можете попробовать ещё раз или использовать конвертеры.\n\nФормат markdown для создания презентации:\nСервисы для конвертации MD в PFD\nhttps://apitemplate.io/pdf-tools/convert-markdown-to-pdf/\n\nhttps://www.markdowntopdf.com/")
            await message.answer(markdown)
    except Exception as e:
        await message.answer(f"Ой, что-то явно пошло не так. Попробуйте ещё раз, пожалуйста.\n{str(e)}")
