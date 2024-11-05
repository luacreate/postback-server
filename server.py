import os
import psycopg2
from flask import Flask, request

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

# Создание таблицы для хранения постбэков
def create_table():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS postbacks (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT,
                    country TEXT,
                    event_type TEXT,
                    amount REAL,
                    currency TEXT
                )
            ''')
        conn.commit()

create_table()

# Обработчик для приема постбэков от 1WIN
@app.route('/postback-handler', methods=['GET'])
def postback_handler():
    # Получаем параметр text из URL
    text = request.args.get('text')
    
    if text:
        try:
            # Парсим строку text, чтобы получить данные
            user_id, country, event_type, amount, currency = text.split(':')

            # Сохраняем данные в базу данных
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO postbacks (user_id, country, event_type, amount, currency)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (user_id, country, event_type, float(amount), currency))
                conn.commit()

            return "Постбэк успешно сохранен", 200
        except ValueError:
            return "Ошибка при разборе строки text", 400
    else:
        return "Параметр text не найден", 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
