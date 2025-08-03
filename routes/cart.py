from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.database import get_session
from models.cart import CartItem, CartItemCreate, CartItemRead
from models.products import Product
from models.user import User
from utils.auth_utils import get_current_user


cart_router = APIRouter()

@cart_router.get('/', response_model = List[CartItemRead])
def get_cart_items(session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    cart_items = session.exec(select(CartItem).where(CartItem.user_id == user.id)).all()
    return cart_items

@cart_router.post('/', response_model = CartItemRead)
def post_cart_item(cart_item : CartItemCreate, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    cart_list = session.exec(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == cart_item.id)).first()

    if cart_list:
        cart_list.quantity += cart_item.quantity
        session.commit()
        session.refresh(cart_list)
        return cart_list
    price = session.get(Product, cart_item.id).price #type: ignore
    new_item = CartItem(user_id = user.id, product_id = cart_item.id, quantity = cart_item.quantity, unit_price = price) # type: ignore
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item

@cart_router.delete('/{itemid}', response_model = dict)
def delete_cart_item(item_id : int, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    cart_item = session.get(CartItem, item_id)

    if not cart_item or cart_item.user_id != user.id:
        raise HTTPException(404, 'Item not found')
    session.delete(cart_item)
    session.commit()
    return {
        'message' : 'Item has been deleted'
    }
