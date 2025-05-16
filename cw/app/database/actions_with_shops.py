from database.connect import create_connection, create_slave_connection, close_connection
from schemas.shop import Shop

async def get_all_shops():
    conn = await create_slave_connection()
    try:
        query = """
            SELECT shop_id, address from shop
        """
        shops = await conn.fetch(query)
        result = [tuple(shop) for shop in shops]
        return result
    finally:
        await close_connection(conn)

async def add_new_shop(shop: Shop):
    conn = await create_connection()
    try:
        query = """
            INSERT INTO shop(address) VALUES ($1)
        """
        await conn.execute(query, shop.address)
    finally:
        await close_connection(conn)

async def rmv_shop(shop_id: int):
    conn = await create_connection()
    try:
        query_stock = """
            DELETE FROM stock WHERE shop_id = $1
        """
        await conn.execute(query_stock, shop_id)
        query = """
            DELETE FROM shop WHERE shop_id = $1
        """
        await conn.execute(query, shop_id)
    finally:
        await close_connection(conn)

async def shop_unique_checking(shop: Shop) -> bool:
    conn = await create_slave_connection()
    try:
        query = """
            SELECT shop_id FROM shop WHERE address = $1
        """
        result = await conn.fetchrow(query, shop.address)
        if result is not None:
            return False
        return True
    finally:
        await close_connection(conn)