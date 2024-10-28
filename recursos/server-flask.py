import json
from flask import Flask, request, jsonify
import os


app = Flask(__name__)

data_file_path = os.path.join(os.path.dirname(__file__), 'data.txt')

def initialize_file():
    if not os.path.exists(data_file_path):
        with open(data_file_path, 'w') as f:
            f.write('[]')

def load_records():
    with open(data_file_path, 'r') as f:
        data = f.read()
        return json.loads(data) if data else []

def save_records(records):
    with open(data_file_path, 'w') as f:
        f.write(json.dumps(records, indent=2))

@app.route('/', methods=['GET'])
def query_records():
    name = request.args.get('name')
    initialize_file()
    records = load_records()
    for record in records:
        if record.get('name') == name:
            return jsonify(record)
    return jsonify({'error': 'data not found'})

@app.route('/', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    initialize_file()
    records = load_records()
    records.append(record)
    save_records(records)
    return jsonify(record)

@app.route('/', methods=['PUT'])
def update_record():
    record = json.loads(request.data)
    initialize_file()
    records = load_records()
    updated = False
    for r in records:
        if r.get('name') == record.get('name'):
            r.update(record)  # Atualiza todos os campos do registro
            updated = True
    if not updated:
        return jsonify({'error': 'record not found'}), 404
    save_records(records)
    return jsonify(record)
    
@app.route('/', methods=['DELETE'])
def delete_record():
    record = json.loads(request.data)
    initialize_file()
    records = load_records()
    records = [r for r in records if r.get('name') != record.get('name')]
    save_records(records)
    return jsonify(record)

@app.route('/', methods=['PATCH'])
def patch_record():
    record = json.loads(request.data)
    initialize_file()
    records = load_records()
    updated = False
    for r in records:
        if r.get('name') == record.get('name'):
            r.update({k: v for k, v in record.items() if k in r})
            updated = True
    if not updated:
        return jsonify({'error': 'record not found'}), 404
    save_records(records)
    return jsonify(record)

@app.route('/', methods=['OPTIONS'])
def options_record():
    return jsonify({"message": "OPTIONS request received"})

if __name__ == '__main__':
    app.run(debug=True)
