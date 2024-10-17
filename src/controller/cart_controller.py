from sqlalchemy.orm import joinedload

from src.controller import Controllers, error_handler
from src.database.models.customer import Customer
from src.database.sql.customer import CustomerORM, OrderORM, PaymentORM

class CartController(Controllers):
    def __init__(self):
        pass


    def get_cart(self, uid: str):
        with self.get_session() as session:
            pass
        