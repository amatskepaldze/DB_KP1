from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from schemas.customer import CustomerSimple
from database.actions_with_customers import authentificate_customer, get_customer_id
from tokens.current_user import get_current_user
from tokens.token_creation import create_access_token

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='',
    tags=['Login']
)

@router.get('/login')
async def return_login_html(request: Request):
    if await get_current_user(request) is None:
        return templates.TemplateResponse("login.html", {"request": request})
    return RedirectResponse(url='/home', status_code=302)

@router.post('/login')
async def login(request: Request,
    customer: CustomerSimple = Form()):
    customer_login = await authentificate_customer(customer)
    if not customer_login:
        raise HTTPException(status_code=400, detail="Неправильный логин или пароль!")
    customer_id = await get_customer_id(customer.customer_login)
    access_token = await create_access_token(customer_login, customer_id['customer_id'])
    response = RedirectResponse(url='/home', status_code=302)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response

@router.post('/logout')
async def logout(request: Request):
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie(key='access_token')
    return response
    