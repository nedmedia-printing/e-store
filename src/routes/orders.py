from flask import Blueprint, render_template

from src.authentication import admin_login
from src.database.models.customer import Order
from src.database.models.users import User
from src.logger import init_logger
from src.main import orders_controller

order_route = Blueprint('order', __name__)
order_logger = init_logger('order_route')


@order_route.get('/admin/orders')
@admin_login
async def get_orders(user: User):
    """

    :param user:
    :return:
    """
    orders: list[Order] = await orders_controller.get_orders()
    context = {'user': user, 'orders': orders}
    return render_template('admin/orders/orders.html', **context)
