from datetime import datetime,timezone
from decimal import Decimal
from typing import List
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlmodel import Field, SQLModel


class Order(SQLModel, table = True):
    id : int | None = Field(default = None, primary_key = True)
    user_id : int = Field(foreign_key = 'user.id')
    created_at : datetime = Field(default = datetime.now(timezone.utc))
    total_price : Decimal = Field(sa_column = Column(Numeric(10,2)))

class OrderItem(SQLModel, table = True):
    id : int | None = Field(default = None, primary_key = True)
    order_id : int = Field(sa_column=Column(
            Integer,
            ForeignKey("order.id", ondelete="CASCADE"),
            nullable=False
        ))
    product_id : int = Field(foreign_key = 'product.id')
    quantity : int = Field(default = 1)

class OrderCreate(BaseModel):
    pass

class OrderItemRead(BaseModel):
    id : int
    order_id : int
    product_id : int
    quantity : int

class OrderRead(BaseModel):
    id : int
    user_id : int
    created_at : datetime
    total_price : Decimal