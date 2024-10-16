from flask import Blueprint, render_template

from src.authentication import user_details
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
    categories = await inventory_controller.get_product_categories()
    context = dict(user=user, categories=categories)
    return render_template('index.html', **context)


@home_route.get('/admin/login')
async def login():
    return render_template('admin/signin.html')


@home_route.get('/admin')
async def get_admin():
    context = dict()
    return render_template('admin/admin.html', **context)

