from database.connect import create_connection, create_slave_connection, close_connection
from schemas.appliance import Appliance
import asyncio

async def get_all_products():
    conn = await create_slave_connection()
    try:
        # Достаем данные из вьюшки
        query = """
            SELECT appliance_id, appliance_name, brand_name, category_name, price, stock, shop_id, address
            FROM appliance_with_shop
        """
        products = await conn.fetch(query)
        result = [tuple(product) for product in products]
        return result
    finally:
        await close_connection(conn)

async def appliance_unique_checking(appliance: Appliance):
    conn = await create_slave_connection()
    try:
        brand_query = """
            SELECT brand_id FROM brand WHERE name = $1
        """
        brand_id = await conn.fetchrow(brand_query, appliance.brand)
        category_query = """
            SELECT category_id FROM category WHERE name = $1
        """
        category_id = await conn.fetchrow(category_query, appliance.category)
        query = """
            SELECT appliance_id FROM appliance WHERE name = $1 AND brand_id = $2 AND category_id = $3 AND price = $4
        """
        result = await conn.fetchrow(query, appliance.name, brand_id['brand_id'], category_id['category_id'], appliance.price)
        if result is not None:
            return False
        return True
    finally:
        await close_connection(conn)

async def appliance_in_shop_unique_checking(appliance: Appliance) -> bool:
    conn = await create_slave_connection()
    try:
        query = """
            SELECT appliance_id FROM appliance_with_shop WHERE appliance_name = $1 AND brand_name = $2 AND address = $3 AND category_name = $4 AND price = $5
        """
        result = await conn.fetchrow(query, appliance.name, appliance.brand, appliance.shop, appliance.category, appliance.price)
        if result is not None:
            return False
        return True
    finally:
        await close_connection(conn)

async def add_new_product(appliance: Appliance):
    conn = await create_connection()
    try:
        brand_id_query = """
            SELECT brand_id FROM brand WHERE name = $1
        """
        brand_id = await conn.fetchrow(brand_id_query, appliance.brand)
        category_id_query = """
            SELECT category_id FROM category WHERE name = $1
        """
        category_id = await conn.fetchrow(category_id_query, appliance.category)
        # Проверяем на уникальность в таблице техники по бренду и наименованию
        if await appliance_unique_checking(appliance):
            appliance_query = """
                INSERT INTO appliance (name, brand_id, category_id, price, description) VALUES ($1, $2, $3, $4, $5)
            """
            await conn.execute(appliance_query, appliance.name, brand_id['brand_id'], category_id['category_id'], appliance.price, appliance.description)
        shop_id_query = """
            SELECT shop_id FROM shop WHERE address = $1
        """
        shop_id = await conn.fetchrow(shop_id_query, appliance.shop)
        appliance_id_query = """
            SELECT appliance_id FROM appliance WHERE name = $1 AND brand_id = $2
        """
        appliance_id = await conn.fetchrow(appliance_id_query, appliance.name, brand_id['brand_id'])
        if await appliance_in_shop_unique_checking(appliance):
            query = """
                INSERT INTO stock (appliance_id, shop_id, stock) VALUES ($1, $2, $3)
            """
            await conn.execute(query, appliance_id['appliance_id'], shop_id['shop_id'], appliance.stock)
        else:
            query = """
                UPDATE stock SET stock = stock + $1 WHERE appliance_id = $2 AND shop_id = $3
            """
            await conn.execute(query, appliance.stock, appliance_id['appliance_id'], shop_id['shop_id'])
    finally:
        await close_connection(conn)

async def rmv_appliance(appliance_id: int, shop_id: int):
    conn = await create_connection()
    try:
        query_stock = """
            DELETE FROM stock WHERE appliance_id = $1 AND shop_id = $2
        """
        await conn.execute(query_stock, appliance_id, shop_id)
    finally:
        await close_connection(conn)

async def get_all_information_about_product(appliance_id: int, shop_id: int):
    conn = await create_slave_connection()
    try:
        query = """
            SELECT appliance_id, appliance_name, brand_name, category_name, price, stock, shop_id, address, appliance_description, brand_description, category_description
            FROM appliance_with_shop
            WHERE appliance_id = $1 AND shop_id = $2
        """
        product = await conn.fetchrow(query, appliance_id, shop_id)
        if product is not None:
            return tuple(product)
        return product
    finally:
        await close_connection(conn)



# asyncio.run(get_all_products())