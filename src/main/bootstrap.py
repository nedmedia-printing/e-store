


def bootstrap():
    """

    :return:
    """
    from src.database.sql.user import UserORM
    from src.database.sql.products import ProductsORM, CategoryORM, InventoryORM
    orm_models = [UserORM, CategoryORM, ProductsORM, InventoryORM]

    for model in orm_models:
        model.create_if_not_table()
