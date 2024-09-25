import random
from pydantic import ValidationError
from flask import Blueprint, render_template, request

from src.database.models import CreateProject
from src.main import projects

home_route = Blueprint('home', __name__)


@home_route.get('/')
async def get_home():
    project_list: list[dict[str, str]] = await projects.get_projects()

    image_filenames: list[str] = ['images/gallery/image_1.jpg', 'images/gallery/image_2.jpg',
                                  'images/gallery/image_3.jpg', 'images/gallery/image_4.jpg']

    image_filename: str = random.choice(image_filenames)
    context = dict(image_filenames=image_filenames, image_filename=image_filename, projects_list=project_list)

    return render_template('index.html', **context)


@home_route.get('/admin/login')
async def login():
    return render_template('auth.html')


@home_route.get('/admin')
async def admin():
    project_list: list[dict[str, str]] = await projects.get_projects()
    context: dict[str, list[dict[str, str]]] = dict(projects_list=project_list)
    return render_template('admin/admin.html', **context)


@home_route.post('/admin/project')
async def add_project():
    try:
        uploaded_file = request.files['image']
        if not uploaded_file:
            return f"Validation error: Please upload image file for your project"

        project_data = CreateProject(project_name=request.form.get('project_name'),
                                     introduction=request.form.get('introduction'),
                                     description=request.form.get('description'),
                                     filename=uploaded_file.filename)

        image_path: str = await projects.add_project(project_data=project_data)

        if image_path:
            uploaded_file.save(image_path)
            project_list: list[dict[str, str]] = await projects.get_projects()
            context: dict[str, list[dict[str, str]]] = dict(projects_list=project_list)
            return render_template('admin/admin.html', **context)

    except ValidationError as e:
        return f"Validation error: {str(e)}"

    project_list: list[dict[str, str]] = await projects.get_projects()
    context: dict[str, list[dict[str, str]]] = dict(projects_list=project_list)
    return render_template('admin/admin.html', **context)


@home_route.get('/admin/project/<string:project_id>')
async def delete_project(project_id: str):
    """
        **delete_project**
            
    :param project_id:
    :return:
    """
    is_deleted = await projects.delete_project(_id=project_id)
    if not is_deleted:
        return "Could not Delete Project: Project may already be deleted"

    project_list: list[dict[str, str]] = await projects.get_projects()
    context: dict[str, list[dict[str, str]]] = dict(projects_list=project_list)
    return render_template('admin/admin.html', **context)
