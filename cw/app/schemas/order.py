from pydantic import BaseModel

class PaymentData(BaseModel):
    customer_id: int
    basket_id: int
    card_number: str
    card_holder_name: str
    card_expiry_date: str  # Формат MM/YY
    card_cvv: str
