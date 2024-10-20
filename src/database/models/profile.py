from pydantic import BaseModel, Field, Extra

from src.database.models.cart import Cart
from src.database.models.customer import Order, Payment
from src.utils import create_id


class Attachment(BaseModel):
    """
    **Attachment**
    Represents a file or artwork associated with an order.
    """
    attachment_id: str = Field(default_factory=create_id)
    order_id: str

    file_name: str
    file_type: str
    file_url: str


class Profile(BaseModel):
    """
        **Profile**
            allows users to create personalized settings
            such us - deposit multiplier
    """
    uid: str
    profile_name: str | None
    first_name: str | None
    surname: str | None
    cell: str | None
    email: str | None
    notes: str | None
    historical_orders: list[Order]
    payment_history: list[Payment]
    cart: Cart | None
    attachments: list[Attachment] | None
    # class Config:
    #     extra = Extra.ignore


