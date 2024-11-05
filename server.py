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
                    event_id TEXT,
                    date BIGINT,
                    amount REAL,
                    transaction_id TEXT,
                    country TEXT,
                    user_id TEXT
                )
            ''')
        conn.commit()

create_table()

# Обработчик для приема постбэков от 1WIN
@app.route('/postback-handler', methods=['GET'])
def postback_handler():
    # Получаем параметры из URL
    event_id = request.args.get('event_id')
    date = request.args.get('date')
    amount = request.args.get('amount')
    transaction_id = request.args.get('transaction_id')
    country = request.args.get('country')
    user_id = request.args.get('user_id')
    
    # Проверка на наличие необходимых параметров
    if event_id and date and amount and transaction_id and country and user_id:
        try:
            # Сохранение данных в базу данных
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO postbacks (event_id, date, amount, transaction_id, country, user_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (event_id, int(date), float(amount), transaction_id, country, user_id))
                conn.commit()

            return "Постбэк успешно сохранен", 200
        except psycopg2.Error as e:
            print(f"Ошибка базы данных: {e}")
            return "Ошибка базы данных", 500
    else:
        return "Недостаточно данных для сохранения постбэка", 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
