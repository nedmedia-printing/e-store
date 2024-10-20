from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pydantic import ValidationError

from src.authentication import login_required
from src.database.models.cart import Cart, CartItem  # Adjust the import as necessary
from src.database.models.products import Products  # Adjust the import as necessary
from src.database.models.users import User
from src.logger import init_logger
from src.main import inventory_controller, cart_controller

cart_route = Blueprint('cart', __name__)
cart_logger = init_logger('Cart Items')


@cart_route.route('/cart', methods=['GET'])
@login_required
async def view_cart(user: User):
    """Render the shopping cart page.
    """
    cart: Cart = await cart_controller.get_outstanding_customer_cart(uid=user.uid)
    context = dict(user=user, cart=cart)
    cart_logger.info(f'Cart Retrieved: {cart}')
    return render_template('cart/shopping_cart.html', **context)


@cart_route.route('/add_to_cart/<string:product_id>', methods=['POST', 'GET'])
@login_required
async def add_to_cart(user: User, product_id: str):
    """Add a product to the shopping cart."""
    quantity = request.form.get('quantity', 1)
    cart_logger.info(f"Cart Quantity: {quantity}")

    product: Products = await inventory_controller.get_product(product_id=product_id)
    cart_logger.info(f"Product: {product}")
    if not product:
        flash(message="There was a Problem with this product please try again later", category="danger")
        return redirect(url_for('cart.view_cart'))  # Redirect to the cart page

    if product.inventory_count <= 0:
        cart_logger.info(f"Product Not in Inventory")
        flash(message="Unfortunately we are out of stock", category="danger")
        return redirect(url_for('cart.view_cart'))  # Redirect to the cart page

    cart: Cart = await cart_controller.get_outstanding_customer_cart(uid=user.uid)
    cart_logger.info(f"Created Customer Cart: {cart}")

    if not cart:
        new_cart = Cart(uid=user.uid)
        cart: Cart = await cart_controller.create_new_cart(cart=new_cart)
    try:
        cart_item: CartItem = cart.add_item(product=product, quantity=quantity)
    except ValidationError as e:
        cart_logger.info(str(e))
        flash(message="Unable to add item to cart, please try again later", category="danger")
        return redirect(url_for('cart.view_cart'))

    cart_item_added = await cart_controller.add_cart_item(cart_item=cart_item)
    cart_logger.info(f"Created New Cart Item: {cart_item}")
    if cart_item_added:
        flash(message="Cart Item Created", category="success")
    else:
        flash(message="Unable to add cart item", category="danger")

    return redirect(url_for('cart.view_cart'))  # Redirect to the cart page


@cart_route.route('/update-cart/<string:product_id>', methods=['POST'])
@login_required
async def update_quantity(user: User, product_id: str):
    """

    :param user:
    :param product_id:
    :return:
    """
    pass


@cart_route.route('/remove_from_cart/<string:item_id>', methods=['POST'])
@login_required
async def remove_from_cart(user: User, item_id: str):
    """Remove a product from the shopping cart."""
    cart_removed = await cart_controller.remove_cart_item(item_id=item_id)
    if cart_removed:
        flash(message="you have successfully cleared your cart", category="success")
    else:
        flash(message="Unable to removed cart items, please try again later", category="danger")
    # context = dict(user=user, cart=cart)
    return redirect(url_for('cart.view_cart'))  # Redirect to the cart page


@cart_route.route('/checkout', methods=['GET'])
async def checkout():
    """Render the checkout page."""
    cart_data = session.get('cart', {})
    cart = Cart(**cart_data)
    return render_template('cart/checkout.html', cart=cart)
