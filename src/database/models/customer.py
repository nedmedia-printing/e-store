from datetime import date, datetime
from pydantic import BaseModel


def create_date_paid() -> date:
    return datetime.now().date()


class Customer(BaseModel):
    uid: str
    order_count: int
    total_spent: int
    city: str
    last_seen: datetime
    last_order_date: datetime
    notes: str
    


