from database.connect import create_connection, close_connection

async def get_order_details(order_id: int):
    conn = await create_connection()
    try:
        query = """
            SELECT o.order_id, o.customer_id, o.basket_id, o.card_number, o.card_holder_name, o.card_expiry_date, o.card_cvv, b.status
            FROM orders o
            JOIN basket b ON o.basket_id = b.basket_id
            WHERE o.order_id = $1
        """
        result = await conn.fetchrow(query, order_id)
        return result
    finally:
        await close_connection(conn)
        
# Получение ID корзины по ID пользователя
async def get_basket_id_by_customer(customer_id: int) -> int:
    conn = await create_connection()
    try:
        query = """
            SELECT basket_id FROM basket WHERE customer_id = $1 AND status = 'open'
        """
        result = await conn.fetchval(query, customer_id)
        return result
    finally:
        await close_connection(conn)

# Создание заказа
async def create_order(
    customer_id: int,
    basket_id: int,
    card_number: str,
    card_holder_name: str,
    card_expiry_date: str,
    card_cvv: str,
) -> int:
    conn = await create_connection()  # Убедитесь, что эта функция возвращает соединение
    try:
        query = """
            INSERT INTO orders (customer_id, basket_id, card_number, card_holder_name, card_expiry_date, card_cvv)
            VALUES ($1, $2, $3, $4, $5, $6)
            
        """
        # Выполняем запрос и получаем ID нового заказа
        conn.execute(query, customer_id, basket_id, card_number, card_holder_name, card_expiry_date, card_cvv)
        # if result:
        #     return result["order_id"]
        # else:
            # raise Exception("Ошибка при создании заказа: результат пустой.")
        return 0
    finally:
        await close_connection(conn)


# Обновление статуса корзины
async def update_basket_status(basket_id: int, status: str):
    conn = await create_connection()
    try:
        query = """
            UPDATE basket SET status = $1 WHERE basket_id = $2
        """
        await conn.execute(query, status, basket_id)
    finally:
        await close_connection(conn)