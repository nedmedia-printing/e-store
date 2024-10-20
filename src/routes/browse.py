from flask import Blueprint, render_template, abort
from src.authentication import user_details
from src.database.models.products import Category
from src.database.models.users import User
from src.main import inventory_controller

browse_route = Blueprint('browse', __name__)


@browse_route.get('/category/<string:seo_slug>')
@user_details
async def get_category(user: User, seo_slug: str):
    """
    Retrieve the category by slug and render the category products.

    :param user: User object
    :param seo_slug: SEO-friendly slug of the category
    :return: Rendered template with the category products
    """
    # Fetch the category details and products
    category: Category = await inventory_controller.get_category_by_slug(seo_slug)  # Assuming this method exists
    if not category:
        abort(404, description="Category not found")

    context = dict(category=category, user=user)
    return render_template('category_products.html', **context)


@browse_route.get('/categories')
@user_details
async def browse(user: User):
    """
    Retrieve the category by slug and render the category products.

    :param user: User object
    :param seo_slug: SEO-friendly slug of the category
    :return: Rendered template with the category products
    """
    # Fetch the category details and products
    categories = await inventory_controller.get_preloaded_categories()

    context = dict(categories=categories, user=user)
    return render_template('browse.html', **context)
