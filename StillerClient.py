import re
import os
from telethon import TelegramClient, events
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

channel_id = 1002096895063

client = TelegramClient(name_session, api_id, api_hash)

SAVE_FOLDER = config["PATH_FILE"]
#Проверка создана ли директория
#================================================================
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
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
@client.on(events.NewMessage(chats=channel_id))
async def new_message(event):
    # Извлекаем текст сообщения
    message_text = event.message.message or ""

    # Проверяем наличие ссылок в тексте сообщения и пропускаем, если есть
    if re.search(r'https?://', message_text):
        print("Сообщение с ссылкой, не проходит по параметрам!")
        return  # Пропускаем обработку и ждём следующего события

    if event.message.grouped_id:
        group_id = event.message.grouped_id
        # Формируем уникальное имя файла на основе его ID, в зависимости от его типа (фото или видео)
        if event.message.photo:
            format = "group"
            ext = ".jpg"
            media_id = event.message.photo.id
        elif event.message.video:
            format = "group"
            ext = ".mp4"
            media_id = event.message.video.id
        else:
            return  # Пропускаем, если медиа не является ни фото, ни видео
        img_name = f"{media_id}{ext}"
        img_path = os.path.join(SAVE_FOLDER, img_name)

        # Скачиваем медиа-файл асинхронно и сохраняем на диск
        await event.message.download_media(file=img_path)
        create_databases(connection)
        create_table(connection)
        # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
        add_new_mem_group(connection, group_id, img_path, img_name, format, message_text)
        print(f"Картинка сохранено: {img_path}")  # Стандартное термининальное оповищение.

    # Проверяем, есть ли у сообщения медиа в виде фото
    elif event.message.photo:
        # Даем уникальное имя для изображения на основании его ID в Telegram
        img_name = f"{event.message.photo.id}.jpg"
        format = 'jpg'
        # Путь, по которому будет сохранено изображение
        img_path = os.path.join(SAVE_FOLDER, img_name)
        # Скачиваем медиа-файл асинхронно и сохраняем на диск
        await event.message.download_media(file=img_path)
        # Вызываем функцию для создания таблицы\БД для фото в MySQL, если она еще не создана
        create_databases(connection)
        create_table(connection)
        # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
        add_new_mem(connection, img_path, img_name, format, message_text)
        print(f"Картинка сохранено: {img_path}")  # Стандартное термининальное оповищение.

    # Проверяем, есть ли у сообщения анимированные изображения типа GIF
    elif event.message.gif or (event.message.document and event.message.document.mime_type == 'image/gif'):
        gif_name = f"{event.message.id}.gif"
        # Путь, где будет сохранено анимированное изображение
        gif_path = os.path.join(SAVE_FOLDER, gif_name)
        format = 'gif'
        # Скачиваем асинхронно и сохраняем на диск
        await event.message.download_media(file=gif_path)
        # Вызываем функцию для создания таблицы\БД для фото в MySQL, если она еще не создана
        create_databases(connection)
        create_table(connection)
        # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
        add_new_mem(connection, gif_path, gif_name, format, message_text)
        print(f"GIF сохранён: {gif_path}")

    # Проверяем, содержит ли сообщение видео
    elif event.message.video:
        video_name = f"{event.message.video.id}.mp4"
        format = 'video'
        # Путь, где будет сохранено анимированное видео
        video_path = os.path.join(SAVE_FOLDER, video_name)
        # Скачиваем асинхронно и сохраняем на диск
        await event.message.download_media(file=video_path)
        # Вызываем функцию для создания таблицы\БД для фото в MySQL, если она еще не создана
        create_databases(connection)
        create_table(connection)
        # Добавляем новую запись в MySQL с путем до картинки, названием и текстом
        add_new_mem(connection, video_path, video_name, format, message_text)
        print(f"Видео сохранено: {video_path}")


    else:
        print("Неопознная ошибка")


# Запуск клиента
client.start(password=config["PASSOWORD_TG"])#Необходим пароль если у вас влюченеа двухфакторная аутентификация телеграм
client.run_until_disconnected()#Позволяет циклу идти бесконечно

