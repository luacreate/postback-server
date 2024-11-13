from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# Задаем путь к папке и файлу данных
DATA_DIR = './data'
DATA_FILE = os.path.join(DATA_DIR, 'data.json')

# Проверка, существует ли папка, и создание папки, если ее нет
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Создание пустого JSON файла, если его нет
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump([], file)

# Функция для чтения данных из файла
def read_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []

# Функция для записи данных в файл
def write_data(data):
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

# Обработчик для приема постбэков от 1WIN
@app.route('/postback-handler', methods=['GET'])
def postback_handler():
    text = request.args.get('text')

    if text:
        try:
            print(f"Получено значение text: {text}")
            parts = text.split(':')

            # Если формат неверный
            if len(parts) < 1 or len(parts) > 2:
                print("Ошибка: Некорректный формат text")
                return "Ошибка: Некорректный формат text", 400

            user_id = parts[0]
            amount = float(parts[1]) if len(parts) == 2 else 0.0  # Если сумма не указана, она равна 0

            # Чтение текущих данных из файла
            data = read_data()

            # Проверка, существует ли запись для данного user_id
            user_found = False
            for entry in data:
                if entry['user_id'] == user_id:
                    # Обновляем сумму депозита, если она указана
                    entry['amount'] += amount
                    user_found = True
                    break

            # Если запись не найдена, добавляем новую
            if not user_found:
                new_entry = {
                    "user_id": user_id,
                    "amount": amount
                }
                data.append(new_entry)

            # Запись обновленных данных в файл
            write_data(data)
            print("Постбэк успешно сохранен в JSON файл")
            return "Постбэк успешно сохранен", 200

        except ValueError as e:
            print(f"Ошибка при разборе строки text: {e}")
            return "Ошибка при разборе строки text", 400
    else:
        print("Параметр text не найден")
        return "Параметр text не найден", 400

# Маршрут для получения данных из data.json
@app.route('/data', methods=['GET'])
def get_data():
    try:
        data = read_data()
        return jsonify(data)
    except Exception as e:
        print(f"Ошибка при чтении data.json: {e}")
        return "Ошибка при чтении данных", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
