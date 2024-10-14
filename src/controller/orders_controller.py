from sqlalchemy.orm import joinedload

from src.controller import Controllers, error_handler
from src.database.models.customer import Order
from src.database.sql.customer import OrderORM, CustomerORM


class OrdersController(Controllers):
    def __init__(self):
        super().__init__()

    @error_handler
    async def get_orders(self) -> list[Order]:
        with self.get_session() as session:
            order_orm_list = session.query(OrderORM).all()
            return [Order(**order_orm) for order_orm in order_orm_list]

    @error_handler
    async def get_order(self, order_id: str) -> Order:
        with self.get_session() as session:
            order_orm = session.query(OrderORM).filter_by(order_id=order_id).first()
            return Order(**order_orm.to_dict())

