from sqlalchemy.orm import joinedload
from flask import Flask
import asyncio
from src.controller import Controllers, error_handler
from src.database.models.customer import Customer
from src.database.sql.customer import CustomerORM, OrderORM, PaymentORM


class CustomerController(Controllers):
    def __init__(self):
        super().__init__()
        self.__customers = []
        self.__customers_dict = {}

    def init_app(self, app: Flask):
        super().init_app(app=app)
        asyncio.run(self.preload_customers())

    @error_handler
    async def preload_customers(self):
        self.__customers = await self.get_all_customers()
        self.__customers_dict = {customer.uid: customer for customer in self.__customers}

    async def get_all_customers(self) -> list[Customer]:
        """retrieve a complete list of customers from the database"""
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
    async def get_customers(self) -> list[Customer]:
        """ Retrieves all customers from the database with joined records. """
        return self.__customers

    @error_handler
    async def get_customer(self, customer_id: str) -> Customer | None:
        """ Retrieves a customer by ID from the preloaded customers. """
        return self.__customers_dict.get(customer_id)

    @error_handler
    async def add_customer(self, customer: Customer) -> Customer:
        """ Adds a new customer to the database. """
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
        await self.preload_customers()  # Update preloaded customers after adding a new one
        return customer

    @error_handler
    async def update_customer(self, customer_id: str, updated_data: dict) -> bool:
        """ Updates an existing customer's details. """
        with self.get_session() as session:
            customer_orm: CustomerORM = session.query(CustomerORM).filter_by(uid=customer_id).first()
            if not customer_orm:
                return False
            for key, value in updated_data.items():
                setattr(customer_orm, key, value)

        await self.preload_customers()  # Update preloaded customers after updating
        return True

    @error_handler
    async def delete_customer(self, customer_id: str) -> bool:
        """ Deletes a customer by ID along with all linked order records. """
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

        await self.preload_customers()  # Update preloaded customers after deletion
        return True
