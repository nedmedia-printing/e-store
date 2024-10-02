from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.database.constants import ID_LEN, NAME_LEN

Base = declarative_base()


class ProductsORM(Base):
    __tablename__ = "products"
    product_id: str = Column(String(ID_LEN), primary_key=True)
    category_id: str = Column(String(ID_LEN), ForeignKey('category.category_id'))
    supplier_id: str = Column(String(ID_LEN))
    barcode: str = Column(String(NAME_LEN))
    name: str = Column(String(NAME_LEN))
    description: str = Column(String(NAME_LEN))
    sell_price: int = Column(Integer)
    buy_price: int = Column(Integer)
    image_name: str = Column(String(NAME_LEN))
    time_of_entry: datetime = Column(DateTime)
    inventory_entries = relationship('InventoryORM', uselist=True)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "category_id": self.category_id,
            "supplier_id": self.supplier_id,
            "barcode": self.barcode,
            "name": self.name,
            "description": self.description,
            "sell_price": self.sell_price,
            "buy_price": self.buy_price,
            "image_name": self.image_name,
            "time_of_entry": self.time_of_entry.isoformat() if self.time_of_entry else None,
            "inventory_entries": [entry.to_dict() for entry in self.inventory_entries]
        }


class CategoryORM(Base):
    __tablename__ = "category"
    category_id: str = Column(String(ID_LEN), primary_key=True)
    name: str = Column(String(NAME_LEN))
    description: str = Column(String(NAME_LEN))
    image_name: str = Column(String(255))
    is_visible: bool = Column(Boolean)
    products = relationship('ProductsORM')
    inventory_entries = relationship('InventoryORM', uselist=True)

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "image_name": self.image_name,
            "is_visible": self.is_visible,
            "products": [product.to_dict() for product in self.products],
            "inventory_entries": [entry.to_dict() for entry in self.inventory_entries]
        }


class InventoryORM(Base):
    __tablename__ = "inventory"
    entry_id: str = Column(String(ID_LEN), primary_key=True)
    product_id: str = Column(String(ID_LEN), ForeignKey('products.product_id'))
    category_id: str = Column(String(ID_LEN), ForeignKey('category.category_id'))
    entry: int = Column(Integer)
    action_type: str = Column(String(NAME_LEN))
    time_of_entry: datetime = Column(DateTime)

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "product_id": self.product_id,
            "category_id": self.category_id,
            "entry": self.entry,
            "action_type": self.action_type,
            "time_of_entry": self.time_of_entry.isoformat() if self.time_of_entry else None
        }
