from pydantic import BaseModel

class Customer(BaseModel):
    customer_login: str
    password: str
    email: str

class CustomerSimple(BaseModel):
    customer_login: str
    password: str