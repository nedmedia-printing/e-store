from flask import Blueprint, render_template, flash

from src.authentication import admin_login
from src.database.models.customer import Customer
from src.database.models.users import User
from src.logger import init_logger
from src.main import customer_controller

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
        customers = [Customer.create_fake_customer() for _ in range(10)]

    # Prepare the context for the template
    context = {
        'user': user,
        'customers': customers
    }
    return render_template('admin/customers.html', **context)

