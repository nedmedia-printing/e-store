from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.authentication import admin_login, login_required
from src.database.models.customer import Order
from src.database.models.profile import Profile
from src.database.models.users import User
from src.logger import init_logger
from src.main import orders_controller, profile_controller

profile_route = Blueprint('profile', __name__)
profile_logger = init_logger('profile_route')


@profile_route.get('/profile')
@login_required
async def get_profile(user: User):
    """ :param user: :return: """
    profile: Profile = await profile_controller.get_profile(uid=user.uid)
    context = dict(user=user, profile=profile)
    return render_template('profile/profile.html', **context)


@profile_route.post('/profile/update')
@login_required
async def update_profile(user: User):
    """ :param user: :return: """
    updated_data = request.form.to_dict()
    success = await profile_controller.update_profile(user.uid, updated_data)
    if success:
        flash('Profile updated successfully', 'success')
    else:
        flash('Failed to update profile', 'danger')
    return redirect(url_for('profile.get_profile'))


@profile_route.post('/profile/delete')
@login_required
async def delete_profile(user: User):
    """ :param user: :return: """
    success = await profile_controller.delete_profile(user.uid)
    if success:
        flash('Profile deleted successfully', 'success')
        return redirect(url_for('auth.logout'))
    else:
        flash('Failed to delete profile', 'danger')
    return redirect(url_for('profile.get_profile'))


@profile_route.post('/profile/add')
@admin_login
async def add_profile():
    """ :return: """
    profile_data = request.form.to_dict()
    profile = Profile(**profile_data)
    added_profile = await profile_controller.add_profile(profile)
    if added_profile:
        flash('Profile added successfully', 'success')
    else:
        flash('Failed to add profile', 'danger')
    return redirect(url_for('profile.get_profile'))
