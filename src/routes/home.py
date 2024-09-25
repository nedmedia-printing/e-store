import random
from pydantic import ValidationError
from flask import Blueprint, render_template, request

home_route = Blueprint('home', __name__)


@home_route.get('/')
async def get_home():
    # project_list: list[dict[str, str]] = await projects.get_projects()
    #
    # image_filenames: list[str] = ['images/gallery/image_1.jpg', 'images/gallery/image_2.jpg',
    #                               'images/gallery/image_3.jpg', 'images/gallery/image_4.jpg']
    #
    # image_filename: str = random.choice(image_filenames)
    context = dict()

    return render_template('index.html', **context)


@home_route.get('/admin/login')
async def login():
    return render_template('auth.html')


@home_route.get('/admin')
async def admin():
    project_list: list[dict[str, str]] = await projects.get_projects()
    context: dict[str, list[dict[str, str]]] = dict(projects_list=project_list)
    return render_template('admin/admin.html', **context)
