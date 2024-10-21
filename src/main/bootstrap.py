
def bootstrap():
    """

    :return:
    """
    from src.database.sql.user import UserORM
    from src.database.sql.products import ProductsORM, CategoryORM, InventoryORM
    from src.database.sql.customer import CustomerORM, OrderORM, PaymentORM, OrderItemsORM
    from src.database.sql.cart import CartORM, CartItemORM
    from src.database.sql.profile import ProfileORM
    orm_models = [UserORM,ProfileORM, CategoryORM, ProductsORM, InventoryORM, CustomerORM, OrderORM, PaymentORM,
                  OrderItemsORM,CartORM, CartItemORM]

    for model in orm_models:
        model.create_if_not_table()
