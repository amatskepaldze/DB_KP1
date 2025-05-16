import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from routers import registration, login, home, products, basket, orders, process_payment

app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

templates = Jinja2Templates(directory="/app/templates")

app.include_router(registration.router)
app.include_router(login.router)
app.include_router(home.router)
app.include_router(products.router)
app.include_router(basket.router)
app.include_router(orders.router)
app.include_router(process_payment.router)


@app.get("/")
async def main(request: Request):
    return RedirectResponse(url='/login')
