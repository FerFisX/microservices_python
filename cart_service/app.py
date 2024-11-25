from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Conexión a la base de datos
DATABASE = 'cart.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL
            )
        ''')
        conn.commit()

@app.route('/cart', methods=['GET'])
def get_cart():
    try:
        with sqlite3.connect(DATABASE) as cart_conn, sqlite3.connect('../catalog_service/catalog.db') as catalog_conn:
            cart_cursor = cart_conn.cursor()
            catalog_cursor = catalog_conn.cursor()

            # Obtener ítems del carrito
            cart_cursor.execute('SELECT destination_id, quantity FROM cart')
            cart_items = cart_cursor.fetchall()

            # Obtener detalles completos desde el catálogo
            detailed_cart = []
            for destination_id, quantity in cart_items:
                catalog_cursor.execute('SELECT name, price FROM destinations WHERE id = ?', (destination_id,))
                destination = catalog_cursor.fetchone()
                if destination:
                    name, price = destination
                    detailed_cart.append({
                        'name': name,
                        'price': price,
                        'quantity': quantity,
                        'subtotal': price * quantity
                    })

        return jsonify(detailed_cart)
    except Exception as e:
        print(f"Error fetching cart items: {e}")
        return jsonify([]), 500


@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    destination_id, quantity = data['destination_id'], data['quantity']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cart (destination_id, quantity)
            VALUES (?, ?)
        ''', (destination_id, quantity))
        conn.commit()
    return jsonify({'message': 'Item added to cart'}), 201



@app.route('/cart/total', methods=['GET'])
def calculate_total():
    try:
        # Conecta a ambas bases de datos
        with sqlite3.connect('cart.db') as cart_conn, sqlite3.connect('../catalog_service/catalog.db') as catalog_conn:
            cart_cursor = cart_conn.cursor()
            catalog_cursor = catalog_conn.cursor()

            # Consulta los datos del carrito
            cart_cursor.execute('SELECT destination_id, quantity FROM cart')
            cart_items = cart_cursor.fetchall()

            total = 0
            for destination_id, quantity in cart_items:
                # Obtén el precio del destino desde catalog.db
                catalog_cursor.execute('SELECT price FROM destinations WHERE id = ?', (destination_id,))
                price = catalog_cursor.fetchone()
                if price:
                    total += price[0] * quantity  # Calcula el total

        return jsonify({'total': total})
    except Exception as e:
        print(f"Error calculating total: {e}")
        return jsonify({'total': 0}), 500

@app.route('/cart/clear', methods=['DELETE'])
def clear_cart():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cart')  # Vacía la tabla 'cart'
            conn.commit()
        return jsonify({'message': 'Cart cleared successfully'}), 200
    except Exception as e:
        print(f"Error clearing cart: {e}")
        return jsonify({'error': 'Failed to clear cart'}), 500



if __name__ == '__main__':
    init_db()
    app.run(port=5002)
