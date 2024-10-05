from flask import Blueprint, render_template, request, redirect, url_for, flash
from pydantic import ValidationError
from src.authentication import admin_login
from src.database.models.products import Products
from src.database.models.users import User
from src.logger import init_logger
from src.main import inventory_controller

inventory_route = Blueprint('inventory', __name__)
inventory_logger = init_logger('inventory_route')


@inventory_route.get('/admin/inventory')
@admin_login
async def get_inventory(user: User):
    pass


@inventory_route.get('/admin/products')
@admin_login
async def get_products(user: User):
    context = dict(user=user)
    return render_template('admin/inventory/products.html', **context)


@inventory_route.get('/admin/product/add')
@admin_login
async def add_product(user: User):
    categories = await inventory_controller.get_product_categories()
    context = dict(categories=categories, user=user)
    return render_template('admin/inventory/add_product.html', **context)


@inventory_route.get('/admin/inventory/product/<string:product_id>')
@admin_login
async def get_product(user: User, product_id: str):
    """
    :param user:
    :param product_id:
    :return:
    """
    product: Products = await inventory_controller.get_product(product_id=product_id)
    context = dict(user=user)
    if not isinstance(product, Products):
        flash(message="Product Not Found", category="danger")
    context.update(product=product)
    return render_template('admin/inventory/product_detail.html', **context)


@inventory_route.post('/admin/products/create-product')
@admin_login
async def create_product(user: User):
    try:
        product = Products(**request.form)

    except ValidationError as e:
        inventory_logger.error(str(e))
        flash(message="please enter all required fields", category='danger')
        return redirect(url_for('inventory.add_product'))

    new_product: Products = inventory_controller.add_product(product=product)
    inventory_logger.info(f"Created New Product: {new_product}")
    return redirect(url_for('inventory.get_product', porduct_id=new_product.product_id))
