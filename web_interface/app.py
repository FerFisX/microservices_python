from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# URLs de microservicios
CATALOG_SERVICE = 'http://localhost:5001'
CART_SERVICE = 'http://localhost:5002'
ORDER_SERVICE = 'http://localhost:5003'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    response = requests.get(f'{CATALOG_SERVICE}/destinations')
    destinations = response.json()
    return render_template('catalog.html', destinations=destinations)

@app.route('/cart')
def cart():
    try:
        response = requests.get(f'{CART_SERVICE}/cart')
        response.raise_for_status()
        cart_items = response.json()

        # Calcula el total
        total = sum(item['subtotal'] for item in cart_items)

        return render_template('cart.html', cart_items=cart_items, total=total)
    except Exception as e:
        print(f"Error fetching cart: {e}")
        return render_template('cart.html', cart_items=[], total=0)




@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    destination_id = request.form['destination_id']
    quantity = request.form['quantity']
    requests.post(f'{CART_SERVICE}/cart', json={'destination_id': destination_id, 'quantity': quantity})
    return redirect(url_for('cart'))

@app.route('/order', methods=['POST'])
def create_order():
    try:
        total_response = requests.get(f'{CART_SERVICE}/cart/total')
        total_response.raise_for_status()
        total = total_response.json().get('total', 0)

        if total > 0:
            # Crea la orden
            order_response = requests.post(f'{ORDER_SERVICE}/orders', json={'total': total})
            order_response.raise_for_status()
            order = order_response.json()

            # Obtén los detalles de la orden
            order_id = order.get('order_id')
            details_response = requests.get(f'{ORDER_SERVICE}/orders/{order_id}/details')
            details_response.raise_for_status()
            order_details = details_response.json()

            # Vacía el carrito
            clear_response = requests.delete(f'{CART_SERVICE}/cart/clear')
            clear_response.raise_for_status()

            return render_template('order.html', order=order_details)
    except Exception as e:
        print(f"Error creating order: {e}")
        return render_template('order.html', order={'order_id': 'N/A', 'total': 0, 'status': 'Error'})



if __name__ == '__main__':
    app.run(port=5000)
