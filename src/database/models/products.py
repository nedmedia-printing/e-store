from datetime import date, datetime
from enum import Enum

from flask import url_for
from pydantic import BaseModel, Field, field_validator
from src.utils import create_id, south_african_standard_time, generate_isn13, load_files_in_folder, \
    products_upload_folder


class InventoryActionTypes(Enum):
    ADJUST_ADD: str = "ADJUST ADD"
    ADJUST_MINUS: str = "ADJUST MINUS"
    PURCHASE_SUPPLIER: str = "PURCHASE SUPPLIER"
    REFUND: str = "REFUND"
    BREAKAGE: str = "BREAKAGE"
    SALE: str = "SALE"
    FREE: str = "FREE"

    @classmethod
    def action_list(cls):
        return [action.value for action in cls]

    @classmethod
    def adding_actions(cls):
        return [InventoryActionTypes.ADJUST_ADD.value,
                InventoryActionTypes.PURCHASE_SUPPLIER.value, InventoryActionTypes.REFUND.value]

    @classmethod
    def subtracting_actions(cls):
        return [InventoryActionTypes.SALE.value, InventoryActionTypes.BREAKAGE.value,
                InventoryActionTypes.ADJUST_MINUS.value, InventoryActionTypes.FREE.value]


class Inventory(BaseModel):
    entry_id: str = Field(default_factory=create_id)
    product_id: str
    category_id: str
    entry: int
    action_type: str
    time_of_entry: datetime = Field(default_factory=south_african_standard_time)


class Products(BaseModel):
    product_id: str = Field(default_factory=create_id)
    category_id: str
    supplier_id: str | None = Field(default=None)
    barcode: str = Field(default_factory=generate_isn13)
    name: str
    description: str
    sell_price: int
    buy_price: int
    image_name: str | None = Field(default=None)
    display_images: list[str] | None = Field(default=[])
    time_of_entry: datetime = Field(default_factory=south_african_standard_time)
    inventory_entries: list[Inventory] | None = Field(default=[])

    @field_validator('name', mode='before')
    def strip_and_lowercase(cls, v: str) -> str:
        return v.strip().lower() if isinstance(v, str) else v

    @property
    def inventory_count(self) -> int:
        total_count = 0
        for entry in self.inventory_entries:
            if entry.action_type in InventoryActionTypes.adding_actions():
                total_count += entry.entry
            elif entry.action_type in InventoryActionTypes.subtracting_actions():
                total_count -= entry.entry
        return total_count

    def get_total_sales(self, start_date: datetime, end_date: datetime) -> int:
        total_sales = 0
        for entry in self.inventory_entries:
            # Filter by action type 'SALE' and check if the entry is within the date range
            if entry.action_type == InventoryActionTypes.SALE.value and start_date <= entry.time_of_entry <= end_date:
                total_sales += entry.entry
        return total_sales

    def get_total_purchases(self, start_date: datetime, end_date: datetime) -> int:
        total_purchases = 0
        for entry in self.inventory_entries:
            # Filter by action type 'PURCHASE_SUPPLIER' and check if the entry is within the date range
            if entry.action_type == InventoryActionTypes.PURCHASE_SUPPLIER.value and start_date <= entry.time_of_entry <= end_date:
                total_purchases += entry.entry
        return total_purchases

    @property
    def display_image_url(self) -> str:
        """
            lookup category images from the upload folder
        :return:
        """
        # folder_path = products_upload_folder(category_id=self.category_id, product_id=self.product_id)
        return url_for('image.display_images', category_id=self.category_id, product_id=self.product_id)


class Category(BaseModel):
    category_id: str = Field(default_factory=create_id)
    name: str
    description: str
    is_visible: bool = Field(default=True)
    display_images: list[str] | None = Field(default=[])
    products: list[Products]
    inventory_entries: list[Inventory]

    @field_validator('name', mode='before')
    def strip_and_lowercase(cls, v: str) -> str:
        return v.strip().lower() if isinstance(v, str) else v

    @property
    def product_count(self) -> int:
        return len(self.products)

    def get_total_sales(self, start_date: datetime, end_date: datetime) -> int:
        total_sales = 0
        # Iterate over all products in the category and sum their total sales
        for product in self.products:
            total_sales += product.get_total_sales(start_date, end_date)
        return total_sales

    def get_total_purchases(self, start_date: datetime, end_date: datetime) -> int:
        total_purchases = 0
        # Iterate over all products in the category and sum their total purchases
        for product in self.products:
            total_purchases += product.get_total_purchases(start_date, end_date)
        return total_purchases

    @property
    def display_image_url(self):
        """
            lookup category images from the upload folder
        :return:
        """
        # folder_path = products_upload_folder(category_id=self.category_id, product_id=self.product_id)
        return url_for('image.display_images', category_id=self.category_id, product_id=None)
