from datetime import datetime

from sqlalchemy import Column, String, inspect, Integer, Boolean, ForeignKey, DateTime, Sequence
from sqlalchemy.orm import relationship
from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine
from src.database.sql.products import ProductsORM


class CartItemORM(Base):
    cart_id: str = Column(String(ID_LEN),  ForeignKey('cart.cart_id'))
    product_id: str = Column(String(ID_LEN), ForeignKey("products.product_id"))
    name: str = Column(String(NAME_LEN))
    price: int = Column(Integer)

    item_id: str = Column(String(ID_LEN), primary_key=True)
    cart = relationship("CartORM", back_populates='items', uselist=False)
    product = relationship("ProductsORM", backref='cart_item', uselist=False)


class CartORM(Base):
    __tablename__ = "cart"
    uid: str = Column(String(ID_LEN))
    cart_id: str = Column(String(ID_LEN), primary_key=True)
    created_at: datetime = Column(DateTime)
    converted_to_order: bool = Column(Boolean)
    converted_at: datetime = Column(DateTime)
    items = relationship('CartItemORM', back_populates='cart', uselist=True)

    def to_dict(self, include_relationships: bool = False) -> dict[str, str | datetime | bool]:
        """

        :return:
        """
        return {
            "uid": self.uid,
            "cart_id": self.cart_id,
            "created_at": self.created_at,
            "converted_to_order": self.converted_to_order,
            "converted_at": self.converted_at,
            "items": [item.to_dict() for item in self.items] if self.items and include_relationships else []
        }
