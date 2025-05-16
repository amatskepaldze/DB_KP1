from database.connect import create_connection, create_slave_connection, close_connection
from schemas.category import Category
import asyncio

async def get_all_categories():
    conn = await create_slave_connection()
    try:
        query = """
            SELECT name FROM category
        """
        categories = await conn.fetch(query)
        result = [category['name'] for category in categories]
        return result
    finally:
        await close_connection(conn)

async def add_new_category(category: Category):
    conn = await create_connection()
    try:
        query = """
            INSERT INTO category (name, description) VALUES ($1, $2)
        """
        await conn.execute(query, category.name, category.description)
    finally:
        await close_connection(conn)

async def category_unique_checking(category: Category) -> bool:
    conn = await create_slave_connection()
    try:
        query = """
            SELECT category_id FROM category WHERE name = $1
        """
        result = await conn.fetchrow(query, category.name)
        if result is not None:
            return False
        return True
    finally:
        await close_connection(conn)

# asyncio.run(get_all_categories())