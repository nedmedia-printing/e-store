from flask import Flask
from sqlalchemy.orm import joinedload
import asyncio
from src.controller import Controllers, error_handler
from src.database.models.products import Category, Products, Inventory
from src.database.sql.products import CategoryORM, ProductsORM, InventoryORM


class InventoryController(Controllers):
    def __init__(self):
        super().__init__()
        self.__categories = []
        self.__categories_dict = {}

    def init_app(self, app: Flask):
        asyncio.run(self.preload_inventory())
        super().init_app(app=app)

    @error_handler
    async def preload_inventory(self):
        self.__categories = await self.get_product_categories()
        self.__categories_dict = {category.category_id: category for category in self.__categories}

    @error_handler
    async def get_preloaded_categories(self) -> list[Category]:
        return self.__categories

    @error_handler
    async def add_category(self, category: Category) -> Category | None:
        with self.get_session() as session:
            is_category_available = session.query(CategoryORM).filter_by(name=category.name.casefold()).first()
            if is_category_available:
                return None
            session.add(CategoryORM(**category.dict(exclude={'display_images'})))
        await self.preload_inventory()  # Update categories after adding a new one
        return category

    @error_handler
    async def get_category(self, category_id: str) -> Category | None:
        """
        Retrieves a category by ID from the preloaded categories.
        :param category_id: The ID of the category to retrieve.
        :return: Category instance or None if not found.
        """
        return self.__categories_dict.get(category_id)

    @error_handler
    async def get_product_categories(self):
        """ Retrieves all product categories from the database with linked records. """
        with self.get_session() as session:
            categories_list_orm = (
                session.query(CategoryORM)
                .options(
                    joinedload(CategoryORM.products).joinedload(ProductsORM.inventory_entries)
                )
                .all()
            )
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
            await self.preload_inventory()  # Update categories after adding a new product
            return product

    @error_handler
    async def update_product(self, product: Products) -> Products | None:
        """ **update_product** """
        with self.get_session() as session:
            product_orm = session.query(ProductsORM).filter_by(product_id=product.product_id).first()
            if not isinstance(product_orm, ProductsORM):
                return None
            for key, value in product.dict().items():
                if key != 'product_id':
                    setattr(product_orm, key, value)
            await self.preload_inventory()  # Update categories after updating a product
            return product

    @error_handler
    async def create_inventory_entry(self, inventory: Inventory) -> Inventory:
        with self.get_session() as session:
            session.add(InventoryORM(**inventory.dict()))
            await self.preload_inventory()  # Update categories after creating a new inventory entry
            return inventory

    @error_handler
    async def get_category_by_slug(self, slug: str) -> Category | None:
        """
        Retrieves a category by its slug from the preloaded categories.
        :param slug: The slug of the category to retrieve.
        :return: Category instance or None if not found.
        """
        for category in self.__categories:
            if category.display_slug == slug:
                return category
        return
