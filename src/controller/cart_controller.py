from sqlalchemy.orm import joinedload

from src.controller import Controllers, error_handler
from src.database.models.cart import Cart, CartItem
from src.database.models.customer import Customer
from src.database.sql.cart import CartORM, CartItemORM
from src.database.sql.customer import CustomerORM, OrderORM, PaymentORM


class CartController(Controllers):
    def __init__(self):
        super().__init__()

    @error_handler
    async def get_outstanding_customer_cart(self, uid: str) -> Cart | None:
        """
        Retrieves the outstanding customer cart with all linked products.
        :param uid: User ID
        :return: Cart instance or None if not found
        """
        with self.get_session() as session:
            cart_orm = (
                session.query(CartORM)
                .options(
                    joinedload(CartORM.items).joinedload(CartItemORM.product)
                )
                .filter_by(uid=uid, converted_to_order=False)
                .first()
            )
            if not cart_orm:
                return None
            return Cart(**cart_orm.to_dict(include_relationships=True))

    @error_handler
    async def add_cart_item(self, cart_item: CartItem) -> CartItem:
        """
        Adds an item to the customer's cart.
        :param cart_item: CartItem instance to be added
        :return: Added CartItem instance
        """
        with self.get_session() as session:
            # Check if the cart exists
            cart_orm = session.query(CartORM).filter_by(cart_id=cart_item.cart_id).first()
            if not cart_orm:
                raise ValueError("Cart not found")

            # Check if the item is already in the cart
            existing_item = session.query(CartItemORM).filter_by(cart_id=cart_item.cart_id,
                                                                 product_id=cart_item.product_id).first()
            if existing_item:
                # Update quantity if item exists
                existing_item.quantity += cart_item.quantity
            else:
                # Add new item
                new_cart_item = CartItemORM(
                    item_id=cart_item.item_id,
                    cart_id=cart_item.cart_id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity
                )
                session.add(new_cart_item)

            return cart_item

    @error_handler
    async def create_new_cart(self, cart: Cart) -> Cart:
        """
        Creates a new cart for the customer.
        :param cart: Cart instance to be created
        :return: Created Cart instance
        """
        with self.get_session() as session:
            # Create a new CartORM instance
            new_cart_orm = CartORM(
                cart_id=cart.cart_id,
                uid=cart.uid,
                created_at=cart.created_at,
                converted_to_order=cart.converted_to_order,
                converted_at=cart.converted_at
            )

            # Add cart items to the CartORM instance
            for item in cart.items:
                new_cart_item = CartItemORM(
                    item_id=item.item_id,
                    cart_id=item.cart_id,
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                new_cart_orm.items.append(new_cart_item)

            # Add the new cart to the session
            session.add(new_cart_orm)

            # Return the created cart
            return cart
