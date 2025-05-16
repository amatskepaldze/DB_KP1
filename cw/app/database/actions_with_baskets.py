from database.connect import create_connection, create_slave_connection, close_connection
from datetime import datetime

async def add_to_basket(appliance_id: int, shop_id: int, stock: int, customer_id: int):
    conn = await create_connection()
    try:
        query_check = """
            SELECT basket_id FROM basket WHERE customer_id = $1 AND status = $2
        """
        basket_id = await conn.fetchrow(query_check, customer_id, "open")
        if basket_id is not None:
            query_appliance_check = """
                SELECT appliance_id FROM appliance_pool WHERE appliance_id = $1 AND basket_id = $2
            """
            if await conn.fetchrow(query_appliance_check, appliance_id, basket_id['basket_id']) is not None:
                query_appliance_add = """
                    UPDATE appliance_pool SET quantity = quantity + $1 WHERE appliance_id = $2 AND basket_id = $3
                """
                await conn.execute(query_appliance_add, stock, appliance_id, basket_id['basket_id'])
            else:
                query_new_appliance_add = """
                    INSERT INTO appliance_pool(appliance_id, basket_id, quantity) VALUES ($1, $2,$3)
                """
                await conn.execute(query_new_appliance_add, appliance_id, basket_id['basket_id'], stock)
        else:
            query_new_basket = """
                INSERT INTO basket(customer_id, date, status) VALUES ($1, $2, $3)
            """
            await conn.execute(query_new_basket, customer_id, datetime.now().date(), "open")
            basket_id = await conn.fetchrow(query_check, customer_id, "open")
            query_new_appliance_pool_add = """
                INSERT INTO appliance_pool(appliance_id, basket_id, quantity) VALUES($1, $2, $3)
            """
            await conn.execute(query_new_appliance_pool_add, appliance_id, basket_id['basket_id'], stock)
        query_delete_from_shop = """
            UPDATE stock SET stock = stock - $1 WHERE appliance_id = $2 AND shop_id = $3
        """
        await conn.execute(query_delete_from_shop, stock, appliance_id, shop_id)
        query_stock_check = """
            SELECT stock FROM stock WHERE appliance_id = $1 AND shop_id = $2
        """
        db_stock = await conn.fetchrow(query_stock_check, appliance_id, shop_id)
        if db_stock['stock'] == 0:
            query_stock_delete = """
                DELETE FROM stock WHERE appliance_id = $1 AND shop_id = $2
            """
            await conn.execute(query_stock_delete, appliance_id, shop_id)
    finally:
        await close_connection(conn)

async def get_all_information_about_basket(basket_id: int):
    conn = await create_slave_connection()
    try:
        query = """
            SELECT basket_id, appliance_id, appliance_name, brand_id, brand_name, price, quantity
            FROM appliance_in_basket
            WHERE basket_id = $1
        """
        basket = await conn.fetch(query, basket_id)
        result = [tuple(product) for product in basket]
        return result
    finally:
        await close_connection(conn)

async def get_basket_id(customer_id: int):
    conn = await create_slave_connection()
    try:
        query = """
            SELECT basket_id FROM basket WHERE customer_id = $1 AND status = $2
        """
        basket_id = await conn.fetchrow(query, customer_id, "open")
        if basket_id is None:
            return basket_id
        return basket_id['basket_id']
    finally:
        await close_connection(conn)

async def make_order(basket_id: int):
    conn = await create_connection()
    try:
        query = """
            UPDATE basket SET status = $1 WHERE basket_id = $2
        """
        await conn.execute(query, "close", basket_id)
    finally:
        await close_connection(conn)

# использование функции SQL
async def get_basket_price(basket_id: int):
    conn = await create_slave_connection()
    try:
        query = """
            SELECT get_basket_price($1)
        """
        price = await conn.fetchrow(query, basket_id)
        return price['get_basket_price']
    finally:
        await close_connection(conn)