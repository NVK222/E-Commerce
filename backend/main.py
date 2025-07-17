from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import create_db
from routes.auth import auth_router
from routes.products import products_router
from routes.cart import cart_router
from routes.orders import orders_router

@asynccontextmanager
async def lifespan(app : FastAPI):
    create_db()
    yield

app = FastAPI(lifespan=lifespan)


app.include_router(auth_router, prefix = '/auth')
app.include_router(products_router, prefix = '/products')
app.include_router(cart_router, prefix = '/cart')
app.include_router(orders_router, prefix = '/order')