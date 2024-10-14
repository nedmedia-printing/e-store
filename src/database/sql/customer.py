from sqlalchemy import Column, String, inspect, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class CustomerORM(Base):
    __tablename__ = "customers"
    uid = Column(String(ID_LEN),  ForeignKey('users.uid'), primary_key=True)
    order_count = Column(Integer)
    name: str = Column(String(60))
    total_spent = Column(Integer)  # Stored in cents
    city = Column(String(255))
    last_seen = Column(DateTime)
    last_order_date = Column(DateTime)
    notes = Column(String(255))

    # Relationship to Ordersproducts
    orders = relationship("OrderORM", back_populates="customer")
    user = relationship("UserORM", back_populates='customer')

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "order_count": self.order_count,
            "total_spent": self.total_spent,
            "city": self.city,
            "last_seen": self.last_seen,
            "last_order_date": self.last_order_date,
            "notes": self.notes,
            "orders": [order.to_dict() for order in self.orders],
            "user": self.user.to_dict() if self.user else None
        }


class OrderORM(Base):
    __tablename__ = "orders"
    order_id = Column(String(ID_LEN), primary_key=True)
    customer_id = Column(String(ID_LEN), ForeignKey("customers.uid"))
    order_date = Column(DateTime)
    total_amount = Column(Integer)  # Stored in cents
    status = Column(String(50))
    date_paid = Column(DateTime)

    # Relationship to Customer
    customer = relationship("CustomerORM", back_populates="orders")

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date,
            "total_amount": self.total_amount,
            "status": self.status,
            "date_paid": self.date_paid
        }
