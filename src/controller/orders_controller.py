from sqlalchemy.orm import joinedload
from flask import Flask
import asyncio
from src.controller import Controllers, error_handler
from src.database.models.customer import Order, OrderStatus
from src.database.sql.customer import OrderORM, CustomerORM, PaymentORM, OrderItemsORM


class OrdersController(Controllers):
    def __init__(self):
        super().__init__()
        self.__orders = []
        self.__orders_dict = {}

    def init_app(self, app: Flask):
        super().init_app(app=app)
        asyncio.run(self.preload_orders())

    @error_handler
    async def preload_orders(self):
        self.__orders = await self.get_all_orders()
        self.__orders_dict = {order.order_id: order for order in self.__orders}

    @error_handler
    async def get_all_orders(self) -> list[Order]:
        """retrieve complete list of orders from database"""
        with self.get_session() as session:
            order_orm_list = (
                session.query(OrderORM)
                .options(
                    joinedload(OrderORM.customer),
                    joinedload(OrderORM.payments),
                    joinedload(OrderORM.order_items)
                )
                .all()
            )
            return [Order(**order_orm.to_dict(include_relationships=True)) for order_orm in order_orm_list]

    @error_handler
    async def get_orders(self) -> list[Order]:
        """ Retrieves all orders from the database with joined records. """
        return self.__orders

    @error_handler
    async def get_order(self, order_id: str) -> Order | None:
        """ Retrieves an order by ID from the preloaded orders. """
        return self.__orders_dict.get(order_id)

    @error_handler
    async def add_order(self, order: Order) -> Order:
        """ Adds a new order to the database. """
        with self.get_session() as session:
            session.add(OrderORM(
                order_id=order.order_id,
                customer_id=order.customer_id,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
                updated_at=order.updated_at
            ))
            for payment in order.payments:
                session.add(PaymentORM(
                    payment_id=payment.payment_id,
                    order_id=payment.order_id,
                    amount=payment.amount,
                    payment_date=payment.payment_date
                ))
            for item in order.order_items:
                session.add(OrderItemsORM(
                    item_id=item.item_id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity
                ))

        await self.preload_orders()  # Update preloaded orders after adding a new one
        return order

    @error_handler
    async def get_refunds(self) -> list[Order]:
        """ Retrieves all refunded orders from the database. """
        with self.get_session() as session:
            order_orm_list = (
                session.query(OrderORM)
                .outerjoin(CustomerORM, OrderORM.customer_id == CustomerORM.uid)
                .outerjoin(PaymentORM, OrderORM.order_id == PaymentORM.order_id)
            ).filter_by(status=OrderStatus.RETURNED.value).all()
            return [Order(**order_orm.to_dict(include_relationships=True)) for order_orm in order_orm_list]

    @error_handler
    async def delete_order(self, order_id: str) -> bool:
        """ Deletes an order by ID along with all linked payments and items. """
        with self.get_session() as session:
            order_orm = session.query(OrderORM).filter_by(order_id=order_id).first()
            if not order_orm:
                return False
            # Delete all related payments and items
            for payment in order_orm.payments:
                session.delete(payment)
            for item in order_orm.order_items:
                session.delete(item)
            session.delete(order_orm)

        await self.preload_orders()  # Update preloaded orders after deletion
        return True
