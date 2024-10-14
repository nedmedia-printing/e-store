


def bootstrap():
    """

    :return:
    """
    from src.database.sql.user import UserORM
    from src.database.sql.products import ProductsORM, CategoryORM, InventoryORM
    from src.database.sql.customer import CustomerORM, OrderORM, PaymentORM
    orm_models = [UserORM, CategoryORM, ProductsORM, InventoryORM, CustomerORM, OrderORM, PaymentORM]

    for model in orm_models:
        model.create_if_not_table()
