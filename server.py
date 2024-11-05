import os
import json
from flask import Flask, request

app = Flask(__name__)

# Имя файла, в который будем сохранять данные
DATA_FILE = 'data.json'

# Создание пустого JSON файла, если его нет
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump([], file)

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
            amount = float(amount)

            # Чтение текущих данных из файла
            try:
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)

                # Проверка, существует ли запись для данного user_id
                user_found = False
                for entry in data:
                    if entry['user_id'] == user_id:
                        # Обновляем сумму депозита
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
                with open(DATA_FILE, 'w') as file:
                    json.dump(data, file, indent=4)

                print("Постбэк успешно сохранен в JSON файл")
                return "Постбэк успешно сохранен", 200
            except Exception as e:
                print(f"Ошибка при сохранении в файл: {e}")
                return "Ошибка при сохранении данных", 500
        except ValueError as e:
            print(f"Ошибка при разборе строки text: {e}")
            return "Ошибка при разборе строки text", 400
    else:
        print("Параметр text не найден")
        return "Параметр text не найден", 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
