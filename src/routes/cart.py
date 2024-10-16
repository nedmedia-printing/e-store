from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from src.database.models.products import Products  # Adjust the import as necessary
from src.main import inventory_controller
from src.database.models.cart import Cart, CartItem  # Adjust the import as necessary

cart_route = Blueprint('cart', __name__)


@cart_route.route('/cart', methods=['GET'])
def view_cart():
    """Render the shopping cart page."""
    cart_data = session.get('cart', {})
    cart = Cart(**cart_data)
    return render_template('cart/shopping_cart.html', cart=cart)


@cart_route.route('/add_to_cart/<string:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add a product to the shopping cart."""
    product = inventory_controller.get_product_by_id(product_id)
    if not product:
        abort(404)  # If product not found, return 404

    cart_data = session.get('cart', {})
    cart = Cart(**cart_data)
    cart.add_item(product_id=product.product_id, name=product.name, price=product.sell_price)

    session['cart'] = cart.dict()
    return redirect(url_for('cart.view_cart'))  # Redirect to the cart page


@cart_route.route('/remove_from_cart/<string:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Remove a product from the shopping cart."""
    cart_data = session.get('cart', {})
    cart = Cart(**cart_data)
    cart.remove_item(product_id)

    session['cart'] = cart.dict()
    return redirect(url_for('cart.view_cart'))  # Redirect to the cart page


@cart_route.route('/checkout', methods=['GET'])
def checkout():
    """Render the checkout page."""
    cart_data = session.get('cart', {})
    cart = Cart(**cart_data)
    return render_template('cart/checkout.html', cart=cart)
