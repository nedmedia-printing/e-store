from flask import Flask
from sqlalchemy.orm import joinedload
import asyncio
from src.controller import Controllers, error_handler
from src.database.models.products import Category, Products, Inventory
from src.database.sql.products import CategoryORM, ProductsORM, InventoryORM


class InventoryController(Controllers):
    def __init__(self):
        super().__init__()
        self.__products_dict: dict[str, Products] = {}
        self.__categories: list[Category] = []
        self.__categories_dict = {}

    def init_app(self, app: Flask):
        asyncio.run(self.preload_inventory())
        super().init_app(app=app)

    @error_handler
    async def preload_inventory(self):
        self.__categories = await self.get_product_categories()
        self.__categories_dict = {category.category_id: category for category in self.__categories}
        self.__products_dict = {product.product_id: product for category in self.__categories for product in
                                category.products}

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
    async def get_product_categories(self) -> list[Category]:
        """Retrieves all product categories from the database with linked records."""
        with self.get_session() as session:
            # Query the CategoryORM and eagerly load related products and inventory entries
            categories_list_orm = (
                session.query(CategoryORM)
                .options(
                    joinedload(CategoryORM.products).joinedload(ProductsORM.inventory_entries),
                    joinedload(CategoryORM.inventory_entries)
                )
                .all()
            )
            # Convert ORM objects to Pydantic models using the to_dict method
            return [Category(**cat.to_dict(include_relationships=True)) for cat in categories_list_orm]

    @error_handler
    async def get_products(self) -> list[Products]:
        """
        Retrieves all products from the preloaded categories.
        :return: List of Product instances.
        """
        return list(self.__products_dict.values())

    @error_handler
    async def get_product(self, product_id: str) -> Products | None:
        """
        Retrieves a product by its ID from the preloaded products.
        :param product_id: The ID of the product to retrieve.
        :return: Product instance or None if not found.
        """
        return self.__products_dict.get(product_id)

    @error_handler
    async def get_product_inventory(self, product_id: str) -> list[Inventory] | None:
        """
        Retrieves the inventory entries for a product by its ID from the preloaded products.
        :param product_id: The ID of the product whose inventory entries are to be retrieved.
        :return: List of Inventory instances or None if not found.
        """
        product = self.__products_dict.get(product_id)
        if product:
            return product.inventory_entries
        return None

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

    @error_handler
    async def delete_inventory_entry(self, entry_id: str) -> bool:
        """
        Deletes an inventory entry by its ID.
        :param entry_id: The ID of the inventory entry to delete.
        :return: bool indicating whether the deletion was successful.
        """
        with self.get_session() as session:
            inventory_entry_orm = session.query(InventoryORM).filter_by(entry_id=entry_id).first()
            if inventory_entry_orm:
                session.delete(inventory_entry_orm)
                return True

        await self.preload_inventory()  # Update preloaded inventory after deletion
        return False

    @error_handler
    async def add_inventory_entry(self, inventory_entry: Inventory) -> Inventory:
        """
        Adds a new inventory entry.
        :param inventory_entry: The inventory entry to add.
        :return: The added inventory entry.
        """
        with self.get_session() as session:
            session.add(InventoryORM(**inventory_entry.dict()))

        await self.preload_inventory()  # Update preloaded inventory after adding a new entry
        return inventory_entry
