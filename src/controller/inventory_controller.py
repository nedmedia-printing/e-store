from src.controller import Controllers
from src.database.models.products import Category, Products, Inventory
from src.database.sql.products import CategoryORM, ProductsORM, InventoryORM


class InventoryController(Controllers):
    def __init__(self):
        super().__init__()

    async def add_category(self, category: Category) -> Category | None:
        with self.get_session() as session:
            is_category_available = session.query(CategoryORM).filter_by(name=category.name).first()
            if is_category_available:
                return None
            session.add(CategoryORM(**category.dict()))
        return category

    async def get_product_categories(self):
        """

        :return:
        """
        with self.get_session() as session:
            categories_list_orm = session.query(CategoryORM).all()
            return [Category(**cat.to_dict()) for cat in categories_list_orm]

    async def add_product(self, product: Products):
        with self.get_session() as session:
            is_product_available = session.query(ProductsORM).filter_by(name=product.name).first()
            if is_product_available:
                return None

            session.add(ProductsORM(**product.dict()))

    async def create_inventory_entry(self, inventory: Inventory) -> Inventory:
        with self.get_session() as session:
            session.add(InventoryORM(**inventory.dict()))
            return inventory

    async def get_products(self):
        pass
