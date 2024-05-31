from mysql.connector import connect, Error


#Основная работа с БД
#================================================================
def create_databases(connection):
    cursor = connection.cursor()
    databeses = """CREATE DATABASE IF NOT EXISTS qa_memes;"""
    try:
        cursor.execute(databeses)
    except Error as err:
        print(f"The error '{err}' occurred")


def create_table(connection):
    cursor = connection.cursor()
    table = """CREATE TABLE IF NOT EXISTS memes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_id VARCHAR(255),
            file_path TEXT,
            image_name VARCHAR(255),
            format VARCHAR(255),
            description TEXT
        );"""
    try:
        cursor.execute(table)
    except Error as err:
        print(f"The error '{err}' occurred")


def add_new_mem(connection, imag, image_name, format, text):
    cursor = connection.cursor()
    table = """INSERT INTO MEMES (file_path, image_name, format, description) VALUES (%s, %s, %s, %s);"""
    try:
        cursor.execute(table, (imag, image_name, format, text))
    except Error as err:
        print(f"The error '{err}' occurred")
    connection.commit()


def add_new_mem_group(connection, group_id, imag, image_name, format, text):
    cursor = connection.cursor()
    table = """INSERT INTO MEMES (group_id, file_path, image_name, format, description) VALUES (%s, %s, %s, %s, %s);"""
    try:
        cursor.execute(table, (group_id, imag, image_name, format, text))
    except Error as err:
        print(f"The error '{err}' occurred")
    connection.commit()


# Функция для показа изображения из БД
def show_image_from_db(connection, img_int):
    try:
        cursor = connection.cursor()
        query_photo = """SELECT group_id, file_path, format, description FROM qa_memes.memes WHERE id = (%s);"""
        # Выполняем запрос для поиска пути изображения по ID
        cursor.execute(query_photo, [img_int])
        record = cursor.fetchone()
        if record:
            group_id, file_path, format, description = record
            return group_id, file_path, format, description  # Возвращаем путь к изображению и описание
        else:
            return None

    except Error as e:
        print(f"Error: {e}")
        return None


# Функция для получения медиафайлов из базы данных по group_id
def show_media_from_db(connection, group_id):
    cursor = connection.cursor()
    # Формируем запрос на выборку всех путей к файлам для заданного group_id
    group_id_query = "SELECT file_path, description FROM qa_memes.memes WHERE group_id = %s"
    cursor.execute(group_id_query, (group_id,))  # Используем кортеж для параметров запроса
    media_files = cursor.fetchall()
    cursor.close()  # Закрываем курсор после выполнения запроса
    # Извлекаем из списка кортежей только пути к файлам и возвращаем их в виде списка
    #file_paths = [file_path_tuple[0] for file_path_tuple in media_files] if media_files else []
    return media_files