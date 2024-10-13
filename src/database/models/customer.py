from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import random
from faker import Faker

from src.database.models.users import User, CreateUser
from src.logger import init_logger
from src.utils import south_african_standard_time, create_id

customer_logger = init_logger("Customer Model")


class OrderStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"
    FAILED = "FAILED"

    @classmethod
    def status_list(cls):
        return [status.value for status in cls]


class Order(BaseModel):
    order_id: str = Field(default_factory=create_id)
    customer_id: str
    order_date: datetime = Field(default_factory=south_african_standard_time)
    total_amount: int
    status: str = Field(default=OrderStatus.PENDING.value)
    date_paid: datetime | None = Field(default=None)


class Customer(BaseModel):
    uid: str
    name: str
    order_count: int = Field(default=0)
    total_spent: int = Field(default=0)
    city: str
    last_seen: datetime = Field(default_factory=south_african_standard_time)
    last_order_date: datetime | None = Field(default=None)
    notes: str | None = Field(default=None)
    orders: list[Order] = Field(default_factory=list)
    user: User

    @property
    def email(self):
        return self.user.email

    @property
    def average_spent_per_order(self) -> float:
        return self.total_spent / self.order_count if self.order_count else 0

    @property
    def last_order(self) -> str:
        if not self.orders:
            return "N/A"
        return max(self.orders, key=lambda x: x.order_date).order_id

    @staticmethod
    def create_fake_customer() -> 'Customer':
        fake = Faker()
        order_count = random.randint(1, 20)
        total_spent = random.randint(100, 10000)
        last_order_date = datetime.now() - timedelta(days=random.randint(1, 365))
        last_seen = last_order_date + timedelta(days=random.randint(1, 30))

        uid = create_id()
        email = fake.email()
        created_user = CreateUser(uid=uid, username=email, password=fake.password(),
                                  email=email, account_verified=True, is_client=True)

        user = User(uid=created_user.uid, username=created_user.username, password_hash=created_user.password_hash,
                    email=created_user.email, account_verified=True, is_client=True)

        return Customer(
            uid=uid,
            name=fake.name(),
            order_count=order_count,
            total_spent=total_spent,
            city=fake.city(),
            last_seen=last_seen,
            last_order_date=last_order_date,
            notes=fake.sentence(),
            orders=[],
            user=user)
