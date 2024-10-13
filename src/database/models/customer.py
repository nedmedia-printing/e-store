from datetime import date, datetime
from pydantic import BaseModel, Field
from enum import Enum

from src.utils import south_african_standard_time, create_id


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
    order_date: datetime
    total_amount: int
    status: str
    date_paid: datetime = Field(default_factory=south_african_standard_time)


class Customer(BaseModel):
    uid: str
    order_count: int
    total_spent: int
    city: str
    last_seen: datetime
    last_order_date: datetime
    notes: str
    orders: list[Order] = []

    @property
    def average_spent_per_order(self) -> float:
        return self.total_spent / self.order_count if self.order_count else 0

    @property
    def last_order(self) -> str:
        if not self.orders:
            return "N/A"
        return max(self.orders, key=lambda x: x.order_date).order_id
