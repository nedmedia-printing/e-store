from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, inspect
from sqlalchemy.orm import relationship

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import engine, Base


class ProductsORM(Base):
    __tablename__ = "products"
    product_id: str = Column(String(ID_LEN), primary_key=True)
    category_id: str = Column(String(ID_LEN), ForeignKey('category.category_id'))
    supplier_id: str = Column(String(ID_LEN), nullable=True)
    barcode: str = Column(String(NAME_LEN))
    name: str = Column(String(NAME_LEN))
    description: str = Column(String(NAME_LEN))
    sell_price: int = Column(Integer)
    buy_price: int = Column(Integer)
    time_of_entry: datetime = Column(DateTime)
    inventory_entries = relationship('InventoryORM', uselist=True)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self, include_relationships=False):
        return {
            "product_id": self.product_id,
            "category_id": self.category_id,
            "supplier_id": self.supplier_id,
            "barcode": self.barcode,
            "name": self.name,
            "description": self.description,
            "sell_price": self.sell_price,
            "buy_price": self.buy_price,
            "time_of_entry": self.time_of_entry.isoformat() if self.time_of_entry else None,
            "inventory_entries": [entry.to_dict() for entry in self.inventory_entries] if self.inventory_entries and include_relationships else [],
            "cart_items": [item.to_dict() for item in self.cart_items] if include_relationships and self.cart_items else []
        }


class CategoryORM(Base):
    __tablename__ = "category"
    category_id: str = Column(String(ID_LEN), primary_key=True)
    name: str = Column(String(NAME_LEN))
    description: str = Column(String(NAME_LEN))
    is_visible: bool = Column(Boolean)
    products = relationship('ProductsORM')
    inventory_entries = relationship('InventoryORM', uselist=True)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self, include_relationships=False):
        return {
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "is_visible": self.is_visible,
            "products": [product.to_dict(include_relationships=include_relationships) for product in self.products]
            if self.products and include_relationships else [],
            "inventory_entries": [entry.to_dict() for entry in self.inventory_entries]
            if self.inventory_entries and include_relationships else []
        }


class InventoryORM(Base):
    __tablename__ = "inventory"
    entry_id: str = Column(String(ID_LEN), primary_key=True)
    blame: str = Column(String(ID_LEN))
    product_id: str = Column(String(ID_LEN), ForeignKey('products.product_id'))
    category_id: str = Column(String(ID_LEN), ForeignKey('category.category_id'))
    entry: int = Column(Integer)
    action_type: str = Column(String(NAME_LEN))
    time_of_entry: datetime = Column(DateTime)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self, include_relationships=False):
        return {
            "entry_id": self.entry_id,
            "product_id": self.product_id,
            "category_id": self.category_id,
            "blame": self.blame,
            "entry": self.entry,
            "action_type": self.action_type,
            "time_of_entry": self.time_of_entry.isoformat() if self.time_of_entry else None
        }
