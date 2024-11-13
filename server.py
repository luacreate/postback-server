import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = './data'
DATA_FILE = os.path.join(DATA_DIR, 'data.json')

# Создание папки и файла, если их нет
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump([], file)

def read_data():
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def write_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/postback-handler', methods=['GET'])
def postback_handler():
    user_id = request.args.get('user_id')
    text = request.args.get('text')

    data = read_data()
    if user_id:
        if not any(entry['user_id'] == user_id for entry in data):
            data.append({"user_id": user_id, "amount": 0})
            write_data(data)
            return "Регистрация сохранена", 200
    if text:
        user_id, amount = text.split(':')
        amount = float(amount)
        for entry in data:
            if entry['user_id'] == user_id:
                entry['amount'] += amount
                break
        else:
            data.append({"user_id": user_id, "amount": amount})
        write_data(data)
        return "Депозит сохранён", 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(read_data()), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
