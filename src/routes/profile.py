from flask import Blueprint, render_template

from src.authentication import admin_login
from src.database.models.customer import Order
from src.database.models.profile import Profile
from src.database.models.users import User
from src.logger import init_logger
from src.main import orders_controller

profile_route = Blueprint('profile', __name__)
profile_logger = init_logger('order_route')



@profile_route.get('/profile')
@login_required
async def get_profile(user: User):
    """

    :param user:
    :return:
    """
    profile: Profile = await profile_controller.get_profile(uid=user.uid)
    context = dict(user=user, profile=profile)
    return render_template('profile/profile.html')