from src.controller import Controllers, error_handler
from src.database.models.products import Category, Products, Inventory
from src.database.sql.products import CategoryORM, ProductsORM, InventoryORM


class InventoryController(Controllers):
    def __init__(self):
        super().__init__()

    @error_handler
    async def add_category(self, category: Category) -> Category | None:
        with self.get_session() as session:
            is_category_available = session.query(CategoryORM).filter_by(name=category.name.casefold()).first()
            if is_category_available:
                return None
            session.add(CategoryORM(**category.dict(exclude={'display_images'})))
        return category

    @error_handler
    async def get_product_categories(self):
        """

        :return:
        """
        with self.get_session() as session:
            categories_list_orm = session.query(CategoryORM).all()
            return [Category(**cat.to_dict()) for cat in categories_list_orm]

    @error_handler
    async def add_product(self, product: Products) -> Products | None:
        with self.get_session() as session:
            is_product_available = session.query(ProductsORM).filter_by(name=product.name.casefold()).first()
            self.logger.info(f"Adding Product: {product}")
            if is_product_available:
                return None
            prepared_dict = product.dict(exclude={'display_images', 'image_name'})
            self.logger.info(f"Prepared Dict: {prepared_dict}")
            session.add(ProductsORM(**prepared_dict))
            return product

    @error_handler
    async def get_product(self, product_id: str) -> Products | None:
        """

        :param product_id:
        :return:
        """
        with self.get_session() as session:
            product_orm = session.query(ProductsORM).filter_by(product_id=product_id).first()
            if isinstance(product_orm, ProductsORM):
                return Products(**product_orm.to_dict())

    @error_handler
    async def create_inventory_entry(self, inventory: Inventory) -> Inventory:
        with self.get_session() as session:
            session.add(InventoryORM(**inventory.dict()))
            return inventory

    @error_handler
    async def get_products(self) -> list[Products]:
        """

        :return:
        """
        with self.get_session() as session:
            products_orm_list: list[ProductsORM] = session.query(ProductsORM).all()
            return [Products(**product.to_dict()) for product in products_orm_list if isinstance(product, ProductsORM)]

