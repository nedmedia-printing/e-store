from datetime import date, datetime

from pydantic import BaseModel, Field, validator, PositiveInt

from src.database.tools import create_transaction_id
from src.utils import create_id


def create_date_paid() -> date:
    return datetime.now().date()


class Payment(BaseModel):
    """
    Represents a payment transaction.
   """
    transaction_id: str = Field(default_factory=create_id)
    subscription_id: str | None
    package_id: str | None
    invoice_number: int | None
    amount_paid: PositiveInt
    date_paid: date = Field(default_factory=create_date_paid)
    payment_method: str
    is_successful: bool
    month: PositiveInt
    comments: str

    def __eq__(self, other):
        """
        Define the equality comparison for Payment instances.
        Two Payment instances are equal if their transaction_id and receipt_number are equal.

        :param other: The other instance to compare with.
        :return: True if the transaction_id and receipt_number are equal, False otherwise.
        """
        if not isinstance(other, Payment):
            return False

        return (self.transaction_id, self.invoice_number) == (other.transaction_id, other.invoice_number)

    @property
    def year(self) -> int:
        return self.date_paid.year

    @property
    def long_day(self) -> int:
        return (self.date_paid.year * 365) + self.date_paid.toordinal()


class CreatePayment(BaseModel):
    """
    Represents a payment transaction.
   """
    transaction_id: str = Field(default_factory=create_transaction_id, description="BankTransaction ID")
    invoice_number: int
    amount_paid: int
    date_paid: date = Field(default_factory=lambda: create_date_paid())
    payment_method: str | None
    is_successful: bool = Field(default=False)
    month: int | None
    comments: str | None


class UpdatePayment(BaseModel):
    transaction_id: str
    invoice_number: int
    amount_paid: int
    date_paid: str
    payment_method: str
    is_successful: bool
    comments: str


class UnitInvoicePaymentForm(BaseModel):
    invoice_number: int
    amount_paid: int
    payment_verified: bool = Field(default=False)


class PaymentVerificationForm(BaseModel):
    transaction_id: str
    invoice_number: str
    payment_method: str
    amount_paid: int
    month: int
    date_paid: date
    comments: str
    is_successful: bool

    @validator('amount_paid', pre=True)
    def validate_amount_paid(cls, value):
        if isinstance(value, str):
            value = int(value.replace(',', ''))
        return value

    @validator('month', pre=True)
    def validate_month(cls, value):
        if isinstance(value, str):
            if value.isdecimal():
                return int(value)
        month = datetime.now().month
        return month
