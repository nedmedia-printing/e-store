from flask import Flask
import asyncio
from sqlalchemy.orm import joinedload

from src.controller import Controllers, error_handler
from src.database.models.cart import Cart, CartItem
from src.database.sql.cart import CartORM, CartItemORM


class CartController(Controllers):
    def __init__(self):
        super().__init__()
        self.__carts = []
        self.__carts_dict = {}

    def init_app(self, app: Flask):
        asyncio.run(self.preload_carts())

    @error_handler
    async def preload_carts(self):
        self.__carts = await self.get_all_carts()
        self.__carts_dict = {cart.cart_id: cart for cart in self.__carts}

    @error_handler
    async def get_all_carts(self) -> list[Cart]:
        """ Retrieves all carts from the database with linked items. """
        with self.get_session() as session:
            carts_list_orm = (
                session.query(CartORM)
                .options(
                    joinedload(CartORM.items).joinedload(CartItemORM.product)
                )
                .all()
            )
            return [Cart(**cart.to_dict(include_relationships=True)) for cart in carts_list_orm]

    @error_handler
    async def get_outstanding_customer_cart(self, uid: str) -> Cart | None:
        """ Retrieves the outstanding customer cart with all linked products. """
        for cart in self.__carts:
            if cart.uid == uid and not cart.converted_to_order:
                return cart
        return None

    @error_handler
    async def add_cart_item(self, cart_item: CartItem) -> CartItem:
        """ Adds an item to the customer's cart. """
        with self.get_session() as session:
            cart_orm = session.query(CartORM).filter_by(cart_id=cart_item.cart_id).first()
            if not cart_orm:
                raise ValueError("Cart not found")
            existing_item = session.query(CartItemORM).filter_by(cart_id=cart_item.cart_id,
                                                                 product_id=cart_item.product_id).first()
            if existing_item:
                existing_item.quantity += cart_item.quantity
            else:
                new_cart_item = CartItemORM(
                    item_id=cart_item.item_id,
                    cart_id=cart_item.cart_id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity
                )
                session.add(new_cart_item)
        await self.preload_carts()  # Update preloaded carts after adding a new item
        return cart_item

    @error_handler
    async def create_new_cart(self, cart: Cart) -> Cart:
        """ Creates a new cart for the customer. """
        with self.get_session() as session:
            new_cart_orm = CartORM(
                cart_id=cart.cart_id,
                uid=cart.uid,
                created_at=cart.created_at,
                converted_to_order=cart.converted_to_order,
                converted_at=cart.converted_at
            )
            for item in cart.items:
                new_cart_item = CartItemORM(
                    item_id=item.item_id,
                    cart_id=item.cart_id,
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                new_cart_orm.items.append(new_cart_item)
            session.add(new_cart_orm)
        await self.preload_carts()  # Update preloaded carts after creating a new cart
        return cart

    @error_handler
    async def remove_cart_item(self, item_id: str) -> bool:
        """ Removes an item from the cart by item ID. """
        with self.get_session() as session:
            cart_item = session.query(CartItemORM).filter_by(item_id=item_id).first()
            if not cart_item:
                raise ValueError("Cart item not found")
            session.delete(cart_item)
        await self.preload_carts()  # Update preloaded carts after removing an item
        return True
