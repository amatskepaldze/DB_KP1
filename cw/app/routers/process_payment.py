from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from tokens.current_user import get_current_user
from database.actions_with_orders import create_order, update_basket_status, get_basket_id_by_customer
from database.actions_with_baskets import get_basket_id

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/process_payment',
    tags=['Payment']
)

@router.get("/", response_class=HTMLResponse)
async def payment_page(request: Request):
    user = await get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")
    # Показываем страницу оплаты
    return templates.TemplateResponse("purchase.html", {"request": request})

@router.post("/")
async def process_payment(
    request: Request,
    card_number: str = Form(...),
    card_holder_name: str = Form(...),
    card_expiry_date: str = Form(...),
    card_cvv: str = Form(...),
):
    user = await get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    # Проверяем срок действия карты
    try:
        expiry_date = datetime.strptime(card_expiry_date, "%m/%y")
        if expiry_date < datetime.now():
            raise HTTPException(status_code=400, detail="Срок действия карты истек.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат срока действия карты.")

    # Получаем ID текущей корзины пользователя
    customer_id = user # ID текущего пользователя
    basket_id = await get_basket_id(customer_id)
    if basket_id is None:
        raise HTTPException(status_code=404, detail="Корзина не найдена.")

    # Создаем заказ
    try:
        order_id = await create_order(customer_id, basket_id, card_number, card_holder_name, card_expiry_date, card_cvv)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания заказа: {str(e)}")
    print(customer_id, basket_id, order_id)

    # Обновляем статус корзины
    try:
        await update_basket_status(basket_id, "Оплачено")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления статуса корзины: {str(e)}")

    # Возвращаем успешный ответ
    return JSONResponse(
        content={
            "status": "success",
            "message": "Оплата успешно обработана.",
            "order_id": order_id,
            "order_status": "Оплачен",
            "card_holder_name": card_holder_name,
            "card_expiry_date": card_expiry_date,
            "card_number": card_number[-4:],  # Показываем только последние 4 цифры
        }
    )