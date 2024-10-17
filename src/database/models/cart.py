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
    items: list[CartItem] = Field(default_factory=list)

    @property
    def total_items(self) -> int:
        """Calculate total number of items in the cart."""
        return sum(item.quantity for item in self.items)

    @property
    def total_price(self) -> float:
        """Calculate total price for all items in the cart."""
        return sum(item.total_price for item in self.items)

    def add_item(self, product_id: str, name: str, price: float, quantity: int = 1):
        """Add an item to the cart."""
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return
        # If item is not found, add a new item
        new_item = CartItem(product_id=product_id, name=name, price=price, quantity=quantity)
        self.items.append(new_item)

    def remove_item(self, product_id: str):
        """Remove an item from the cart."""
        self.items = [item for item in self.items if item.product_id != product_id]

    def clear_cart(self):
        """Clear all items from the cart."""
        self.items.clear()


class CartItem(BaseModel):
    item_id: str = Field(default_factory=create_id)
    cart_id: str
    product_id: str
    quantity: PositiveInt = Field(default=1)  # Default quantity is 1
    cart: Cart
    product: Products

    @property
    def total_price(self) -> float:
        """Calculate total price for this cart item."""
        return self.price * self.quantity
