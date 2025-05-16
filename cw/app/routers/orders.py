from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from tokens.current_user import get_current_user
from database.actions_with_orders import get_order_details


router = APIRouter(
    prefix='/orders',
    tags=['Orders']
)

templates = Jinja2Templates(directory="templates")

@router.get('/{order_id}')
async def get_order_html(request: Request, order_id: int):
    user = await get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")
    
    # Получаем информацию о заказе
    order_details = await get_order_details(order_id)
    if order_details is None:
        # Если заказ не найден, возвращаем сообщение об ошибке на той же странице
        return templates.TemplateResponse("purchase.html", {
            "request": request,
            "error_message": "Заказ не найден."
        })
    
    # Если заказ найден, перенаправляем на главную страницу
    return RedirectResponse(url="/", status_code=303)