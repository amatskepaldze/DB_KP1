from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from tokens.current_user import get_current_user
from database.actions_with_baskets import get_all_information_about_basket, get_basket_id, make_order, get_basket_price

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/basket',
    tags=['Basket']
)

@router.get('/')
async def get_basket_html(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/login')
    basket_id = await get_basket_id(user)
    if basket_id is not None:
        basket = await get_all_information_about_basket(basket_id)
        total = await get_basket_price(basket_id)
    else:
        basket = None
        total = None
    return templates.TemplateResponse("basket.html", {
                                    "request": request,
                                    "basket": basket,
                                    "basket_id": basket_id,
                                    "total": total
    })

# @router.post('/make_order')
# async def make_order_query(request: Request,
#                            basket_id: int = Form()):
#     await make_order(basket_id)
#     return {"message": "Заказ был сделан успешно!"}

@router.post('/make_order')
async def make_order_query(request: Request, basket_id: int = Form()):
    await make_order(basket_id)
    return RedirectResponse(url=f'/orders/{basket_id}', status_code=303)