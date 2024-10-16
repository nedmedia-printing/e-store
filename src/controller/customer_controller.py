from sqlalchemy.orm import joinedload

from src.controller import Controllers, error_handler
from src.database.models.customer import Customer
from src.database.sql.customer import CustomerORM, OrderORM, PaymentORM


class CustomerController(Controllers):
    def __init__(self):
        super().__init__()

    @error_handler
    async def add_customer(self, customer: Customer) -> Customer:
        """
        Adds a new customer to the database.
        :param customer: Customer instance
        :return: None
        """
        with self.get_session() as session:
            session.add(CustomerORM(
                uid=customer.uid,
                name=customer.name,
                order_count=customer.order_count,
                total_spent=customer.total_spent,
                city=customer.city,
                last_seen=customer.last_seen,
                last_order_date=customer.last_order_date,
                notes=customer.notes
            ))
            return customer

    @error_handler
    async def get_customers(self) -> list[Customer]:
        """
        Retrieves all customers from the database with joined records.
        :return: List of Customer instances
        """
        with self.get_session() as session:
            customers_orm_list = (
                session.query(CustomerORM)
                .options(
                    joinedload(CustomerORM.orders)
                    .joinedload(OrderORM.payments),
                    joinedload(CustomerORM.orders)
                    .joinedload(OrderORM.order_items)
                )
                .all()
            )

            return [Customer(**customer_orm.to_dict(include_relationships=True)) for customer_orm in customers_orm_list]

    @error_handler
    async def get_customer(self, customer_id: str) -> Customer | None:
        """
        Retrieves a customer by ID along with their orders.
        :param customer_id: Customer ID
        :return: Customer instance or None if not found
        """
        with self.get_session() as session:
            self.logger.info(f"Inside Get Customer: {customer_id}")
            customer_orm = (
                session.query(CustomerORM)
                .options(
                    joinedload(CustomerORM.orders)
                    .joinedload(OrderORM.payments),
                    joinedload(CustomerORM.orders)
                    .joinedload(OrderORM.order_items)
                )  # Ensures orders are loaded
                .filter_by(uid=customer_id)
                .first()
            )
            if not customer_orm:
                return None
            self.logger.info(f"Customer Found: {customer_orm}")
            return Customer(**customer_orm.to_dict(include_relationships=True))

    @error_handler
    async def update_customer(self, customer_id: str, updated_data: dict) -> bool:
        """
        Updates an existing customer's details.
        :param customer_id: Customer ID
        :param updated_data: Dictionary of updated customer data
        :return: True if update is successful, False otherwise
        """
        with self.get_session() as session:
            customer_orm: CustomerORM = session.query(CustomerORM).filter_by(uid=customer_id).first()
            if not customer_orm:
                return False
            for key, value in updated_data.items():
                setattr(customer_orm, key, value)
            return True

    @error_handler
    async def delete_customer(self, customer_id: str) -> bool:
        """
        Deletes a customer by ID along with all linked order records.
        :param customer_id: Customer ID
        :return: True if deletion is successful, False otherwise
        """
        with self.get_session() as session:
            customer_orm = session.query(CustomerORM).filter_by(uid=customer_id).first()
            if not customer_orm:
                return False

            # Delete all related orders
            for order in customer_orm.orders:
                # Delete all related payments for each order
                for payment in order.payments:
                    session.delete(payment)
                # Delete all related order items for each order
                for item in order.order_items:
                    session.delete(item)
                session.delete(order)

            # Finally, delete the customer
            session.delete(customer_orm)
            return True
