from sqlalchemy.orm import joinedload

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
            return [Category(**cat.to_dict(include_relationships=True)) for cat in categories_list_orm]

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

    async def get_category(self, category_id: str):
        """
        :param category_id:
        :return:
        """
        with self.get_session() as session:
            category_orm = session.query(CategoryORM) \
                .options(joinedload(CategoryORM.products)) \
                .filter_by(category_id=category_id) \
                .first()

            if not category_orm:
                return None

            # Convert dictionary to Pydantic model
            return Category(**category_orm.to_dict())

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

    async def update_product(self, product: Products) -> Products | None:
        """
            **update_product**
        :param product:
        :return:
        """
        with self.get_session() as session:
            product_orm = session.query(ProductsORM).filter_by(product_id=product.product_id).first()
            if not isinstance(product_orm, ProductsORM):
                return None

            for key, value in product.dict().items():
                if key != 'product_id':
                    setattr(product_orm, key, value)
            return product

    @error_handler
    async def create_inventory_entry(self, inventory: Inventory) -> Inventory:
        with self.get_session() as session:
            session.add(InventoryORM(**inventory.dict()))
            return inventory

    @error_handler
    async def get_products(self) -> list[Products]:
        """
        **get_products**

        :return:
        """
        with self.get_session() as session:
            products_orm_list: list[ProductsORM] = session.query(ProductsORM).all()
            return [Products(**product.to_dict()) for product in products_orm_list if isinstance(product, ProductsORM)]

    @error_handler
    async def get_category_products(self, category_id: str) -> list[Products]:
        """

        :param category_id:
        :return:
        """
        with self.get_session() as session:
            products_orm_list: list[ProductsORM] = session.query(ProductsORM).filter_by(category_id=category_id).all()
            return [Products(**product.to_dict()) for product in products_orm_list if isinstance(product, ProductsORM)]

    @error_handler
    async def get_product_inventory(self, product_id: str) -> list[Inventory]:
        """

        :param product_id:
        :return:
        """
        with self.get_session() as session:
            inventory_orm_list = session.query(InventoryORM).filter_by(product_id=product_id).all()
            return [Inventory(**inventory_orm.to_dict()) for inventory_orm in inventory_orm_list]

    @error_handler
    async def add_inventory_entry(self, inventory_entry: Inventory) -> Inventory:
        """

        :param inventory_entry:
        :return:
        """
        with self.get_session() as session:
            session.add(InventoryORM(**inventory_entry.dict()))
            return inventory_entry

    async def delete_inventory_entry(self, entry_id: str) -> tuple[Inventory, bool]:
        """

        :param entry_id:
        :return:
        """
        with self.get_session() as session:
            inventory_entry_orm = session.query(InventoryORM).filter_by(entry_id=entry_id).first()
            inventory = Inventory(**inventory_entry_orm.to_dict())
            if not inventory_entry_orm:
                return inventory, False
            session.delete(inventory_entry_orm)
            return inventory, True
