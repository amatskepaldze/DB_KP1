from passlib.context import CryptContext
from database.connect import create_connection, create_slave_connection, close_connection
from schemas.customer import Customer, CustomerSimple

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def get_customer(customer_login: str):
    conn = await create_slave_connection()
    try:
        query = """
            SELECT customer_login, password FROM customer WHERE customer_login = $1
        """
        customer = await conn.fetchrow(query, customer_login)
        return customer
    finally:
        await close_connection(conn)

async def create_customer(customer: Customer):
    conn = await create_connection()
    try:
        hashed_password = bcrypt_context.hash(customer.password)
        query = """
            INSERT INTO customer (customer_login, password, email, rights) VALUES ($1, $2, $3, $4)
        """
        await conn.execute(query, customer.customer_login, hashed_password, customer.email, 'user')
    finally:
        await close_connection(conn)

async def authentificate_customer(customer: Customer | CustomerSimple):
    db_customer = await get_customer(customer.customer_login)
    if not db_customer or not bcrypt_context.verify(customer.password, db_customer['password']):
        return None
    return db_customer['customer_login']

async def get_customer_id(customer_login: str):
    conn = await create_slave_connection()
    try:
        customer = await conn.fetchrow('SELECT customer_id FROM customer WHERE customer_login = $1', customer_login)
        return customer
    finally:
        await close_connection(conn)

async def validate_admin(customer_id: int):
    conn = await create_slave_connection()
    try:
        customer = await conn.fetchrow('SELECT customer_id FROM customer WHERE customer_id = $1 AND rights = $2', customer_id, "admin")
        if customer is None:
            return None
        return customer['customer_id']
    finally:
        await close_connection(conn)

async def get_all_customers(role: str):
    conn = await create_slave_connection()
    try:
        query = """
            SELECT customer_login FROM customer WHERE rights = $1
        """
        customers = await conn.fetch(query, role)
        result = [customer['customer_login'] for customer in customers]
        return result
    finally:
        await close_connection(conn)

async def manage_admin(customer_login: str):
    conn = await create_connection()
    try:
        query = """
            UPDATE customer SET rights = $1 WHERE customer_login = $2
        """
        await conn.execute(query, "admin", customer_login)
    finally:
        await close_connection(conn)