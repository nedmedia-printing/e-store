from sqlalchemy import Column, String, inspect, Integer, Boolean, ForeignKey, DateTime, Sequence
from sqlalchemy.orm import relationship
from src.database.constants import ID_LEN
from src.database.sql import Base, engine
from src.database.sql.products import ProductsORM


class PaymentORM(Base):
    __tablename__ = "payment"
    transaction_id = Column(String(ID_LEN), primary_key=True)
    receipt_number = Column(Integer, Sequence('invoice_number_seq'), autoincrement=True)
    order_id = Column(String(ID_LEN), ForeignKey('orders.order_id'))
    amount_paid = Column(Integer)
    date_paid = Column(DateTime)
    payment_method = Column(String(32))
    is_successful = Column(Boolean, default=False)
    month = Column(Integer)
    comments = Column(String(255))
    order = relationship("OrderORM", back_populates="payments", uselist=False)

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
            'transaction_id': self.transaction_id,
            'order_id': self.order_id,
            'receipt_number': self.receipt_number,
            'amount_paid': self.amount_paid,
            'date_paid': self.date_paid,
            'payment_method': self.payment_method,
            'is_successful': self.is_successful,
            'month': self.month,
            'comments': self.comments,
            "order": self.order.to_dict() if self.order and include_relationships else None
        }


class CustomerORM(Base):
    __tablename__ = "customers"
    uid = Column(String(ID_LEN), ForeignKey('users.uid'), primary_key=True)
    order_count = Column(Integer)
    name = Column(String(60))
    total_spent = Column(Integer)  # Stored in cents
    city = Column(String(255))
    last_seen = Column(DateTime)
    last_order_date = Column(DateTime)
    notes = Column(String(255))

    # Relationship to Orders products
    orders = relationship("OrderORM", back_populates="customer", uselist=True)

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
            "uid": self.uid,
            "name": self.name,
            "order_count": self.order_count,
            "total_spent": self.total_spent,
            "city": self.city,
            "last_seen": self.last_seen,
            "last_order_date": self.last_order_date,
            "notes": self.notes,
            "orders": [order.to_dict() for order in self.orders] if include_relationships else []

        }


class OrderORM(Base):
    __tablename__ = "orders"
    order_id = Column(String(ID_LEN), primary_key=True)
    customer_id = Column(String(ID_LEN), ForeignKey("customers.uid"))
    order_date = Column(DateTime)
    discount_percent = Column(Integer)  # Stored in cents
    status = Column(String(50))
    date_paid = Column(DateTime)

    # Relationship to Customer
    customer = relationship("CustomerORM", back_populates="orders", uselist=False)
    payments = relationship("PaymentORM", back_populates="order", uselist=True)
    order_items = relationship("OrderItemsORM", back_populates="order", uselist=True)

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
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date,
            "total_amount": self.total_amount,
            "status": self.status,
            "date_paid": self.date_paid,
            "customer": self.customer.to_dict() if self.customer and include_relationships else None,
            "payments": [payment.to_dict() for payment in self.payments] if include_relationships else [],
            "items": [item.to_dict() for item in self.order_items] if self.order_items else []
        }


class OrderItemsORM(Base):
    __tablename__ = "order_items"
    item_id = Column(String(ID_LEN), primary_key=True)
    order_id = Column(String(ID_LEN), ForeignKey("orders.order_id"))
    product_id = Column(String(ID_LEN), ForeignKey("products.product_id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)  # Price at the time of order, stored in cents

    # Relationship to Order
    order = relationship("OrderORM", back_populates="order_items")

    # Relationship to Product
    product = relationship("ProductsORM", uselist=False)

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
            "item_id": self.item_id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
            "product": self.product.to_dict() if self.product else None,
            "order": self.order.to_dict() if self.order and include_relationships else None
        }
