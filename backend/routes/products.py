from decimal import Decimal
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, asc, desc, select
from db.database import get_session
from models.filter import FilterParamsProduct
from models.products import Product, ProductCreate, ProductRead
from models.user import User
from utils.auth_utils import get_current_user


products_router = APIRouter()

@products_router.get('/', response_model = List[ProductRead])
def get_products(filter_params : FilterParamsProduct = Depends(),
                 session : Session = Depends(get_session)
                 ):
    query = select(Product)
    if filter_params.name:
        query = query.where(func.lower(Product.name).like(f'%{filter_params.name}%'))
    if filter_params.min_price is not None:
        query = query.where(Product.price >= filter_params.min_price)
    if filter_params.max_price is not None:
        query = query.where(Product.price <= filter_params.max_price)
    
    to_sort = getattr(Product, filter_params.sort_by)
    order_values = {
        'asc' : asc,
        'desc' : desc
    }
    to_order = order_values.get(filter_params.order, asc)
    query = query.order_by(to_order(to_sort))

    query = query.offset(filter_params.offset).limit(filter_params.limit)

    return session.exec(query).all()


@products_router.post('/', response_model = ProductRead)
def admin_create_product(product : ProductCreate,
                         session : Session = Depends(get_session),
                         user : User = Depends(get_current_user)
                         ):
    if not user.isadmin:
        raise HTTPException(400, 'No permission')
    db_product = Product(**product.model_dump())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@products_router.put('/{id}', response_model = ProductRead)
def admin_update_product(id : int, name : str | None = None, description : str | None = None, price : Decimal | None = None, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    if not user.isadmin:
        raise HTTPException(400, 'No Permission')
    product = session.get(Product, id)
    if not product:
        raise HTTPException(404, 'No product with id found')
    if name:
        product.name = name
    if description:
        product.description = description
    if price:
        product.price = price
    session.commit()
    session.refresh(product)
    return product

@products_router.delete('/{id}', response_model = dict)
def admin_delete_product(id : int, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    if not user.isadmin:
        raise HTTPException(400, 'No permission')
    product = session.get(Product, id)
    if not product:
        raise HTTPException(404, 'No product with id found')
    session.delete(product)
    session.commit()
    return {
        'message' : 'Product successfully deleted'
    }
