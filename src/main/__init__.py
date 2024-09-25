from flask import Flask
from src.config import config_instance

from src.utils import template_folder, static_folder, upload_folder
from src.controllers.projects import ProjectController

projects = ProjectController()


def bootstrap():
    from src.database.projects import ProjectsORM
    ProjectsORM.create_if_not_table()
    from src.database.users import UsersORM
    UsersORM.create_if_not_table()


def create_app(config=config_instance()):
    app = Flask(__name__)
    app.template_folder = template_folder()
    app.static_folder = static_folder()
    app.config['UPLOAD_FOLDER'] = upload_folder()
    app.config.from_object(config)

    with app.app_context():
        from src.routes.home import home_route
        app.register_blueprint(home_route)
        bootstrap()
    return app
