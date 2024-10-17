from datetime import datetime
from sqlalchemy import Column, String, inspect, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.constants import ID_LEN
from src.database.sql import Base, engine


class CartItemORM(Base):
    __tablename__ = "cart_item"
    item_id: str = Column(String(ID_LEN), primary_key=True)
    cart_id: str = Column(String(ID_LEN), ForeignKey('cart.cart_id'))
    product_id: str = Column(String(ID_LEN), ForeignKey("products.product_id"))
    quantity: int = Column(Integer)
    cart = relationship("CartORM", back_populates='items', uselist=False)
    product = relationship("ProductsORM", backref='cart_items', uselist=True)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self, include_relationships=False):
        """
            Product should always be part of Cart Item independently of relationships
        :param include_relationships:
        :return:
        """
        return {
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "item_id": self.item_id,
            "cart": self.cart.to_dict() if self.cart and include_relationships else None,
            "product": self.product.to_dict() if self.product else None
        }


class CartORM(Base):
    __tablename__ = "cart"
    uid: str = Column(String(ID_LEN))
    cart_id: str = Column(String(ID_LEN), primary_key=True)
    created_at: datetime = Column(DateTime)
    converted_to_order: bool = Column(Boolean)
    converted_at: datetime = Column(DateTime)
    items = relationship('CartItemORM', back_populates='cart', uselist=True)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

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
