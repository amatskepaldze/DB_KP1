from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from tokens.current_user import get_current_user
from database.actions_with_products import get_all_products, add_new_product, rmv_appliance
from database.actions_with_customers import validate_admin, get_all_customers, manage_admin
from database.actions_with_brands import get_all_brands, add_new_brand, brand_unique_checking
from database.actions_with_categories import get_all_categories, add_new_category, category_unique_checking
from database.actions_with_shops import get_all_shops, add_new_shop, rmv_shop, shop_unique_checking
from database.actions_with_orders import create_order #, update_basket_status
from tokens.current_user import get_current_user
from schemas.appliance import Appliance
from schemas.brand import Brand
from schemas.category import Category
from schemas.shop import Shop
from fastapi.responses import JSONResponse
from datetime import datetime

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/home',
    tags=['Home']
)

@router.get('/')
async def return_home_html(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/login')
    products = await get_all_products()
    shops = await get_all_shops()
    if await validate_admin(user) == user:
        brands = await get_all_brands()
        categories = await get_all_categories()
        users = await get_all_customers("user")
        return templates.TemplateResponse("home_admin.html",
                                        {
                                            "request": request,
                                            "brands": brands,
                                            "categories": categories,
                                            "products": products,
                                            "users": users,
                                            "shops": shops
                                        })
    return templates.TemplateResponse("home.html",
                                    {
                                        "request": request,
                                        "products": products
                                    })

# ADMIN PANEL
# @router.post('/add_appliance')
# async def add_new_appliance_query(request: Request,
#                                 appliance: Appliance = Form()):
#     if (len(appliance.description) == 0):
#         appliance.description = None
#     # Проверка уникальности
#     await add_new_product(appliance)
#     return {"message": "Товар был добавлен успешно!"}

# @router.get("/process_payment", response_class=HTMLResponse)
# async def process_payment_page(request: Request):
#     # Проверяем, авторизован ли пользователь
#     user = await get_current_user(request)
#     if user is None:
#         raise HTTPException(status_code=401, detail="Пользователь не авторизован")

#     # Здесь можно добавить логику для обработки оплаты
#     return templates.TemplateResponse("process_payment.html", {"request": request})
@router.get("/process_payment")
async def payment_page(request: Request):
    return templates.TemplateResponse("purchase.html", {"request": request})

@router.post("/process_payment")
async def process_payment(
    request: Request,
    card_number: str = Form(...),
    card_holder_name: str = Form(...),
    card_expiry_date: str = Form(...),
    card_cvv: str = Form(...),
):
    # Проверяем срок действия карты
    try:
        expiry_date = datetime.strptime(card_expiry_date, "%m/%y")
        if expiry_date < datetime.now():
            raise HTTPException(status_code=400, detail="Срок действия карты истек.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат срока действия карты.")

    # Получаем данные клиента и корзины
    customer_id = 1  # Замените на текущего пользователя (пример)
    basket_id = 1    # Замените на текущую корзину (пример)

    # Создаем заказ
    try:
        order_id = await create_order(customer_id, basket_id, card_number, card_holder_name, card_expiry_date, card_cvv)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания заказа: {str(e)}")

    # Возвращаем успешный ответ
    return JSONResponse(
        content={
            "status": "success",
            "message": "Оплата успешно обработана.",
            "order_id": order_id,
            "order_status": "Оплачен",
            "card_holder_name": card_holder_name,
            "card_expiry_date": card_expiry_date,
            "card_number": card_number[-4:],
        }
    )

@router.post('/add_appliance')
async def add_new_appliance_query(request: Request,
                                appliance: Appliance = Form()):
    # Проверяем Content-Type для определения формата данных
    content_type = request.headers.get("Content-Type", "")
    if "application/json" in content_type:
        body = await request.json()
        appliance = Appliance(**body)
        # elif "multipart/form-data" in content_type:
    else:
        form = await request.form()
        form_data = {key: form[key] for key in form}
        appliance = Appliance(**form_data)
    # except:
    #     raise HTTPException(status_code=400, detail="Неподдерживаемый тип данных. Используйте JSON или form-data.")

    
    # Обработка описания, если оно пустое
    if appliance.description and len(appliance.description) == 0:
        appliance.description = None

    # Проверка уникальности и добавление товара
    await add_new_product(appliance)
    return {"message": "Товар был добавлен успешно!"}
@router.post('/rmv_appliance')
async def rmv_appliance_query(request: Request,
                              appliance_id: int = Form(),
                              shop_id: int = Form()):
    await rmv_appliance(appliance_id, shop_id)
    return {"message": "Товар был удален успешно!"}

@router.post('/add_shop')
async def add_new_shop_query(request: Request,
                             shop: Shop = Form()):
    if not await shop_unique_checking(shop):
        return {"status": "FAIL", "message": "Такой магазин уже есть!"}
    else:
        await add_new_shop(shop)
        return {"status": "OK", "message": "Магазин был добавлен успешно!"}

@router.post('/rmv_shop')
async def rmv_shop_query(request: Request,
                         shop_id: int = Form()):
    await rmv_shop(shop_id)
    return {"message": "Магазин был удален успешно!"}

@router.post('/add_brand')
async def add_new_brand_query(request: Request,
                            brand: Brand = Form()):
    if (len(brand.description) == 0):
        brand.description = None
    if not await brand_unique_checking(brand):
        return {"status": "FAIL", "message": "Такой бренд уже есть!"}
    else:
        await add_new_brand(brand)
        return {"status": "OK", "message": "Бренд был добавлен успешно!"}

@router.post('/add_category')
async def add_new_category_query(request: Request,
                                category: Category = Form()):
    if (len(category.description) == 0):
        category.description = None
    if not await category_unique_checking(category):
        return {"status": "FAIL", "message": "Такая категория уже есть!"}
    else:
        await add_new_category(category)
        return {"status": "OK", "message": "Категория была добавлена успешно!"}

@router.post('/add_admin')
async def add_new_admin_query(request: Request,
                              username: str = Form()):
    await manage_admin(username)
    return {"message": "Новый администратор назначен успешно!"}

