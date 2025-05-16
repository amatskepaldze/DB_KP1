from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from schemas.customer import Customer
from database.actions_with_customers import get_customer, create_customer, get_customer_id
from tokens.current_user import get_current_user
from tokens.token_creation import create_access_token


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='',
    tags=['Registration']
)

@router.get("/register")
async def return_registration_html(request: Request):
    if await get_current_user(request) is None:
        return templates.TemplateResponse("register.html", {"request": request})
    return RedirectResponse(url='/home', status_code=302)

@router.post("/register")
async def register(request: Request,
    customer: Customer = Form()):
    existing_customer = await get_customer(customer.customer_login)
    if existing_customer:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже зарегестрирован!")
    try:
        await create_customer(customer)
    except:
        raise HTTPException(status_code=400, detail="Пароль или логин слишком короткий!")
    customer_id = await get_customer_id(customer.customer_login)
    access_token = await create_access_token(customer.customer_login, customer_id['customer_id'])
    response = RedirectResponse(url='/home', status_code=302)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response
    

