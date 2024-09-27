from datetime import date, datetime
from pydantic import BaseModel


def create_date_paid() -> date:
    return datetime.now().date()


class Orders(BaseModel):
    order_id: str
    uid: str
    total: int
    payment_status: str
    fulfilment_status: str
    delivery_type: str
    order_date: datetime
    last_status_update: datetime
    notes: str

