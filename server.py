from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Имя файла, в который будем сохранять данные
DATA_FILE = '/tmp/data.json'

# Создание пустого JSON файла, если его нет
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump([], file)

# Обработчик для приема постбэков от 1WIN
@app.route('/postback-handler', methods=['GET'])
def postback_handler():
    text = request.args.get('text')
    
    if text:
        try:
            print(f"Получено значение text: {text}")
            parts = text.split(':')

            if len(parts) != 2:
                print("Ошибка: Некорректный формат text")
                return "Ошибка: Некорректный формат text", 400

            user_id, amount = parts
            amount = float(amount)

            try:
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)

                user_found = False
                for entry in data:
                    if entry['user_id'] == user_id:
                        entry['amount'] += amount
                        user_found = True
                        break

                if not user_found:
                    new_entry = {
                        "user_id": user_id,
                        "amount": amount
                    }
                    data.append(new_entry)

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

# Добавляем новый маршрут для получения данных из data.json
@app.route('/data', methods=['GET'])
def get_data():
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
        return jsonify(data)  # Возвращаем данные в формате JSON
    except Exception as e:
        print(f"Ошибка при чтении data.json: {e}")
        return "Ошибка при чтении данных", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
