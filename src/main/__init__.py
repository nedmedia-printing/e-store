from flask import Flask
from src.config import config_instance

from src.utils import template_folder, static_folder, upload_folder
from src.controller.encryptor import Encryptor
from src.controller.inventory_controller import InventoryController
from src.controller.auth import UserController
from src.main.bootstrap import bootstrap

encryptor = Encryptor()
inventory_controller = InventoryController()
user_controller = UserController()


def _add_blue_prints(app: Flask):
    """
        this function adds blueprints
    :param app:
    :return:
    """
    from src.routes.home import home_route
    from src.routes.inventory import inventory_route
    from src.routes.auth import auth_route

    app.register_blueprint(home_route)
    app.register_blueprint(inventory_route)
    app.register_blueprint(auth_route)


def create_app(config=config_instance()):
    app = Flask(__name__)
    app.template_folder = template_folder()
    app.static_folder = static_folder()
    app.config['UPLOAD_FOLDER'] = upload_folder()
    app.config.from_object(config)

    with app.app_context():
        _add_blue_prints(app=app)

        bootstrap()
        encryptor.init_app(app=app)
        inventory_controller.init_app(app=app)

    return app
