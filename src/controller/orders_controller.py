from src.controller import Controllers, error_handler
from src.database.models.customer import Order, OrderStatus
from src.database.sql.customer import OrderORM, CustomerORM, PaymentORM


class OrdersController(Controllers):
    def __init__(self):
        super().__init__()

    @error_handler
    async def get_orders(self) -> list[Order]:
        """
        Retrieves all orders from the database with joined records.
        :return: List of Order instances
        """
        with self.get_session() as session:
            order_orm_list = (
                session.query(OrderORM)
                .outerjoin(CustomerORM, OrderORM.customer_id == CustomerORM.uid)
                .outerjoin(PaymentORM, OrderORM.order_id == PaymentORM.order_id)
                .all()
            )
            return [Order(**order_orm.to_dict(include_relationships=True)) for order_orm in order_orm_list]

    @error_handler
    async def get_order(self, order_id: str) -> Order:
        with self.get_session() as session:
            order_orm = session.query(OrderORM).filter_by(order_id=order_id).first()
            return Order(**order_orm.to_dict(include_relationships=True))

    async def get_refunds(self) -> list[Order]:
        """

        :return:
        """
        with self.get_session() as session:
            order_orm_list = (
                session.query(OrderORM)
                .outerjoin(CustomerORM, OrderORM.customer_id == CustomerORM.uid)
                .outerjoin(PaymentORM, OrderORM.order_id == PaymentORM.order_id)
            ).filter_by(status=OrderStatus.RETURNED.value).all()
            return [Order(**order_orm.to_dict(include_relationships=True)) for order_orm in order_orm_list]
