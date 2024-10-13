from sqlalchemy.orm import joinedload

from src.controller import Controllers, error_handler
from src.database.models.customer import Customer
from src.database.models.products import Category, Products, Inventory
from src.database.sql.customer import CustomerORM
from src.database.sql.products import CategoryORM, ProductsORM, InventoryORM


class CustomerController(Controllers):
    def __init__(self):
        super().__init__()


    @error_handler
    async def add_customer(self, customer: Customer):
        """

        :param customer:
        :return:
        """
        pass

    async def get_customers(self):
        """

        :return:
        """
        with self.get_session() as session:
            customers_orm_list = session.query(CustomerORM).all()

            return [Customer(**customer_orm) for customer_orm in customers_orm_list]
