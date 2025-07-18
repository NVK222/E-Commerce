from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

class FilterParamsBase(BaseModel):
    offset : int = Field(0, ge = 0)
    limit : int = Field(10, ge = 1, le = 25)
    order : Literal['asc', 'desc'] = Field('asc', description = 'Order by (asc, desc)')

class FilterParamsProduct(FilterParamsBase):
    name : str | None = Field(None, description = 'Name to filter by (case - insensitive)')
    min_price : Decimal | None = Field(None, ge = 0, description = 'Filter by minimum price')
    max_price : Decimal | None = Field(None, ge = 0, description = 'Filter by maximum price')
    sort_by : Literal['username', 'price'] = Field('username', description = 'Sort by (name, price)')

class FilterParamsUser(FilterParamsBase):
    name : str | None = Field(None, description = 'Name to filter by (case - insensitive)')
    sort_by : Literal['id', 'name', 'email', 'isadmin'] = Field('id', description = 'Sort by (id, name, email, isadmin)')