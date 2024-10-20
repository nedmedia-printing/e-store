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
        Retrieves all product categories from the database with linked records.
        :return: List of Category instances
        """
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
            return product

    @error_handler
    async def get_category(self, category_id: str) -> Category | None:
        """
        Retrieves a category by ID along with its products and their inventory entries.
        :param category_id: Category ID
        :return: Category instance or None if not found
        """
        with self.get_session() as session:
            category_orm = (
                session.query(CategoryORM)
                .options(
                    joinedload(CategoryORM.products).joinedload(ProductsORM.inventory_entries)
                )
                .filter_by(category_id=category_id)
                .first()
            )
            if not category_orm:
                return None

            return Category(**category_orm.to_dict(include_relationships=True))

    @error_handler
    async def get_product(self, product_id: str) -> Products | None:
        """
        Retrieves a product by ID along with its inventory entries.
        :param product_id: Product ID
        :return: Product instance or None if not found
        """
        with self.get_session() as session:
            product_orm = (
                session.query(ProductsORM)
                .options(
                    joinedload(ProductsORM.inventory_entries)
                )
                .filter_by(product_id=product_id)
                .first()
            )
            if not product_orm:
                return None

            return Products(**product_orm.to_dict(include_relationships=True))

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
        Retrieves all products from the database with linked inventory entries.
        :return: List of Product instances
        """
        with self.get_session() as session:
            products_orm_list: list[ProductsORM] = (
                session.query(ProductsORM)
                .options(
                    joinedload(ProductsORM.inventory_entries)
                )
                .all()
            )
            return [Products(**product.to_dict(include_relationships=True)) for product in products_orm_list if
                    isinstance(product, ProductsORM)]

    @error_handler
    async def get_category_by_slug(self, slug: str) -> Category:
        """
            first retrieve all categories second compare the slug for each category and return the matching one
            retrieve the category with its linked products
        :param slug:
        :return:
        """
        categories = await self.get_product_categories()
        category = next((cat for cat in categories if cat.display_slug == slug), None)
        return category

    @error_handler
    async def get_category_products(self, category_id: str) -> list[Products]:
        """
        Retrieves products by category ID along with their inventory entries.
        :param category_id: Category ID
        :return: List of Product instances
        """
        with self.get_session() as session:
            products_orm_list: list[ProductsORM] = (
                session.query(ProductsORM)
                .options(
                    joinedload(ProductsORM.inventory_entries)
                )
                .filter_by(category_id=category_id)
                .all()
            )
            return [Products(**product.to_dict(include_relationships=True)) for product in products_orm_list if
                    isinstance(product, ProductsORM)]

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
            self.logger.info(f"created new inventory entry: {inventory_entry}")
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
