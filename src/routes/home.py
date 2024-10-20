from flask import Blueprint, render_template

from src.authentication import user_details, admin_login
from src.database.models.products import Category
from src.database.models.users import User
from src.main import inventory_controller

home_route = Blueprint('home', __name__)


@home_route.get('/')
@user_details
async def get_home(user: User):
    # project_list: list[dict[str, str]] = await projects.get_projects()
    #
    # image_filenames: list[str] = ['images/gallery/image_1.jpg', 'images/gallery/image_2.jpg',
    #                               'images/gallery/image_3.jpg', 'images/gallery/image_4.jpg']
    #
    # image_filename: str = random.choice(image_filenames)
    categories: Category = await inventory_controller.get_preloaded_categories()
    context = dict(user=user, categories=categories)
    return render_template('index.html', **context)


@home_route.get('/admin/login')
async def login():
    return render_template('admin/signin.html')


@home_route.get('/admin')
@admin_login
async def get_admin(user: User):
    context = dict(user=user)
    return render_template('admin/admin.html', **context)

