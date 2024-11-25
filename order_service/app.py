from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Conexión a la base de datos
DATABASE = 'order.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    total = data['total']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (total, status)
            VALUES (?, ?)
        ''', (total, 'Pending'))
        conn.commit()
        order_id = cursor.lastrowid
    return jsonify({'order_id': order_id, 'status': 'Pending'}), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
    if order:
        return jsonify({'id': order[0], 'total': order[1], 'status': order[2]})
    else:
        return jsonify({'error': 'Order not found'}), 404
    
@app.route('/orders/<int:order_id>/details', methods=['GET'])
def get_order_details(order_id):
    try:
        with sqlite3.connect('../cart_service/cart.db') as cart_conn, sqlite3.connect('../catalog_service/catalog.db') as catalog_conn:
            cart_cursor = cart_conn.cursor()
            catalog_cursor = catalog_conn.cursor()

            # Obtén todos los ítems del carrito
            cart_cursor.execute('SELECT destination_id, quantity FROM cart')
            cart_items = cart_cursor.fetchall()

            order_details = []
            for destination_id, quantity in cart_items:
                # Consulta el destino en catalog.db
                catalog_cursor.execute('SELECT name, price FROM destinations WHERE id = ?', (destination_id,))
                destination = catalog_cursor.fetchone()
                if destination:
                    name, price = destination
                    order_details.append({
                        'name': name,
                        'price': price,
                        'quantity': quantity,
                        'total': price * quantity
                    })

        # Calcula el total general
        total = sum(item['total'] for item in order_details)
        return jsonify({
            'order_id': order_id,
            'status': 'Pending',
            'total': total,
            'details': order_details
        })
    except Exception as e:
        print(f"Error fetching order details: {e}")
        return jsonify({'error': 'Failed to fetch order details'}), 500

    

if __name__ == '__main__':
    init_db()
    app.run(port=5003)
