from flask import Blueprint, render_template, request, redirect, url_for, session, abort, flash

from src.authentication import login_required
from src.database.models.products import Products  # Adjust the import as necessary
from src.database.models.users import User
from src.main import inventory_controller, cart_controller
from src.database.models.cart import Cart, CartItem  # Adjust the import as necessary

cart_route = Blueprint('cart', __name__)


@cart_route.route('/cart', methods=['GET'])
@login_required
async def view_cart(user: User):
    """Render the shopping cart page."""
    cart: Cart = await cart_controller.get_outstanding_customer_cart(uid=user.uid)
    context = dict(user=user, cart=cart)
    return render_template('cart/shopping_cart.html', **context)


@cart_route.route('/add_to_cart/<string:product_id>', methods=['POST', 'GET'])
@login_required
async def add_to_cart(user: User, product_id: str):
    """Add a product to the shopping cart."""
    quantity = request.form.get('quantity', 1)

    product: Products = await inventory_controller.get_product(product_id=product_id)

    if not product:
        flash(message="There was a Problem with this product please try again later", category="danger")
        return redirect(url_for('cart.view_cart'))  # Redirect to the cart page

    if product.inventory_count <= 0:
        flash(message="Unfortunately we are out of stock", category="danger")
        return redirect(url_for('cart.view_cart'))  # Redirect to the cart page

    cart: Cart = await cart_controller.get_outstanding_customer_cart(uid=user.uid)
    if not cart:
        new_cart = Cart(uid=user.uid)
        cart = await cart_controller.create_new_cart(new_cart=new_cart)
    cart_item: CartItem = cart.add_item(product_id=product_id, quantity=quantity)
    cart_item_added = await cart_controller.add_cart_item(cart_item=cart_item)
    if cart_item_added:
        flash(message="Cart Item Created", category="success")
    else:
        flash(message="Unable to add cart item", category="danger")

    return redirect(url_for('cart.view_cart'))  # Redirect to the cart page


@cart_route.route('/remove_from_cart/<string:product_id>', methods=['POST'])
async def remove_from_cart(product_id):
    """Remove a product from the shopping cart."""
    cart_data = session.get('cart', {})
    cart = Cart(**cart_data)
    cart.remove_item(product_id)

    session['cart'] = cart.dict()
    return redirect(url_for('cart.view_cart'))  # Redirect to the cart page


@cart_route.route('/checkout', methods=['GET'])
async def checkout():
    """Render the checkout page."""
    cart_data = session.get('cart', {})
    cart = Cart(**cart_data)
    return render_template('cart/checkout.html', cart=cart)
