from datetime import datetime
from pydantic import BaseModel, Field, PositiveInt

from src.database.models.products import Products
from src.utils import south_african_standard_time, create_id


class Cart(BaseModel):
    uid: str
    cart_id: str = Field(default_factory=create_id)
    created_at: datetime = Field(default_factory=south_african_standard_time)
    converted_to_order: bool = Field(default=False)
    converted_at: datetime | None = Field(default=None)
    items: list['CartItem'] = Field(default_factory=list)

    @property
    def total_items(self) -> int:
        """Calculate total number of items in the cart."""
        return sum(item.quantity for item in self.items)

    @property
    def total_price(self) -> int:
        """Calculate total price for all items in the cart."""
        return sum(item.line_price for item in self.items)

    def add_item(self, product_id: str, quantity: int = 1):
        """Add an item to the cart."""
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return
        # If item is not found, add a new item
        new_item = CartItem(product_id=product_id, cart_id=self.cart_id, quantity=quantity)
        self.items.append(new_item)
        return new_item

    def remove_item(self, product_id: str):
        """Remove an item from the cart."""
        self.items = [item for item in self.items if item.product_id != product_id]

    def clear_cart(self):
        """Clear all items from the cart."""
        self.items.clear()

    def cart_summary(self):
        """
        Summarizes the cart details for easy checkout handling.
        :return: dict containing cart summary.
        """
        return {
            "uid": self.uid,
            "cart_id": self.cart_id,
            "created_at": self.created_at.isoformat(),
            "converted_to_order": self.converted_to_order,
            "converted_at": self.converted_at.isoformat() if self.converted_at else None,
            "total_items": self.total_items,
            "total_price": self.total_price,
            "items": [item.item_summary() for item in self.items]
        }


class CartItem(BaseModel):
    item_id: str = Field(default_factory=create_id)
    cart_id: str
    product_id: str
    quantity: PositiveInt = Field(default=1)  # Default quantity is 1
    cart: Cart
    product: Products

    @property
    def item_price(self) -> int:
        return self.product.sell_price

    @property
    def line_price(self) -> int:
        """Calculate total price for this cart item."""
        return self.item_price * self.quantity

    @property
    def name(self) -> str:
        """

        :return:
        """
        return self.product.name

    @property
    def description(self):
        """description for product items"""
        return self.product.description

    @property
    def inventory_count(self) -> int:
        return self.product.inventory_count

    def item_summary(self):
        return {
            "item_id": self.item_id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "item_price": self.item_price,
            "line_price": self.line_price,
            "name": self.name,
            "description": self.description,
            "inventory_count": self.inventory_count}
