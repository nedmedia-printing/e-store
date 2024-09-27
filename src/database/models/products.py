from datetime import date, datetime
from pydantic import BaseModel


def create_date_paid() -> date:
    return datetime.now().date()


class Products(BaseModel):
    product_id: str
    barcode: str
    name: str
    description: str
    sell_price: int
    buy_price: int
    category_id: str
    image_name: str
    supplier_id: str


class Category(BaseModel):
    category_id: str
    name: str
    description: str
    image_name: str
    is_visible: bool


class Inventory(BaseModel):
    product_id: str
    category_id: str
    current_inventory: int
    time_of_entry: datetime


