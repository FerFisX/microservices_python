from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Conexión a la base de datos
DATABASE = 'catalog.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS destinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        conn.commit()

@app.route('/destinations', methods=['GET'])
def get_destinations():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM destinations')
        destinations = cursor.fetchall()
    return jsonify(destinations)

@app.route('/destinations', methods=['POST'])
def add_destination():
    data = request.get_json()
    name, description, price = data['name'], data['description'], data['price']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO destinations (name, description, price)
            VALUES (?, ?, ?)
        ''', (name, description, price))
        conn.commit()
    return jsonify({'message': 'Destination added successfully'}), 201

if __name__ == '__main__':
    init_db()
    app.run(port=5001)
