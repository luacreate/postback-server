import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Получение URL для подключения к базе данных из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL")

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
    promo = request.form.get('promo')  # Информация о промо, которая будет использоваться для проверки

    # Сохранение данных в базу данных PostgreSQL
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

# Обработчик для проверки ID
@app.route('/check-id', methods=['GET'])
def check_id():
    sub_id = request.args.get('sub_id')

    if sub_id:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT SUM(amount), promo FROM postbacks WHERE sub_id = %s GROUP BY promo', (sub_id,))
                result = cursor.fetchone()
                if result and result[0] > 4.5 and result[1]:  # Проверка суммы депозита > 4.5 и наличия промо
                    return jsonify({"exists": True})
                else:
                    return jsonify({"exists": False})
    else:
        return jsonify({"error": "ID не предоставлен"}), 400

if __name__ == '__main__':
    app.run(port=5000)
