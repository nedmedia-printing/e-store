from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

from src.database.constants import ID_LEN, NAME_LEN

Base = declarative_base()


class Products(Base):
    product_id: str = Column(String(ID_LEN), primary_key=True)
    category_id: str = Column(String(ID_LEN))
    supplier_id: str = Column(String(ID_LEN))
    name: str = Column(String(NAME_LEN))
    description: str = Column(String(NAME_LEN))
    sell_price: int = Column(Integer)
    buy_price: int = Column(Integer)
    image_name: str = Column(String(NAME_LEN))


class Category(Base):
    category_id: str = Column(String(ID_LEN))
    name: str = Column(String(NAME_LEN))
    description: str = Column(String(NAME_LEN))
    image_name: str = Column(String(255))
    is_visible: bool = Column(Boolean)


class Inventory(Base):
    product_id: str = Column(String(ID_LEN))
    category_id: str = Column(String(ID_LEN))
    current_inventory: int = Column(Integer)
    time_of_entry: datetime = Column(DateTime)

