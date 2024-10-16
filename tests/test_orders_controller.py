import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.controller.orders_controller import OrdersController
from src.database.models.customer import Order, OrderStatus, Payment, PaymentStatus
from src.database.sql.customer import OrderORM, CustomerORM, PaymentORM


@pytest.mark.asyncio
class TestOrdersController:
    @pytest.fixture
    def controller(self):
        return OrdersController()

    @pytest.fixture
    def mock_session(self):
        with patch('src.controller.Controllers.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session
            yield mock_session

    @pytest.fixture
    def mock_order_data(self):
        # Mock data for OrderORM
        return OrderORM(
            order_id="order_1",
            customer_id="customer_1",
            order_date=datetime.now(),
            discount_percent=10,
            status=OrderStatus.PENDING.value
        )

    async def test_get_orders(self, controller, mock_session, mock_order_data):
        # Set up the mock query
        mock_session.query.return_value.outerjoin.return_value.outerjoin.return_value.all.return_value = [mock_order_data]

        # Mock OrderORM's to_dict method
        mock_order_data.to_dict.return_value = {
            "order_id": "order_1",
            "customer_id": "customer_1",
            "order_date": datetime.now(),
            "discount_percent": 10,
            "status": OrderStatus.PENDING.value,
            "payments": [],
            "order_items": []
        }

        orders = await controller.get_orders()

        assert len(orders) == 1
        assert orders[0].order_id == "order_1"
        assert orders[0].status == OrderStatus.PENDING.value

    async def test_get_order(self, controller, mock_session, mock_order_data):
        # Set up the mock query
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_order_data

        # Mock OrderORM's to_dict method
        mock_order_data.to_dict.return_value = {
            "order_id": "order_1",
            "customer_id": "customer_1",
            "order_date": datetime.now(),
            "discount_percent": 0,
            "status": OrderStatus.PENDING.value,
            "payments": [],
            "order_items": []
        }

        order = await controller.get_order(order_id="order_1")

        assert order.order_id == "order_1"
        assert order.status == OrderStatus.PENDING.value

    async def test_get_refunds(self, controller, mock_session, mock_order_data):
        # Set up the mock query for refunded orders
        mock_order_data.status = OrderStatus.RETURNED.value
        mock_session.query.return_value.outerjoin.return_value.outerjoin.return_value.filter_by.return_value.all.return_value = [mock_order_data]

        # Mock OrderORM's to_dict method
        mock_order_data.to_dict.return_value = {
            "order_id": "order_2",
            "customer_id": "customer_2",
            "order_date": datetime.now(),
            "discount_percent": 0,
            "status": OrderStatus.RETURNED.value,
            "payments": [],
            "order_items": []
        }

        refunds = await controller.get_refunds()

        assert len(refunds) == 1
        assert refunds[0].order_id == "order_2"
        assert refunds[0].status == OrderStatus.RETURNED.value

    async def test_add_payment_updates_status(self):
        order = Order(
            order_id="123",
            customer_id="456",
            discount_percent=0,
            status=OrderStatus.PENDING.value,
            order_items=[]
        )
        payment = Payment(
            order_id=order.order_id,
            amount=10000,
            payment_method="Credit Card",
            payment_status=PaymentStatus.COMPLETED.value
        )

        order.add_payment(payment)

        assert order.is_paid_in_full
        assert order.status == OrderStatus.PAID.value

    async def test_order_balance_calculation(self):
        order = Order(
            order_id="123",
            customer_id="456",
            discount_percent=0,
            status=OrderStatus.PENDING.value,
            order_items=[
                {"product_id": "prod1", "quantity": 2, "price": 5000},
                {"product_id": "prod2", "quantity": 1, "price": 10000},
            ]
        )
        payment = Payment(
            order_id=order.order_id,
            amount=10000,
            payment_method="Credit Card",
            payment_status=PaymentStatus.COMPLETED.value
        )

        order.add_payment(payment)

        assert order.order_balance == 5000
        assert not order.is_paid_in_full
