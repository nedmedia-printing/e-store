from sqlalchemy import Column, String, inspect
from sqlalchemy.orm import relationship

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class ProfileORM(Base):
    __tablename__ = "profile"
    uid = Column(String(ID_LEN), primary_key=True)
    profile_name = Column(String(NAME_LEN))
    first_name = Column(String(NAME_LEN))
    surname = Column(String(NAME_LEN))
    cell = Column(String(16))
    email = Column(String(255))
    notes = Column(String(255))
    user = relationship("UserORM", backref='profile')
    historical_orders = relationship("OrderORM", backref='profile')
    payment_history = relationship('PaymentORM', backref='profile')
    cart = relationship('CartORM', backref='profile')

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self, include_relationships: bool = False):
        """
        Converts the ProfileORM instance to a dictionary.
        :param include_relationships: Include related data if True.
        :return: Dictionary representation of the instance.
        """
        data = {
            'uid': self.uid,
            'profile_name': self.profile_name,
            'first_name': self.first_name,
            'surname': self.surname,
            'cell': self.cell,
            'email': self.email,
            'notes': self.notes
        }

        if include_relationships:
            data['user'] = self.user.to_dict() if self.user else None
            data['historical_orders'] = [order.to_dict(include_relationships=True) for order in self.historical_orders]
            data['payment_history'] = [payment.to_dict(include_relationships=True) for payment in self.payment_history]
            data['cart'] = self.cart.to_dict(include_relationships=True) if self.cart else None

        return data
