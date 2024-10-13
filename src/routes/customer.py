from flask import Blueprint, render_template, flash, redirect, url_for, request
from pydantic import ValidationError

from src.authentication import admin_login
from src.database.models.customer import Customer, CustomerUpdate
from src.database.models.users import User
from src.logger import init_logger
from src.main import customer_controller

customer_route = Blueprint('customer', __name__)
customer_logger = init_logger('customer_route')


@customer_route.get('/admin/customers')
@admin_login
async def get_customers(user: User):
    customers: list[Customer] = await customer_controller.get_customers()
    if not customers:
        flash(message="Note: This is just fake customer data for testing purposes", category="success")
        customers = [Customer.create_fake_customer() for _ in range(10)]
    context = {'user': user, 'customers': customers}
    return render_template('admin/customers.html', **context)


@customer_route.get('/admin/edit_customer/<string:customer_id>')
@admin_login
async def edit_customer(user: User, customer_id: str):
    customer = await customer_controller.get_customer(customer_id)
    if not customer:
        flash(message="Customer not found", category="danger")
        return redirect(url_for('customer.get_customers'))
    context = {'customer': customer}
    return render_template('admin/customers/edit_customer.html', **context)


@customer_route.post('/admin/edit_customer/<string:customer_id>')
@admin_login
async def save_customer_edits(user: User, customer_id: str):
    customer = await customer_controller.get_customer(customer_id=customer_id)
    if not customer:
        flash(message="Customer not found", category="danger")
        return redirect(url_for('customer.get_customers'))
    try:
        updated_data = CustomerUpdate(**request.form.to_dict())
        await customer_controller.update_customer(customer_id, updated_data.dict(exclude_unset=True))
        flash(message="Customer updated successfully", category="success")
    except ValidationError as e:
        customer_logger.error(f"Validation Error: {e}")
        flash(message=f"Failed to update customer: {e}", category="danger")
    except Exception as e:
        customer_logger.error(f"Error updating customer: {e}")
        flash(message="Failed to update customer", category="danger")

    return redirect(url_for('customer.get_customers'))


@customer_route.route('/admin/delete_customer/<string:customer_id>', methods=['POST'])
@admin_login
async def delete_customer(user: User, customer_id: str):
    if request.method == 'POST':
        confirmation = request.form.get('confirmation', 'no')
        if confirmation == 'yes':
            success = await customer_controller.delete_customer(customer_id)
            if success:
                flash(message="Customer deleted successfully", category="success")
            else:
                flash(message="Failed to delete customer", category="danger")
        else:
            flash(message="Customer deletion cancelled", category="info")
    return redirect(url_for('customer.get_customers'))
