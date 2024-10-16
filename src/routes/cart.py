from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from src.authentication import user_details
from src.database.models.users import User
from src.main import inventory_controller
from src.database.models.products import Products  # Import your Products model
from src.database.models.cart import CartItem  # Import your CartItem model or create it

cart_route = Blueprint('cart', __name__)


# Endpoint to add a product to the cart
@cart_route.route('/add_to_cart/<string:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Check if the product exists
    product = inventory_controller.get_product_by_id(product_id)
    if not product:
        abort(404)  # If product not found, return 404

    # Create or retrieve the cart from the session
    cart = session.get('cart', {})
    if product_id in cart:
        cart[product_id]['quantity'] += 1  # Increase quantity if already in cart
    else:
        cart[product_id] = {'quantity': 1, 'name': product.name, 'price': product.sell_price}

    session['cart'] = cart  # Store cart in session
    return redirect(url_for('home.index'))  # Redirect to home or any page you prefer


# Endpoint to view the shopping cart
@cart_route.route('/cart', methods=['GET'])
def view_cart():
    cart = session.get('cart', {})
    return render_template('cart/view_cart.html', cart=cart)


# Endpoint to checkout
@cart_route.route('/checkout', methods=['GET'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('home.index'))  # Redirect if cart is empty

    return render_template('cart/checkout.html', cart=cart)


# Optional: Endpoint to remove an item from the cart
@cart_route.route('/remove_from_cart/<string:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]  # Remove the item from the cart
        session['cart'] = cart  # Update the session cart
    return redirect(url_for('cart.view_cart'))  # Redirect to the cart view


# Optional: Endpoint to clear the cart
@cart_route.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)  # Remove cart from session
    return redirect(url_for('home.index'))  # Redirect to home
