from decimal import Decimal
from functools import total_ordering
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.database import get_session
from models.cart import CartItem
from models.order import Order, OrderItem, OrderRead
from models.user import User
from utils.auth_utils import get_current_user

orders_router = APIRouter()

@orders_router.get('/', response_model = List[OrderRead])
def get_orders(session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    orders = session.exec(select(Order).where(Order.user_id == user.id)).all()
    return [OrderRead.model_validate(order.model_dump) for order in orders]

@orders_router.post('/', response_model = List[OrderRead])
def post_order(session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    if not user:
        raise HTTPException(404, 'Invalid credentials')
    cart = session.exec(select(CartItem).where(CartItem.user_id == user.id)).all()
    if not cart:
        raise HTTPException(404, 'Cart is empty')
    total_price = Decimal(0)
    for item in cart:
        total_price += item.unit_price * item.quantity
    order = Order(user_id = user.id, total_price = total_price) #type: ignore
    session.add(order)
    session.commit()
    session.refresh(order)

    for item in cart:
        order_item = OrderItem(order_id = order.id, product_id = item.product_id, quantity = item.quantity) #type: ignore
        session.add(order_item)
    
    for item in cart:
        session.delete(item)
    
    session.commit()
    return order

@orders_router.get('/{id}', response_model = dict)
def get_order_by_id(id : int, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    order = session.exec(select(Order).where(Order.id == id, Order.user_id == user.id)).first()
    items = session.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all() # type: ignore
    return {
        'order' : order,
        'items' : items
    }

@orders_router.get('/{id}', response_model = List[OrderRead])
def admin_get_orders(id : int, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    if not user.isadmin:
        raise HTTPException(400, 'No permission')
    user_ = session.get(User, id)
    if not user_:
        raise HTTPException(404, 'No such user found')
    orders = session.exec(select(Order).where(Order.user_id == user_.id)).all()
    return [OrderRead.model_validate(order.model_dump) for order in orders]
