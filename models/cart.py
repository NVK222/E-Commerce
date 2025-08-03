from decimal import Decimal
from pydantic import BaseModel
from sqlalchemy import Column, Numeric
from sqlmodel import Field, SQLModel


class CartItem(SQLModel, table = True):
    id : int | None = Field(default = None, primary_key = True)
    user_id : int = Field(foreign_key = 'user.id')
    product_id : int = Field(foreign_key = 'product.id')
    quantity : int = Field(default = 1)
    unit_price : Decimal = Field(sa_column = Column(Numeric(10,2)))

class CartItemCreate(BaseModel):
    id : int
    quantity : int = 1

class CartItemRead(BaseModel):
    id : int
    user_id : int
    product_id : int
    quantity : int
    unit_price : Decimal
