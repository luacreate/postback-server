import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Получение URL для подключения к базе данных из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL переменная окружения не найдена")

# Создание таблицы для хранения постбэков
def create_table():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS postbacks (
                    id SERIAL PRIMARY KEY,
                    event_type TEXT,
                    amount REAL,
                    sub_id TEXT,
                    promo TEXT
                )
            ''')
        conn.commit()

create_table()

# Обработчик для приема постбэков
@app.route('/postback-handler', methods=['POST'])
def postback_handler():
    event_type = request.form.get('event_type')
    amount = request.form.get('amount')
    sub_id = request.form.get('sub_id')
    promo = request.form.get('promo')

    if event_type and amount and sub_id:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO postbacks (event_type, amount, sub_id, promo)
                    VALUES (%s, %s, %s, %s)
                ''', (event_type, float(amount), sub_id, promo))
            conn.commit()
        return "Постбэк успешно сохранен", 200
    else:
        return "Недостаточно данных для сохранения постбэка", 400

if __name__ == '__main__':
    # Установка порта и хоста из переменных окружения
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
