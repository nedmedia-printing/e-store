from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator, PositiveInt, EmailStr
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
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"
    FAILED = "FAILED"

    @classmethod
    def status_list(cls):
        return [status.value for status in cls]


class PaymentStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"

    @classmethod
    def status_list(cls):
        return [status.value for status in cls]


class Payment(BaseModel):
    """
    Payment Class

    Attributes:
        - payment_id (str): Unique identifier for the payment.
        - order_id (str): Identifier for the order associated with this payment.
        - amount (int): The amount of the payment in cents.
        - payment_date (datetime): The date and time when the payment was made.
        - payment_method (str): The method used for the payment (e.g., Credit Card, PayPal, Bank Transfer).
        - payment_status (str): The current status of the payment (e.g., PENDING, COMPLETED, FAILED, REFUNDED, CANCELLED).

    Methods:
        - create_fake_payment(order_id: str) -> Payment:
            Creates a fake payment for testing purposes.

    Example:
        payment = Payment.create_fake_payment(order_id="123")
        print(payment)
    """
    payment_id: str = Field(default_factory=create_id)
    order_id: str
    amount: PositiveInt
    payment_date: datetime = Field(default_factory=south_african_standard_time)
    payment_method: str
    payment_status: str = Field(default=PaymentStatus.PENDING.value)

    @field_validator('amount')
    def check_non_negative(cls, v):
        if v < 0:
            raise ValueError('Amount must be non-negative')
        return v

    @staticmethod
    def create_fake_payment(order_id: str) -> 'Payment':
        fake = Faker()
        return Payment(
            payment_id=fake.uuid4(),
            order_id=order_id,
            amount=random.randint(1000, 50000),
            payment_date=datetime.now(),
            payment_method=random.choice(['Credit Card', 'PayPal', 'Bank Transfer']),
            payment_status=PaymentStatus.COMPLETED.value
        )


class Order(BaseModel):
    """
    Order Class

    Attributes:
        - order_id (str): Unique identifier for the order.
        - customer_id (str): Identifier for the customer who placed the order.
        - order_date (datetime): The date and time when the order was placed.
        - total_amount (int): The total amount of the order in cents.
        - status (str): The current status of the order.
        - date_paid (datetime | None): The date and time when the order was paid, if applicable.

    Order Status Progression:
        - PENDING: The order has been placed but not yet processed.
        - PROCESSING: The order is being processed.
        - SHIPPED: The order has been shipped to the customer.
        - DELIVERED: The order has been delivered to the customer.
        - PAID: The order has been paid for.
        - CANCELLED: The order has been cancelled.
        - RETURNED: The order has been returned by the customer.
        - FAILED: The order process has failed.

    Methods:
        - update_status(new_status: OrderStatus) -> None:
            Updates the status of the order. If the new status is PAID, it also sets the date_paid attribute to the current date and time.

    Example:
        order = Order(
            order_id="123",
            customer_id="456",
            total_amount=10000
        )
        order.update_status(OrderStatus.PROCESSING)
        print(order.status)  # Output: 'PROCESSING'
    """

    order_id: str = Field(default_factory=create_id)
    customer_id: str
    order_date: datetime = Field(default_factory=south_african_standard_time)
    total_amount: int
    status: str = Field(default=OrderStatus.PENDING.value)
    date_paid: datetime | None = Field(default=None)
    payments: list[Payment] = []

    @property
    def order_balance(self) -> int:
        total_paid = sum(
            payment.amount for payment in self.payments if payment.payment_status == PaymentStatus.COMPLETED.value)
        return self.total_amount - total_paid

    @property
    def is_paid_in_full(self) -> bool:
        total_paid = sum(
            payment.amount for payment in self.payments if payment.payment_status == PaymentStatus.COMPLETED.value)
        return total_paid >= self.total_amount

    def update_status(self, new_status: OrderStatus) -> None:
        if new_status in OrderStatus:
            self.status = new_status.value
            if new_status == OrderStatus.PAID and self.is_paid_in_full:
                self.date_paid = datetime.now()
        else:
            raise ValueError(f"Invalid status: {new_status}")

    def add_payment(self, payment: Payment) -> None:
        self.payments.append(payment)
        if payment.payment_status == PaymentStatus.COMPLETED.value:
            self.update_status(OrderStatus.PAID)
        if self.is_paid_in_full:
            self.update_status(new_status=OrderStatus.PAID)


class Customer(BaseModel):
    """
     Customer Class

     Attributes:
         - uid (str): Unique identifier for the customer.
         - name (str): Name of the customer.
         - order_count (int): The number of orders placed by the customer.
         - total_spent (int): The total amount spent by the customer in cents.
         - city (str): The city where the customer is located.
         - last_seen (datetime): The date and time when the customer was last seen.
         - last_order_date (datetime | None): The date and time when the last order was placed by the customer.
         - notes (str | None): Additional notes about the customer.
         - orders (list[Order]): List of orders placed by the customer.
         - user (User): User information associated with the customer.

     Properties:
         - email (str): Email address of the customer.
         - average_spent_per_order (float): The average amount spent per order by the customer.
         - last_order (str): The ID of the last order placed by the customer.

     Methods:
         - create_fake_customer() -> Customer:
             Creates a fake customer for testing purposes.

     Example:
         customer = Customer.create_fake_customer()
         print(customer)
     """
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
        total_spent = random.randint(1000, 10000)
        last_order_date = datetime.now() - timedelta(days=random.randint(1, 365))
        last_seen = last_order_date + timedelta(days=random.randint(1, 30))
        uid = create_id()
        email = fake.email()
        created_user = CreateUser(uid=uid, username=email, password=fake.password(), email=email, account_verified=True,
                                  is_client=True)
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
            user=user
        )


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    city: str| None = Field(default=None)
    notes: str | None = Field(default=None)


if __name__ == "__main__":
    # Example usage:
    order = Order(
        order_id="123",
        customer_id="456",
        total_amount=10000
    )

    # Add payments to the order
    payment1 = Payment(order_id=order.order_id, amount=5000, payment_method='Credit Card',
                       payment_status=PaymentStatus.COMPLETED.value)
    payment2 = Payment(order_id=order.order_id, amount=5000, payment_method='PayPal',
                       payment_status=PaymentStatus.COMPLETED.value)

    order.add_payment(payment1)
    order.add_payment(payment2)

    print(order.is_paid_in_full)  # Output: True
    print(order.order_balance)  # Output: 0
