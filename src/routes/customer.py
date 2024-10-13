from flask import Blueprint, render_template, request, redirect, url_for, flash
from pydantic import ValidationError
from src.authentication import admin_login
from src.database.models.customer import Customer
from src.database.models.products import Products, Category, Inventory, InventoryActionTypes
from src.database.models.users import User
from src.logger import init_logger
from src.main import inventory_controller, customer_controller
from src.utils import products_upload_folder, save_files_to_folder

customer_route = Blueprint('customer', __name__)
customer_logger = init_logger('customer_route')


@customer_route.get('/admin/customers')
@admin_login
async def get_customers(user: User):
    """

    :param user:d 
    :return:
    """
    customers: list[Customer] = await customer_controller.get_customers()
    if not customers:
        flash(message="Note This is just fake customer data for testing purposes", category="success")
        for i in range(10):
            customers.append(Customer.create_fake_customer())

    context = dict(user=user, customers=customers)
    return render_template('admin/customers.html', **context)

