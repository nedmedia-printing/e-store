from flask import Flask
from src.config import config_instance

from src.emailer import SendMail
from src.cache.caching import Caching
from src.controller.encryptor import Encryptor
from src.firewall import Firewall

system_cache = Caching()
send_mail = SendMail()
encryptor = Encryptor()

from src.utils import template_folder, static_folder, upload_folder, format_currency
from src.controller.auth import UserController
from src.controller.inventory_controller import InventoryController
from src.controller.orders_controller import OrdersController
from src.controller.customer_controller import CustomerController
from src.controller.cart_controller import CartController

from src.main.bootstrap import bootstrap

user_controller = UserController()
inventory_controller = InventoryController()
orders_controller = OrdersController()
customer_controller = CustomerController()
cart_controller = CartController()
firewall = Firewall()


def _add_blue_prints(app: Flask):
    """
        this function adds blueprints
    :param app:
    :return:
    """
    from src.routes.home import home_route
    from src.routes.inventory import inventory_route
    from src.routes.auth import auth_route
    from src.routes.documents import images_route
    from src.routes.customer import customer_route
    from src.routes.orders import order_route
    from src.routes.browse import browse_route
    from src.routes.cart import cart_route

    app.register_blueprint(home_route)
    app.register_blueprint(inventory_route)
    app.register_blueprint(auth_route)
    app.register_blueprint(images_route)
    app.register_blueprint(customer_route)
    app.register_blueprint(order_route)
    app.register_blueprint(browse_route)
    app.register_blueprint(cart_route)


def _add_filters(app: Flask):
    app.jinja_env.filters['currency'] = format_currency


def create_app(config=config_instance()):
    app = Flask(__name__)
    app.template_folder = template_folder()
    app.static_folder = static_folder()
    app.config['UPLOAD_FOLDER'] = upload_folder()
    # same config as in Nginx
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
    app.config.from_object(config)

    with app.app_context():
        firewall.init_app(app=app)
        _add_blue_prints(app=app)
        _add_filters(app=app)

        bootstrap()
        encryptor.init_app(app=app)

        user_controller.init_app(app=app)
        inventory_controller.init_app(app=app)
        customer_controller.init_app(app=app)
        orders_controller.init_app(app=app)
        cart_controller.init_app(app=app)

    return app
