from flask import Blueprint, render_template, request, redirect, url_for, flash
from pydantic import ValidationError
from src.authentication import admin_login
from src.database.models.products import Products, Category
from src.database.models.users import User
from src.logger import init_logger
from src.main import inventory_controller
from src.utils import products_upload_folder, save_files_to_folder

inventory_route = Blueprint('inventory', __name__)
inventory_logger = init_logger('inventory_route')


@inventory_route.get('/admin/inventory')
@admin_login
async def get_inventory(user: User):
    pass


@inventory_route.get('/admin/categories')
@admin_login
async def get_categories(user: User):
    """

    :param user:
    :return:
    """
    categories: list[Category] = await inventory_controller.get_product_categories()
    updated_category_list = []
    for category in categories:
        category.update_category_images()
        updated_category_list.append(category)

    context = dict(user=user, categories=updated_category_list)
    return render_template('admin/inventory/categories.html', **context)


@inventory_route.post('/admin/category/add')
@admin_login
async def add_category(user: User):
    """

    :param user:
    :return:
    """
    try:
        category = Category(**request.form, inventory_entries=[], products=[])
        display_image = request.files.getlist('display_image')
    except ValidationError as e:
        inventory_logger.error(str(e))
        return redirect(url_for('inventory.get_categories'))

    new_category: Category = await inventory_controller.add_category(category=category)
    if display_image:
        category_image_upload_folder_path = products_upload_folder(category_id=category.category_id, product_id=None)

        save_files_to_folder(folder_path=category_image_upload_folder_path, file_list=display_image)

    if not isinstance(category, Category):
        flash(message="Unable to create new category please try again later", category="danger")

    return redirect(url_for('inventory.get_categories'))


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
    context = dict(user=user)
    product: Products = await inventory_controller.get_product(product_id=product_id)
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
