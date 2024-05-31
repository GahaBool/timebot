import asyncio
import os

from aiogram import Bot, Dispatcher, types
from mysql.connector import connect, Error, errorcode
from datetime import datetime, time, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import dotenv_values
from SQL_Qury import create_databases, create_table, show_image_from_db, show_media_from_db

#Создал файл специально, что бы можно было работать с личными данными.
#Необходимосоздать свой .env и туда закинуть все необходимы переменные с у которых стоит приписка "config"
#================================================================
config = dotenv_values()

def connection_db():
    try:
        connection = connect(host=config["HOST"],
                             user=config["USER"],
                             password=config["PASSWORD"],
                             db=config["DATABASES"],)
        create_databases(connection)
        create_table(connection)
        print("Bot working!")
        print("################################################################")
    except Error as err:
        print(f"The error '{err}' occurred")
    return connection

connection = connection_db()

#Бот aiogram
#================================================================
bot = Bot(config["TOKEN"])
dp = Dispatcher()

chat_id = -4222665779

def save_last_sent_id(last_id):
    with open("last_sent_id.txt", "w") as file:
        file.write(str(last_id))

def load_last_sent_id():
    try:
        with open("last_sent_id.txt", "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 1  # начнем с 1, если файл не найден

async def send_message(bot: bot):
    global last_sent_id
    last_sent_id = load_last_sent_id()  # Загрузить последний отправленный id при старте бота

    group_id, file_path, format, description = show_image_from_db(connection, last_sent_id)

    if format == "group":

        media_files_paths = show_media_from_db(connection, group_id)

        media_group = []

        text = ''

        for file_paths, file_description in media_files_paths:
            if file_path.endswith('.mp4'):  # Для видеофайлов
                media = types.InputMediaPhoto(media=types.FSInputFile(file_paths), caption=file_description)
            else:  # Для фотографий (предполагается, что все остальное - фотографии)
                media = types.InputMediaPhoto(media=types.FSInputFile(file_paths), caption=file_description)

            media_group.append(media)

        await bot.send_media_group(chat_id, media=media_group)

    elif format == "video":
        await bot.send_video(chat_id, video=types.FSInputFile(path=file_path), caption=description)
    elif format == "gif":
        await bot.send_animation(chat_id, animation=types.FSInputFile(path=file_path), caption=description)
    elif format == "jpg":
        await bot.send_photo(chat_id, photo=types.FSInputFile(path=file_path), caption=description)
    else:
        print("Такого формат не поддерживается!")

    last_sent_id += 1
    save_last_sent_id(last_sent_id)

async def telebot():
    await bot.delete_webhook(drop_pending_updates=True)
    scheduler = AsyncIOScheduler(timezone="Asia/Irkutsk")
    scheduler.add_job(send_message, trigger='cron', hour=14, minute=13, start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.start()
    await dp.start_polling(bot)


asyncio.run(telebot())