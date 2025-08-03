from decimal import Decimal
from pydantic import BaseModel
from sqlalchemy import Column, Numeric
from sqlmodel import Field, SQLModel


class Product(SQLModel, table = True):
    id : int | None = Field(None, primary_key = True)
    name : str = Field(max_length = 32)
    description : str = Field(max_length = 256)
    price : Decimal = Field(sa_column=Column(Numeric(8, 2)))

class ProductCreate(BaseModel):
    name : str
    description : str
    price : Decimal

class ProductRead(BaseModel):
    id : int
    name : str
    description : str
    price : Decimal