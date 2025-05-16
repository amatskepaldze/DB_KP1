from database.connect import create_connection, create_slave_connection, close_connection
from schemas.brand import Brand
import asyncio

async def get_all_brands():
    conn = await create_slave_connection()
    try:
        query = """
            SELECT name FROM brand
        """
        brands = await conn.fetch(query)
        result = [brand['name'] for brand in brands]
        return result
    finally:
        await close_connection(conn)

async def add_new_brand(brand: Brand):
    conn = await create_connection()
    try:
        query = """
            INSERT INTO brand (name, description) VALUES ($1, $2)
        """
        await conn.execute(query, brand.name, brand.description)
    finally:
        await close_connection(conn)

async def brand_unique_checking(brand: Brand) -> bool:
    conn = await create_slave_connection()
    try:
        query = """
            SELECT brand_id FROM brand WHERE name = $1
        """
        result = await conn.fetchrow(query, brand.name)
        if result is not None:
            return False
        return True
    finally:
        await close_connection(conn)

# asyncio.run(get_all_brands())