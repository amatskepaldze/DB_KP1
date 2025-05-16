from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from tokens.current_user import get_current_user
from database.actions_with_products import get_all_information_about_product
from database.actions_with_baskets import add_to_basket

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

@router.get("/{appliance_id}&{shop_id}")
async def get_product_html(request: Request, appliance_id: int, shop_id: int):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/login')
    product = await get_all_information_about_product(appliance_id, shop_id)
    if product is None:
        return RedirectResponse(url='/home/')
    return templates.TemplateResponse("product.html", {
                                    "request": request,
                                    "product": product
    })

@router.post("/add_to_basket")
async def add_to_basket_query(request: Request,
                        appliance_id: int = Form(),
                        shop_id: int = Form(),
                        stock: int = Form()):
    user = await get_current_user(request)
    await add_to_basket(appliance_id, shop_id, stock, user)

