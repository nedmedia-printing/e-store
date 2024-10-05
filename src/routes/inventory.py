from flask import Blueprint, render_template

from src.authentication import admin_login
from src.database.models.users import User
from src.main import inventory_controller

inventory_route = Blueprint('inventory', __name__)


@inventory_route.get('/admin/inventory')
@admin_login
def get_inventory(user: User):
    pass


@inventory_route.get('/admin/products')
@admin_login
async def get_products(user: User):
    context = dict()
    return render_template('admin/products.html', **context)


@inventory_route.get('/admin/product/add')
@admin_login
async def add_product(user: User):
    categories = await inventory_controller.get_product_categories()
    context = dict(categories=categories, user=user)
    return render_template('admin/add_product.html', **context)


@inventory_route.post('/admin/products/create-product')
@admin_login
def create_product(user: User):
    pass
