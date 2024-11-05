import os
import psycopg2
from flask import Flask, request

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

# Создание таблицы для хранения постбэков
def create_table():
    try:
        print("Попытка подключения к базе данных для создания таблицы...")
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS postbacks (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT,
                        amount REAL
                    )
                ''')
            conn.commit()
        print("Таблица успешно создана или уже существует.")
    except psycopg2.Error as e:
        print(f"Ошибка при создании таблицы: {e}")

create_table()

# Обработчик для приема постбэков от 1WIN
@app.route('/postback-handler', methods=['GET'])
def postback_handler():
    # Получаем параметр text из URL
    text = request.args.get('text')
    
    if text:
        try:
            # Парсим строку text, чтобы получить данные
            print(f"Получено значение text: {text}")
            parts = text.split(':')

            # Проверка на наличие двух частей в строке
            if len(parts) != 2:
                print("Ошибка: Некорректный формат text")
                return "Ошибка: Некорректный формат text", 400

            user_id, amount = parts

            # Сохранение данных в базу данных
            try:
                print("Попытка подключения к базе данных для вставки данных...")
                with psycopg2.connect(DATABASE_URL) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute('''
                            INSERT INTO postbacks (user_id, amount)
                            VALUES (%s, %s)
                        ''', (user_id, float(amount)))
                    conn.commit()

                print("Постбэк успешно сохранен")
                return "Постбэк успешно сохранен", 200
            except psycopg2.Error as e:
                print(f"Ошибка базы данных при вставке данных: {e}")
                return "Ошибка базы данных", 500
        except ValueError as e:
            print(f"Ошибка при разборе строки text: {e}")
            return "Ошибка при разборе строки text", 400
    else:
        print("Параметр text не найден")
        return "Параметр text не найден", 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
