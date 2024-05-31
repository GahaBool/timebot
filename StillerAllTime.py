import re
import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
from mysql.connector import connect, Error
from SQL_Qury import create_databases, create_table, add_new_mem, add_new_mem_group

from dotenv import dotenv_values

#Создал файл специально, что бы можно было работать с личными данными.
#Необходимосоздать свой .env и туда закинуть все необходимы переменные с у которых стоит приписка "config"
#================================================================
config = dotenv_values()

name_session = 'MemBot'

api_id = config["API_ID"]
api_hash = config["API_HASH"]

client = TelegramClient(name_session, api_id, api_hash)

channel_id = config[ID_SlillerAllTime]#'https://t.me/qa_memes' # 1001123683328

SAVE_FOLDER = -1002240980053

#Подключение к базам MySQL
#================================================================
def connection_db():
    try:
        connection = connect(host=config["HOST"],
                             user=config["USER"],
                             password=config["PASSWORD"],
                             db=config["DATABASES"],)
        create_databases(connection)
        create_table(connection)
        print("MySQL connectint!")
        print("################################################################")
    except Error as err:
        print(f"The error '{err}' occurred")
    return connection

connection = connection_db()

#Автоматическое добавление сообщей в базу данных.
#================================================================
async def download_memes():
    async with TelegramClient(name_session, api_id, api_hash) as client:
        # Вы устанавливате reverse=True, чтобы перебирать сообщения от старых к новым
        async for message in client.iter_messages(channel_id, reverse=True):
            # Проверяем, является ли медиа в сообщении фотографией
            message_text = message.text or ''

            if message.grouped_id:
                group_id = message.grouped_id
                # Формируем уникальное имя файла на основе его ID, в зависимости от его типа (фото или видео)
                if message.photo:
                    format = "group"
                    ext = ".jpg"
                    media_id = message.photo.id
                elif message.video:
                    format = "group"
                    ext = ".mp4"
                    media_id = message.video.id
                else:
                    return  # Пропускаем, если медиа не является ни фото, ни видео
                img_name = f"{media_id}{ext}"
                img_path = os.path.join(SAVE_FOLDER, img_name)

                # Скачиваем медиа-файл асинхронно и сохраняем на диск
                await message.download_media(file=img_path)
                create_databases(connection)
                create_table(connection)
                # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
                add_new_mem_group(connection, group_id, img_path, img_name, format, message_text)
                print(f"Картинка\Видео медиа группы сохранено: {img_path}")  # Стандартное термининальное оповищение.

            elif message.photo:
                # Задаем путь, где будет сохранено фото
                file_name = f"{message.photo.id}.jpg"
                format = 'jpg'
                file_path = os.path.join(SAVE_FOLDER, file_name)
                # Скачиваем медиа-файл асинхронно и сохраняем на диск
                await message.download_media(file=file_path)
                # Вызываем функцию для создания таблицы\БД для фото в MySQL, если она еще не создана
                create_databases(connection)
                create_table(connection)
                # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
                add_new_mem(connection, file_path, file_name, format, message_text)
                print(f"Фото сохранено: {file_path}")

            elif message.gif:
                gif_name = f"{message.id}.gif"
                # Путь, где будет сохранено анимированное изображение
                gif_path = os.path.join(SAVE_FOLDER, gif_name)
                format = 'gif'
                # Скачиваем асинхронно и сохраняем на диск
                await message.download_media(file=gif_path)
                # Вызываем функцию для создания таблицы\БД для фото в MySQL, если она еще не создана
                create_databases(connection)
                create_table(connection)
                # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
                add_new_mem(connection, gif_path, gif_name, format, message_text)
                print(f"GIF сохранён: {gif_path}")

            # Проверяем, содержит ли сообщение видео
            elif message.video:
                video_name = f"{message.video.id}.mp4"
                format = 'video'
                # Путь, где будет сохранено анимированное видео
                video_path = os.path.join(SAVE_FOLDER, video_name)
                # Скачиваем асинхронно и сохраняем на диск
                await message.download_media(file=video_path)
                # Вызываем функцию для создания таблицы\БД для фото в MySQL, если она еще не создана
                create_databases(connection)
                create_table(connection)
                # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
                add_new_mem(connection, video_path, video_name, format, message_text)
                print(f"Видео сохранено: {video_path}")


            else:
                print("Такой файл не поддерживается!")

# Запускаем скачивание фотографий
loop = asyncio.get_event_loop()
loop.run_until_complete(download_memes())