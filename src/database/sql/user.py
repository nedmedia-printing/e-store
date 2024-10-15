from sqlalchemy import Column, String, Boolean, inspect
from sqlalchemy.orm import relationship

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class UserORM(Base):
    """
    User Model
        User ORM
    """
    __tablename__ = 'users'
    uid: str = Column(String(ID_LEN), primary_key=True, unique=True, index=True)

    username: str = Column(String(NAME_LEN))
    password_hash: str = Column(String(255))
    email: str = Column(String(256))
    account_verified: bool = Column(Boolean, default=False)
    is_system_admin: bool = Column(Boolean, default=False)
    is_client: bool = Column(Boolean, default=False)
    customer = relationship("CustomerORM", back_populates="user")

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def __init__(self,
                 uid: str,
                 username: str,
                 password_hash: str,
                 email: str,
                 account_verified: bool = False,
                 is_system_admin: bool = False,
                 is_client: bool = False):

        self.uid = uid
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.account_verified = account_verified
        self.is_system_admin = is_system_admin
        self.is_client = is_client

    def __bool__(self) -> bool:
        return bool(self.uid) and bool(self.username) and bool(self.email)

    def to_dict(self, include_relationships=False) -> dict[str, str | bool]:
        return {
            'uid': self.uid,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'account_verified': self.account_verified,
            'is_system_admin': self.is_system_admin,
            'is_client': self.is_client,
            'customer': self.customer.to_dict() if self.customer and include_relationships else None
        }
